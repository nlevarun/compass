"""
Jira Bidirectional Sync

Create issues from feedback/clusters and sync status bidirectionally.
Uses the Jira REST API (cloud and server compatible).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from jira import JIRA
from jira.exceptions import JIRAError


class JiraSync:
    """Bidirectional sync with Jira"""

    def __init__(
        self,
        jira_url: str,
        username: str,
        api_token: str,
        db: Session,
        default_project: Optional[str] = None,
        default_issue_type: str = "Story"
    ):
        """
        Initialize Jira sync.

        Args:
            jira_url: Jira instance URL (e.g., "https://yourcompany.atlassian.net")
            username: Jira username/email
            api_token: Jira API token (not password!)
            db: Database session
            default_project: Default project key (e.g., "PROJ")
            default_issue_type: Default issue type ("Story", "Bug", "Task", etc.)
        """
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.db = db
        self.default_project = default_project
        self.default_issue_type = default_issue_type

        # Initialize Jira client
        self.jira = JIRA(
            server=jira_url,
            basic_auth=(username, api_token)
        )

    def test_connection(self) -> Dict:
        """
        Test Jira connection and permissions.

        Returns:
            Connection status dictionary
        """
        try:
            # Try to get current user
            user = self.jira.myself()

            # Get accessible projects
            projects = self.jira.projects()
            project_keys = [p.key for p in projects]

            return {
                "status": "success",
                "connected": True,
                "user": user["displayName"],
                "email": user.get("emailAddress"),
                "projects": project_keys
            }
        except JIRAError as e:
            return {
                "status": "error",
                "connected": False,
                "error": str(e)
            }

    def create_issue_from_cluster(
        self,
        cluster_id: int,
        project_key: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Create a Jira issue from a feedback cluster.

        Args:
            cluster_id: Compass cluster ID
            project_key: Jira project key (uses default if not provided)
            issue_type: Issue type (uses default if not provided)
            priority: Jira priority ("Highest", "High", "Medium", "Low", "Lowest")
            labels: List of labels to add
            custom_fields: Additional custom fields

        Returns:
            Result dictionary with issue key and URL
        """
        from models import Cluster, Feedback, JiraIssue

        # Get cluster data
        cluster = self.db.query(Cluster).filter(Cluster.id == cluster_id).first()
        if not cluster:
            return {"status": "error", "error": f"Cluster {cluster_id} not found"}

        # Check if already linked to Jira
        existing_issue = self.db.query(JiraIssue).filter(
            JiraIssue.cluster_id == cluster_id
        ).first()
        if existing_issue:
            return {
                "status": "warning",
                "message": "Cluster already linked to Jira issue",
                "jira_key": existing_issue.jira_key,
                "jira_url": existing_issue.jira_url
            }

        # Get feedback samples for description
        feedback_list = self.db.query(Feedback).filter(
            Feedback.cluster_id == cluster_id
        ).order_by(Feedback.customer_revenue.desc()).limit(10).all()

        # Build issue description
        description = self._build_issue_description(cluster, feedback_list)

        # Auto-set priority based on cluster priority score
        if priority is None:
            priority = self._map_priority_score_to_jira(cluster.priority_score)

        # Build issue data
        project = project_key or self.default_project
        if not project:
            return {"status": "error", "error": "No project key specified"}

        issue_dict = {
            "project": {"key": project},
            "summary": cluster.label[:255],  # Jira has 255 char limit
            "description": description,
            "issuetype": {"name": issue_type or self.default_issue_type},
        }

        # Add optional fields
        if priority:
            issue_dict["priority"] = {"name": priority}

        if labels:
            issue_dict["labels"] = labels
        else:
            issue_dict["labels"] = ["compass", "customer-feedback"]

        # Add custom fields if provided
        if custom_fields:
            issue_dict.update(custom_fields)

        try:
            # Create issue in Jira
            new_issue = self.jira.create_issue(fields=issue_dict)

            # Add comment with detailed feedback
            self._add_feedback_comment(new_issue.key, feedback_list)

            # Store in database
            jira_issue = JiraIssue(
                jira_key=new_issue.key,
                jira_id=str(new_issue.id),
                jira_url=f"{self.jira_url}/browse/{new_issue.key}",
                cluster_id=cluster_id,
                title=cluster.label,
                description=description,
                status=str(new_issue.fields.status),
                priority=priority,
                issue_type=issue_type or self.default_issue_type,
                sync_direction="bidirectional",
                last_synced_at=datetime.utcnow()
            )
            self.db.add(jira_issue)
            self.db.commit()

            return {
                "status": "success",
                "jira_key": new_issue.key,
                "jira_id": str(new_issue.id),
                "jira_url": f"{self.jira_url}/browse/{new_issue.key}"
            }

        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def create_issue_from_feedback(
        self,
        feedback_id: int,
        project_key: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict:
        """
        Create a Jira issue from a single feedback entry.

        Args:
            feedback_id: Compass feedback ID
            project_key: Jira project key
            issue_type: Issue type
            priority: Jira priority

        Returns:
            Result dictionary
        """
        from models import Feedback

        # Get feedback
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return {"status": "error", "error": f"Feedback {feedback_id} not found"}

        # Build issue
        project = project_key or self.default_project
        if not project:
            return {"status": "error", "error": "No project key specified"}

        summary = feedback.title or feedback.text[:100]
        description = f"""
*Customer:* {feedback.customer_name or 'Unknown'}
*Revenue Impact:* ${feedback.customer_revenue or 0:,.2f}
*Sentiment:* {self._format_sentiment(feedback.sentiment_score)}
*Submitted:* {feedback.submitted_at.strftime('%Y-%m-%d')}

*Feedback:*
{feedback.text}

---
_Imported from Compass_
        """.strip()

        issue_dict = {
            "project": {"key": project},
            "summary": summary[:255],
            "description": description,
            "issuetype": {"name": issue_type or self.default_issue_type},
            "labels": ["compass", "customer-feedback"]
        }

        if priority:
            issue_dict["priority"] = {"name": priority}

        try:
            new_issue = self.jira.create_issue(fields=issue_dict)

            # Update feedback with external ID
            external_ids = feedback.external_ids or {}
            external_ids["jira_key"] = new_issue.key
            external_ids["jira_url"] = f"{self.jira_url}/browse/{new_issue.key}"
            feedback.external_ids = external_ids
            self.db.commit()

            return {
                "status": "success",
                "jira_key": new_issue.key,
                "jira_url": f"{self.jira_url}/browse/{new_issue.key}"
            }

        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def link_existing_issue(
        self,
        jira_key: str,
        cluster_id: Optional[int] = None,
        roadmap_item_id: Optional[int] = None
    ) -> Dict:
        """
        Link an existing Jira issue to a Compass cluster or roadmap item.

        Args:
            jira_key: Jira issue key (e.g., "PROJ-123")
            cluster_id: Optional cluster ID to link
            roadmap_item_id: Optional roadmap item ID to link

        Returns:
            Result dictionary
        """
        from models import JiraIssue

        if not cluster_id and not roadmap_item_id:
            return {"status": "error", "error": "Must specify cluster_id or roadmap_item_id"}

        try:
            # Fetch issue from Jira
            issue = self.jira.issue(jira_key)

            # Store in database
            jira_issue = JiraIssue(
                jira_key=issue.key,
                jira_id=str(issue.id),
                jira_url=f"{self.jira_url}/browse/{issue.key}",
                cluster_id=cluster_id,
                roadmap_item_id=roadmap_item_id,
                title=str(issue.fields.summary),
                description=str(issue.fields.description) if issue.fields.description else None,
                status=str(issue.fields.status),
                priority=str(issue.fields.priority) if issue.fields.priority else None,
                assignee=issue.fields.assignee.displayName if issue.fields.assignee else None,
                issue_type=str(issue.fields.issuetype),
                sync_direction="bidirectional",
                last_synced_at=datetime.utcnow()
            )
            self.db.add(jira_issue)
            self.db.commit()

            return {
                "status": "success",
                "jira_key": issue.key,
                "jira_url": f"{self.jira_url}/browse/{issue.key}"
            }

        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def sync_issue_status(self, jira_key: str) -> Dict:
        """
        Sync status from Jira to Compass.

        Args:
            jira_key: Jira issue key

        Returns:
            Sync result dictionary
        """
        from models import JiraIssue, RoadmapItem

        # Get stored issue
        jira_issue = self.db.query(JiraIssue).filter(JiraIssue.jira_key == jira_key).first()
        if not jira_issue:
            return {"status": "error", "error": f"Jira issue {jira_key} not found in Compass"}

        try:
            # Fetch latest from Jira
            issue = self.jira.issue(jira_key)

            # Update stored data
            jira_issue.status = str(issue.fields.status)
            jira_issue.priority = str(issue.fields.priority) if issue.fields.priority else None
            jira_issue.assignee = issue.fields.assignee.displayName if issue.fields.assignee else None
            jira_issue.last_synced_at = datetime.utcnow()

            # Map Jira status to Compass roadmap status
            compass_status = self._map_jira_status_to_compass(str(issue.fields.status))

            # Update roadmap item if linked
            if jira_issue.roadmap_item_id:
                roadmap_item = self.db.query(RoadmapItem).filter(
                    RoadmapItem.id == jira_issue.roadmap_item_id
                ).first()
                if roadmap_item:
                    roadmap_item.status = compass_status
                    roadmap_item.updated_at = datetime.utcnow()

            self.db.commit()

            return {
                "status": "success",
                "jira_key": jira_key,
                "jira_status": str(issue.fields.status),
                "compass_status": compass_status
            }

        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def sync_all_issues(self) -> Dict:
        """
        Sync all linked Jira issues.

        Returns:
            Summary of sync results
        """
        from models import JiraIssue

        jira_issues = self.db.query(JiraIssue).all()

        synced = 0
        errors = []

        for jira_issue in jira_issues:
            result = self.sync_issue_status(jira_issue.jira_key)
            if result["status"] == "success":
                synced += 1
            else:
                errors.append({
                    "jira_key": jira_issue.jira_key,
                    "error": result.get("error")
                })

        return {
            "status": "success",
            "total_issues": len(jira_issues),
            "synced": synced,
            "errors": errors
        }

    def update_issue_priority(self, jira_key: str, new_priority: str) -> Dict:
        """
        Update Jira issue priority based on Compass data.

        Args:
            jira_key: Jira issue key
            new_priority: New priority ("Highest", "High", "Medium", "Low", "Lowest")

        Returns:
            Update result
        """
        try:
            issue = self.jira.issue(jira_key)
            issue.update(fields={"priority": {"name": new_priority}})

            # Update in database
            from models import JiraIssue
            jira_issue = self.db.query(JiraIssue).filter(JiraIssue.jira_key == jira_key).first()
            if jira_issue:
                jira_issue.priority = new_priority
                jira_issue.last_synced_at = datetime.utcnow()
                self.db.commit()

            return {
                "status": "success",
                "jira_key": jira_key,
                "priority": new_priority
            }

        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def add_comment(self, jira_key: str, comment: str) -> Dict:
        """
        Add a comment to a Jira issue.

        Args:
            jira_key: Jira issue key
            comment: Comment text

        Returns:
            Result dictionary
        """
        try:
            self.jira.add_comment(jira_key, comment)
            return {
                "status": "success",
                "jira_key": jira_key
            }
        except JIRAError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # Helper methods

    def _build_issue_description(self, cluster, feedback_list: List) -> str:
        """Build Jira issue description from cluster data."""
        description = f"""
*Cluster Summary*
- Request Count: {cluster.size}
- Priority Score: {cluster.priority_score:.2f}
- Total Revenue Impact: ${cluster.total_revenue:,.2f}
- Average Sentiment: {self._format_sentiment(cluster.avg_sentiment)}

*Top Customer Feedback:*
""".strip()

        for idx, fb in enumerate(feedback_list[:5], 1):
            customer_info = f"{fb.customer_name} (${fb.customer_revenue:,.0f})" if fb.customer_name else "Anonymous"
            description += f"\n\n{idx}. *{customer_info}*\n{fb.text[:200]}..."

        description += "\n\n---\n_Generated by Compass - Customer Feedback Intelligence Platform_"

        return description

    def _add_feedback_comment(self, jira_key: str, feedback_list: List):
        """Add detailed feedback as a comment."""
        if not feedback_list:
            return

        comment = "*Detailed Customer Feedback:*\n\n"
        for idx, fb in enumerate(feedback_list[:10], 1):
            customer = fb.customer_name or "Anonymous"
            revenue = f"${fb.customer_revenue:,.0f}" if fb.customer_revenue else "N/A"
            comment += f"{idx}. {customer} ({revenue})\n{fb.text[:300]}\n\n"

        try:
            self.jira.add_comment(jira_key, comment)
        except JIRAError:
            pass  # Non-critical

    def _map_priority_score_to_jira(self, score: float) -> str:
        """Map Compass priority score to Jira priority."""
        if score >= 0.8:
            return "Highest"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Medium"
        elif score >= 0.2:
            return "Low"
        else:
            return "Lowest"

    def _map_jira_status_to_compass(self, jira_status: str) -> str:
        """Map Jira status to Compass roadmap status."""
        status_lower = jira_status.lower()

        if any(s in status_lower for s in ["done", "closed", "resolved", "completed"]):
            return "shipped"
        elif any(s in status_lower for s in ["in progress", "in development", "in review"]):
            return "in_progress"
        elif any(s in status_lower for s in ["selected", "planned", "committed"]):
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
