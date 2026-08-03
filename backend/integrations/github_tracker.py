"""
GitHub Integration for Build Tracking

Auto-links commits and PRs to roadmap items via keywords like:
- "Compass-123" or "COMPASS-123"
- "#123" (if configured)
- "Fixes #123", "Closes Compass-123", etc.

Tracks development velocity and estimates completion dates.
"""

import re
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from models import RoadmapItem, FeatureBuild
from database import get_db


class GitHubTracker:
    """Track GitHub activity and link to roadmap items"""

    def __init__(self, github_token: Optional[str] = None, repo_owner: str = "", repo_name: str = ""):
        """
        Initialize GitHub tracker.

        Args:
            github_token: GitHub personal access token
            repo_owner: GitHub repository owner (e.g., "octocat")
            repo_name: GitHub repository name (e.g., "hello-world")
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"

        # Keyword patterns to extract roadmap item IDs
        self.patterns = [
            r'compass[_-]?(\d+)',  # Compass-123, compass_123, COMPASS123
            r'#(\d+)',  # #123 (if context is clear)
        ]

    def extract_roadmap_ids(self, text: str) -> List[int]:
        """
        Extract roadmap item IDs from commit messages or PR descriptions.

        Args:
            text: Commit message or PR description

        Returns:
            List of roadmap item IDs found in text
        """
        ids = []
        text_lower = text.lower()

        for pattern in self.patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    item_id = int(match.group(1))
                    if item_id not in ids:
                        ids.append(item_id)
                except (ValueError, IndexError):
                    continue

        return ids

    async def fetch_recent_commits(self, since_days: int = 7) -> List[Dict]:
        """
        Fetch recent commits from GitHub.

        Args:
            since_days: Number of days to look back

        Returns:
            List of commit data dictionaries
        """
        if not self.github_token:
            return []

        since_date = (datetime.utcnow() - timedelta(days=since_days)).isoformat()
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits"

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        params = {
            "since": since_date,
            "per_page": 100
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching commits: {e}")
                return []

    async def fetch_recent_prs(self, state: str = "all", since_days: int = 30) -> List[Dict]:
        """
        Fetch recent pull requests from GitHub.

        Args:
            state: PR state - "open", "closed", or "all"
            since_days: Number of days to look back

        Returns:
            List of PR data dictionaries
        """
        if not self.github_token:
            return []

        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                prs = response.json()

                # Filter by date
                since_date = datetime.utcnow() - timedelta(days=since_days)
                filtered_prs = [
                    pr for pr in prs
                    if datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00')).replace(tzinfo=None) >= since_date
                ]

                return filtered_prs
            except httpx.HTTPError as e:
                print(f"Error fetching PRs: {e}")
                return []

    async def sync_commits_to_roadmap(self, db: Session) -> Dict[str, int]:
        """
        Sync recent commits to roadmap items based on keywords.

        Args:
            db: Database session

        Returns:
            Statistics: {"commits_processed": X, "builds_created": Y, "builds_updated": Z}
        """
        commits = await self.fetch_recent_commits(since_days=7)
        stats = {"commits_processed": 0, "builds_created": 0, "builds_updated": 0}

        for commit_data in commits:
            stats["commits_processed"] += 1

            # Extract commit info
            commit = commit_data.get("commit", {})
            sha = commit_data.get("sha")
            message = commit.get("message", "")
            author = commit.get("author", {}).get("name", "")
            committer = commit.get("committer", {}).get("name", "")
            committed_at_str = commit.get("author", {}).get("date", "")

            try:
                committed_at = datetime.fromisoformat(committed_at_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                committed_at = datetime.utcnow()

            # Extract roadmap item IDs
            roadmap_ids = self.extract_roadmap_ids(message)

            for roadmap_id in roadmap_ids:
                # Check if roadmap item exists
                roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_id).first()
                if not roadmap_item:
                    continue

                # Check if build already exists
                existing_build = db.query(FeatureBuild).filter(
                    FeatureBuild.roadmap_item_id == roadmap_id,
                    FeatureBuild.commit_sha == sha
                ).first()

                if existing_build:
                    # Update existing build
                    existing_build.author = author
                    existing_build.committer = committer
                    existing_build.committed_at = committed_at
                    stats["builds_updated"] += 1
                else:
                    # Create new build
                    new_build = FeatureBuild(
                        roadmap_item_id=roadmap_id,
                        commit_sha=sha,
                        author=author,
                        committer=committer,
                        committed_at=committed_at
                    )
                    db.add(new_build)
                    stats["builds_created"] += 1

                # Update roadmap item status
                if roadmap_item.status == "proposed" or roadmap_item.status == "planned":
                    roadmap_item.status = "in_progress"
                    if not roadmap_item.build_started_at:
                        roadmap_item.build_started_at = committed_at

        db.commit()
        return stats

    async def sync_prs_to_roadmap(self, db: Session) -> Dict[str, int]:
        """
        Sync recent PRs to roadmap items based on keywords.

        Args:
            db: Database session

        Returns:
            Statistics: {"prs_processed": X, "builds_created": Y, "builds_updated": Z}
        """
        prs = await self.fetch_recent_prs(state="all", since_days=30)
        stats = {"prs_processed": 0, "builds_created": 0, "builds_updated": 0}

        for pr_data in prs:
            stats["prs_processed"] += 1

            # Extract PR info
            pr_number = pr_data.get("number")
            pr_url = pr_data.get("html_url")
            pr_title = pr_data.get("title", "")
            pr_body = pr_data.get("body", "") or ""
            pr_state = pr_data.get("state")  # "open" or "closed"
            branch_name = pr_data.get("head", {}).get("ref", "")
            author = pr_data.get("user", {}).get("login", "")

            created_at_str = pr_data.get("created_at", "")
            merged_at_str = pr_data.get("merged_at")

            try:
                pr_created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                pr_created_at = datetime.utcnow()

            pr_merged_at = None
            if merged_at_str:
                try:
                    pr_merged_at = datetime.fromisoformat(merged_at_str.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass

            # Extract stats
            lines_added = pr_data.get("additions", 0)
            lines_deleted = pr_data.get("deletions", 0)
            files_changed = pr_data.get("changed_files", 0)

            # Extract roadmap item IDs from title and body
            combined_text = f"{pr_title} {pr_body}"
            roadmap_ids = self.extract_roadmap_ids(combined_text)

            for roadmap_id in roadmap_ids:
                # Check if roadmap item exists
                roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_id).first()
                if not roadmap_item:
                    continue

                # Check if build already exists
                existing_build = db.query(FeatureBuild).filter(
                    FeatureBuild.roadmap_item_id == roadmap_id,
                    FeatureBuild.pr_number == pr_number
                ).first()

                if existing_build:
                    # Update existing build
                    existing_build.pr_url = pr_url
                    existing_build.pr_title = pr_title
                    existing_build.pr_state = pr_state
                    existing_build.branch_name = branch_name
                    existing_build.author = author
                    existing_build.lines_added = lines_added
                    existing_build.lines_deleted = lines_deleted
                    existing_build.files_changed = files_changed
                    existing_build.pr_merged_at = pr_merged_at
                    stats["builds_updated"] += 1
                else:
                    # Create new build
                    new_build = FeatureBuild(
                        roadmap_item_id=roadmap_id,
                        pr_number=pr_number,
                        pr_url=pr_url,
                        pr_title=pr_title,
                        pr_state=pr_state,
                        branch_name=branch_name,
                        author=author,
                        lines_added=lines_added,
                        lines_deleted=lines_deleted,
                        files_changed=files_changed,
                        pr_created_at=pr_created_at,
                        pr_merged_at=pr_merged_at
                    )
                    db.add(new_build)
                    stats["builds_created"] += 1

                # Update roadmap item status based on PR state
                if pr_merged_at and roadmap_item.status != "shipped":
                    roadmap_item.status = "in_progress"  # Will be "shipped" when released
                elif pr_state == "open" and roadmap_item.status == "proposed":
                    roadmap_item.status = "in_progress"
                    if not roadmap_item.build_started_at:
                        roadmap_item.build_started_at = pr_created_at

        db.commit()
        return stats

    def calculate_velocity(self, db: Session, days: int = 30) -> Dict[str, float]:
        """
        Calculate development velocity based on historical data.

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Velocity metrics: {"avg_days_to_ship": X, "avg_commits_per_feature": Y, "avg_prs_per_feature": Z}
        """
        since_date = datetime.utcnow() - timedelta(days=days)

        # Get shipped roadmap items
        shipped_items = db.query(RoadmapItem).filter(
            RoadmapItem.status == "shipped",
            RoadmapItem.shipped_at.isnot(None),
            RoadmapItem.build_started_at.isnot(None),
            RoadmapItem.shipped_at >= since_date
        ).all()

        if not shipped_items:
            return {"avg_days_to_ship": 0, "avg_commits_per_feature": 0, "avg_prs_per_feature": 0}

        total_days = 0
        total_commits = 0
        total_prs = 0

        for item in shipped_items:
            # Calculate days from start to ship
            days_to_ship = (item.shipped_at - item.build_started_at).days
            total_days += days_to_ship

            # Count builds
            builds = db.query(FeatureBuild).filter(FeatureBuild.roadmap_item_id == item.id).all()
            for build in builds:
                if build.commit_sha:
                    total_commits += 1
                if build.pr_number:
                    total_prs += 1

        num_items = len(shipped_items)
        return {
            "avg_days_to_ship": round(total_days / num_items, 1),
            "avg_commits_per_feature": round(total_commits / num_items, 1),
            "avg_prs_per_feature": round(total_prs / num_items, 1)
        }

    def estimate_completion_date(self, db: Session, roadmap_item_id: int) -> Optional[datetime]:
        """
        Estimate completion date for a roadmap item based on historical velocity.

        Args:
            db: Database session
            roadmap_item_id: Roadmap item ID

        Returns:
            Estimated completion date or None
        """
        roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_item_id).first()
        if not roadmap_item or roadmap_item.status == "shipped":
            return None

        # Get velocity
        velocity = self.calculate_velocity(db, days=90)
        avg_days = velocity.get("avg_days_to_ship", 0)

        if avg_days == 0:
            return None

        # Adjust based on effort estimate
        effort_multiplier = {"small": 0.5, "medium": 1.0, "large": 2.0}
        multiplier = effort_multiplier.get(roadmap_item.estimated_effort, 1.0)
        estimated_days = avg_days * multiplier

        # If build started, use that as start date; otherwise, use now
        start_date = roadmap_item.build_started_at or datetime.utcnow()
        estimated_completion = start_date + timedelta(days=estimated_days)

        return estimated_completion


# Webhook handler for GitHub events (optional)
async def handle_github_webhook(event_type: str, payload: Dict, db: Session) -> Dict:
    """
    Handle GitHub webhook events for real-time tracking.

    Supported events:
    - push: New commits
    - pull_request: PR opened/closed/merged
    - release: New release published

    Args:
        event_type: GitHub event type (X-GitHub-Event header)
        payload: Event payload
        db: Database session

    Returns:
        Processing result
    """
    result = {"event_type": event_type, "processed": False, "message": ""}

    if event_type == "push":
        # Handle push event
        commits = payload.get("commits", [])
        result["commits_processed"] = 0

        for commit in commits:
            message = commit.get("message", "")
            sha = commit.get("id", "")
            author = commit.get("author", {}).get("name", "")

            # Extract roadmap IDs
            tracker = GitHubTracker()
            roadmap_ids = tracker.extract_roadmap_ids(message)

            for roadmap_id in roadmap_ids:
                roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_id).first()
                if roadmap_item:
                    # Create or update build
                    existing_build = db.query(FeatureBuild).filter(
                        FeatureBuild.roadmap_item_id == roadmap_id,
                        FeatureBuild.commit_sha == sha
                    ).first()

                    if not existing_build:
                        new_build = FeatureBuild(
                            roadmap_item_id=roadmap_id,
                            commit_sha=sha,
                            author=author,
                            committed_at=datetime.utcnow()
                        )
                        db.add(new_build)
                        result["commits_processed"] += 1

        db.commit()
        result["processed"] = True

    elif event_type == "pull_request":
        # Handle PR event
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "") or ""

        # Extract roadmap IDs
        tracker = GitHubTracker()
        combined_text = f"{pr_title} {pr_body}"
        roadmap_ids = tracker.extract_roadmap_ids(combined_text)

        for roadmap_id in roadmap_ids:
            roadmap_item = db.query(RoadmapItem).filter(RoadmapItem.id == roadmap_id).first()
            if roadmap_item:
                # Update roadmap item status based on PR action
                if action == "opened":
                    roadmap_item.status = "in_progress"
                elif action == "closed" and pr.get("merged"):
                    # PR merged, but not shipped until release
                    roadmap_item.status = "in_progress"

        db.commit()
        result["processed"] = True
        result["message"] = f"PR {pr_number} {action}"

    return result
