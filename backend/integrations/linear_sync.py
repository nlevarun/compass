"""
Linear Bidirectional Sync

Create issues from feedback/clusters and sync status bidirectionally.
Uses Linear's GraphQL API (modern alternative to Jira).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import httpx


class LinearSync:
    """Bidirectional sync with Linear"""

    def __init__(
        self,
        api_key: str,
        db: Session,
        default_team_id: Optional[str] = None
    ):
        """
        Initialize Linear sync.

        Args:
            api_key: Linear API key
            db: Database session
            default_team_id: Default team ID for creating issues
        """
        self.api_key = api_key
        self.db = db
        self.default_team_id = default_team_id
        self.api_url = "https://api.linear.app/graphql"

        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

    async def _graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL request to Linear API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                json={"query": query, "variables": variables or {}},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise Exception(f"Linear API error: {data['errors']}")

            return data.get("data", {})

    async def test_connection(self) -> Dict:
        """
        Test Linear connection and permissions.

        Returns:
            Connection status dictionary
        """
        query = """
        query {
            viewer {
                id
                name
                email
            }
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """

        try:
            data = await self._graphql_request(query)
            viewer = data.get("viewer", {})
            teams = data.get("teams", {}).get("nodes", [])

            return {
                "status": "success",
                "connected": True,
                "user": viewer.get("name"),
                "email": viewer.get("email"),
                "teams": [{"id": t["id"], "name": t["name"], "key": t["key"]} for t in teams]
            }
        except Exception as e:
            return {
                "status": "error",
                "connected": False,
                "error": str(e)
            }

    async def create_issue_from_cluster(
        self,
        cluster_id: int,
        team_id: Optional[str] = None,
        priority: Optional[int] = None,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a Linear issue from a feedback cluster.

        Args:
            cluster_id: Compass cluster ID
            team_id: Linear team ID (uses default if not provided)
            priority: Linear priority (0=none, 1=urgent, 2=high, 3=medium, 4=low)
            labels: List of label names to add

        Returns:
            Result dictionary with issue ID and URL
        """
        from models import Cluster, Feedback, LinearIssue

        # Get cluster data
        cluster = self.db.query(Cluster).filter(Cluster.id == cluster_id).first()
        if not cluster:
            return {"status": "error", "error": f"Cluster {cluster_id} not found"}

        # Check if already linked to Linear
        existing_issue = self.db.query(LinearIssue).filter(
            LinearIssue.cluster_id == cluster_id
        ).first()
        if existing_issue:
            return {
                "status": "warning",
                "message": "Cluster already linked to Linear issue",
                "linear_id": existing_issue.linear_id,
                "linear_url": existing_issue.linear_url
            }

        # Get feedback samples for description
        feedback_list = self.db.query(Feedback).filter(
            Feedback.cluster_id == cluster_id
        ).order_by(Feedback.customer_revenue.desc()).limit(10).all()

        # Build issue description
        description = self._build_issue_description(cluster, feedback_list)

        # Auto-set priority based on cluster priority score
        if priority is None:
            priority = self._map_priority_score_to_linear(cluster.priority_score)

        # Get team ID
        team = team_id or self.default_team_id
        if not team:
            return {"status": "error", "error": "No team ID specified"}

        # Get or create labels
        label_ids = []
        if labels:
            label_ids = await self._get_or_create_labels(team, labels)
        else:
            label_ids = await self._get_or_create_labels(team, ["compass", "customer-feedback"])

        # Create issue mutation
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                    state {
                        name
                    }
                    priority
                }
            }
        }
        """

        variables = {
            "input": {
                "teamId": team,
                "title": cluster.label[:255],
                "description": description,
                "priority": priority,
                "labelIds": label_ids
            }
        }

        try:
            data = await self._graphql_request(mutation, variables)
            result = data.get("issueCreate", {})

            if not result.get("success"):
                return {"status": "error", "error": "Failed to create Linear issue"}

            issue = result.get("issue", {})

            # Store in database
            linear_issue = LinearIssue(
                linear_id=issue["id"],
                linear_identifier=issue["identifier"],
                linear_url=issue["url"],
                cluster_id=cluster_id,
                title=cluster.label,
                description=description,
                status=issue["state"]["name"],
                priority=priority,
                sync_direction="bidirectional",
                last_synced_at=datetime.utcnow()
            )
            self.db.add(linear_issue)
            self.db.commit()

            return {
                "status": "success",
                "linear_id": issue["id"],
                "linear_identifier": issue["identifier"],
                "linear_url": issue["url"]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_issue_from_feedback(
        self,
        feedback_id: int,
        team_id: Optional[str] = None,
        priority: Optional[int] = None
    ) -> Dict:
        """
        Create a Linear issue from a single feedback entry.

        Args:
            feedback_id: Compass feedback ID
            team_id: Linear team ID
            priority: Linear priority

        Returns:
            Result dictionary
        """
        from models import Feedback

        # Get feedback
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return {"status": "error", "error": f"Feedback {feedback_id} not found"}

        # Get team ID
        team = team_id or self.default_team_id
        if not team:
            return {"status": "error", "error": "No team ID specified"}

        # Build issue
        title = feedback.title or feedback.text[:100]
        description = f"""
**Customer:** {feedback.customer_name or 'Unknown'}
**Revenue Impact:** ${feedback.customer_revenue or 0:,.2f}
**Sentiment:** {self._format_sentiment(feedback.sentiment_score)}
**Submitted:** {feedback.submitted_at.strftime('%Y-%m-%d')}

**Feedback:**
{feedback.text}

---
_Imported from Compass_
        """.strip()

        # Get labels
        label_ids = await self._get_or_create_labels(team, ["compass", "customer-feedback"])

        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    url
                }
            }
        }
        """

        variables = {
            "input": {
                "teamId": team,
                "title": title[:255],
                "description": description,
                "priority": priority or 0,
                "labelIds": label_ids
            }
        }

        try:
            data = await self._graphql_request(mutation, variables)
            result = data.get("issueCreate", {})

            if not result.get("success"):
                return {"status": "error", "error": "Failed to create Linear issue"}

            issue = result.get("issue", {})

            # Update feedback with external ID
            external_ids = feedback.external_ids or {}
            external_ids["linear_id"] = issue["id"]
            external_ids["linear_identifier"] = issue["identifier"]
            external_ids["linear_url"] = issue["url"]
            feedback.external_ids = external_ids
            self.db.commit()

            return {
                "status": "success",
                "linear_id": issue["id"],
                "linear_identifier": issue["identifier"],
                "linear_url": issue["url"]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def link_existing_issue(
        self,
        issue_id: str,
        cluster_id: Optional[int] = None,
        roadmap_item_id: Optional[int] = None
    ) -> Dict:
        """
        Link an existing Linear issue to a Compass cluster or roadmap item.

        Args:
            issue_id: Linear issue ID
            cluster_id: Optional cluster ID to link
            roadmap_item_id: Optional roadmap item ID to link

        Returns:
            Result dictionary
        """
        from models import LinearIssue

        if not cluster_id and not roadmap_item_id:
            return {"status": "error", "error": "Must specify cluster_id or roadmap_item_id"}

        # Fetch issue from Linear
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                url
                state {
                    name
                }
                priority
                assignee {
                    name
                }
            }
        }
        """

        try:
            data = await self._graphql_request(query, {"id": issue_id})
            issue = data.get("issue", {})

            if not issue:
                return {"status": "error", "error": f"Linear issue {issue_id} not found"}

            # Store in database
            linear_issue = LinearIssue(
                linear_id=issue["id"],
                linear_identifier=issue["identifier"],
                linear_url=issue["url"],
                cluster_id=cluster_id,
                roadmap_item_id=roadmap_item_id,
                title=issue["title"],
                description=issue.get("description"),
                status=issue["state"]["name"],
                priority=issue.get("priority"),
                assignee=issue["assignee"]["name"] if issue.get("assignee") else None,
                sync_direction="bidirectional",
                last_synced_at=datetime.utcnow()
            )
            self.db.add(linear_issue)
            self.db.commit()

            return {
                "status": "success",
                "linear_id": issue["id"],
                "linear_identifier": issue["identifier"],
                "linear_url": issue["url"]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def sync_issue_status(self, issue_id: str) -> Dict:
        """
        Sync status from Linear to Compass.

        Args:
            issue_id: Linear issue ID

        Returns:
            Sync result dictionary
        """
        from models import LinearIssue, RoadmapItem

        # Get stored issue
        linear_issue = self.db.query(LinearIssue).filter(LinearIssue.linear_id == issue_id).first()
        if not linear_issue:
            return {"status": "error", "error": f"Linear issue {issue_id} not found in Compass"}

        # Fetch latest from Linear
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                state {
                    name
                }
                priority
                assignee {
                    name
                }
            }
        }
        """

        try:
            data = await self._graphql_request(query, {"id": issue_id})
            issue = data.get("issue", {})

            if not issue:
                return {"status": "error", "error": f"Linear issue {issue_id} not found"}

            # Update stored data
            linear_issue.status = issue["state"]["name"]
            linear_issue.priority = issue.get("priority")
            linear_issue.assignee = issue["assignee"]["name"] if issue.get("assignee") else None
            linear_issue.last_synced_at = datetime.utcnow()

            # Map Linear status to Compass roadmap status
            compass_status = self._map_linear_status_to_compass(issue["state"]["name"])

            # Update roadmap item if linked
            if linear_issue.roadmap_item_id:
                roadmap_item = self.db.query(RoadmapItem).filter(
                    RoadmapItem.id == linear_issue.roadmap_item_id
                ).first()
                if roadmap_item:
                    roadmap_item.status = compass_status
                    roadmap_item.updated_at = datetime.utcnow()

            self.db.commit()

            return {
                "status": "success",
                "linear_id": issue_id,
                "linear_status": issue["state"]["name"],
                "compass_status": compass_status
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def sync_all_issues(self) -> Dict:
        """
        Sync all linked Linear issues.

        Returns:
            Summary of sync results
        """
        from models import LinearIssue

        linear_issues = self.db.query(LinearIssue).all()

        synced = 0
        errors = []

        for linear_issue in linear_issues:
            result = await self.sync_issue_status(linear_issue.linear_id)
            if result["status"] == "success":
                synced += 1
            else:
                errors.append({
                    "linear_id": linear_issue.linear_id,
                    "error": result.get("error")
                })

        return {
            "status": "success",
            "total_issues": len(linear_issues),
            "synced": synced,
            "errors": errors
        }

    async def update_issue_priority(self, issue_id: str, new_priority: int) -> Dict:
        """
        Update Linear issue priority based on Compass data.

        Args:
            issue_id: Linear issue ID
            new_priority: New priority (0-4)

        Returns:
            Update result
        """
        mutation = """
        mutation UpdateIssue($id: String!, $priority: Int!) {
            issueUpdate(id: $id, input: { priority: $priority }) {
                success
                issue {
                    id
                    priority
                }
            }
        }
        """

        try:
            data = await self._graphql_request(mutation, {"id": issue_id, "priority": new_priority})
            result = data.get("issueUpdate", {})

            if not result.get("success"):
                return {"status": "error", "error": "Failed to update Linear issue"}

            # Update in database
            from models import LinearIssue
            linear_issue = self.db.query(LinearIssue).filter(LinearIssue.linear_id == issue_id).first()
            if linear_issue:
                linear_issue.priority = new_priority
                linear_issue.last_synced_at = datetime.utcnow()
                self.db.commit()

            return {
                "status": "success",
                "linear_id": issue_id,
                "priority": new_priority
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def add_comment(self, issue_id: str, comment: str) -> Dict:
        """
        Add a comment to a Linear issue.

        Args:
            issue_id: Linear issue ID
            comment: Comment text

        Returns:
            Result dictionary
        """
        mutation = """
        mutation CreateComment($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "issueId": issue_id,
                "body": comment
            }
        }

        try:
            data = await self._graphql_request(mutation, variables)
            result = data.get("commentCreate", {})

            if not result.get("success"):
                return {"status": "error", "error": "Failed to create comment"}

            return {
                "status": "success",
                "linear_id": issue_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # Helper methods

    async def _get_or_create_labels(self, team_id: str, label_names: List[str]) -> List[str]:
        """Get or create labels and return their IDs."""
        # First, get existing labels for the team
        query = """
        query GetTeamLabels($teamId: String!) {
            team(id: $teamId) {
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """

        try:
            data = await self._graphql_request(query, {"teamId": team_id})
            existing_labels = data.get("team", {}).get("labels", {}).get("nodes", [])
            label_map = {label["name"].lower(): label["id"] for label in existing_labels}

            label_ids = []
            for name in label_names:
                if name.lower() in label_map:
                    label_ids.append(label_map[name.lower()])
                else:
                    # Create new label
                    create_mutation = """
                    mutation CreateLabel($input: IssueLabelCreateInput!) {
                        issueLabelCreate(input: $input) {
                            success
                            issueLabel {
                                id
                            }
                        }
                    }
                    """
                    create_vars = {
                        "input": {
                            "teamId": team_id,
                            "name": name
                        }
                    }
                    create_data = await self._graphql_request(create_mutation, create_vars)
                    result = create_data.get("issueLabelCreate", {})
                    if result.get("success"):
                        label_ids.append(result["issueLabel"]["id"])

            return label_ids

        except Exception as e:
            print(f"Error getting/creating labels: {e}")
            return []

    def _build_issue_description(self, cluster, feedback_list: List) -> str:
        """Build Linear issue description from cluster data."""
        description = f"""
**Cluster Summary**
- Request Count: {cluster.size}
- Priority Score: {cluster.priority_score:.2f}
- Total Revenue Impact: ${cluster.total_revenue:,.2f}
- Average Sentiment: {self._format_sentiment(cluster.avg_sentiment)}

**Top Customer Feedback:**
""".strip()

        for idx, fb in enumerate(feedback_list[:5], 1):
            customer_info = f"{fb.customer_name} (${fb.customer_revenue:,.0f})" if fb.customer_name else "Anonymous"
            description += f"\n\n{idx}. **{customer_info}**\n{fb.text[:200]}..."

        description += "\n\n---\n_Generated by Compass - Customer Feedback Intelligence Platform_"

        return description

    def _map_priority_score_to_linear(self, score: float) -> int:
        """Map Compass priority score to Linear priority (0-4)."""
        if score >= 0.8:
            return 1  # Urgent
        elif score >= 0.6:
            return 2  # High
        elif score >= 0.4:
            return 3  # Medium
        else:
            return 4  # Low

    def _map_linear_status_to_compass(self, linear_status: str) -> str:
        """Map Linear status to Compass roadmap status."""
        status_lower = linear_status.lower()

        if any(s in status_lower for s in ["done", "completed", "canceled", "cancelled"]):
            return "shipped"
        elif any(s in status_lower for s in ["in progress", "started"]):
            return "in_progress"
        elif any(s in status_lower for s in ["planned", "backlog"]):
            return "planned"
        else:
            return "proposed"

    def _format_sentiment(self, score: Optional[float]) -> str:
        """Format sentiment score for display."""
        if score is None:
            return "Unknown"
        elif score >= 0.5:
            return f"Positive ({score:.2f})"
        elif score >= -0.5:
            return f"Neutral ({score:.2f})"
        else:
            return f"Negative ({score:.2f})"
