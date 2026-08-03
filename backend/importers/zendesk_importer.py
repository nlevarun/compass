"""
Zendesk Historical Data Importer

Import all historical support tickets from Zendesk.
Handles tickets, comments, tags, and customer data.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import asyncio
from sqlalchemy.orm import Session


class ZendeskImporter:
    """Import historical tickets from Zendesk API"""

    def __init__(
        self,
        subdomain: str,
        email: str,
        api_token: str,
        source_id: int,
        db: Session,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize Zendesk importer.

        Args:
            subdomain: Zendesk subdomain (e.g., "yourcompany")
            email: Admin email for API access
            api_token: Zendesk API token
            source_id: Compass source ID for imported tickets
            db: Database session
            progress_callback: Optional callback for progress updates (processed, total)
        """
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token
        self.source_id = source_id
        self.db = db
        self.progress_callback = progress_callback
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"

        # Auth for requests
        self.auth = (f"{email}/token", api_token)

    async def fetch_tickets(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[Dict]:
        """
        Fetch tickets from Zendesk API with pagination.

        Args:
            start_date: Earliest ticket creation date (default: 5 years ago)
            end_date: Latest ticket creation date (default: now)
            status_filter: Filter by ticket status (e.g., ["closed", "solved"])
            batch_size: Number of tickets per API request (max 100)

        Returns:
            List of ticket dictionaries
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=365 * 5)  # 5 years
        if end_date is None:
            end_date = datetime.utcnow()

        all_tickets = []
        next_url = f"{self.base_url}/incremental/tickets.json?start_time={int(start_date.timestamp())}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            while next_url:
                try:
                    response = await client.get(next_url, auth=self.auth)
                    response.raise_for_status()
                    data = response.json()

                    tickets = data.get("tickets", [])

                    # Apply status filter if specified
                    if status_filter:
                        tickets = [t for t in tickets if t.get("status") in status_filter]

                    # Stop if we've passed the end date
                    filtered_tickets = []
                    for ticket in tickets:
                        created_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
                        if created_at <= end_date:
                            filtered_tickets.append(ticket)
                        else:
                            next_url = None  # Stop pagination
                            break

                    all_tickets.extend(filtered_tickets)

                    # Update progress
                    if self.progress_callback:
                        self.progress_callback(len(all_tickets), len(all_tickets))

                    # Get next page
                    if data.get("end_of_stream", False):
                        next_url = None
                    else:
                        next_url = data.get("next_page")

                    # Rate limiting: Zendesk has 700 requests/minute limit
                    await asyncio.sleep(0.1)

                except httpx.HTTPError as e:
                    print(f"Error fetching Zendesk tickets: {e}")
                    raise

        return all_tickets

    async def fetch_ticket_comments(self, ticket_id: int) -> List[Dict]:
        """
        Fetch all comments for a specific ticket.

        Args:
            ticket_id: Zendesk ticket ID

        Returns:
            List of comment dictionaries
        """
        url = f"{self.base_url}/tickets/{ticket_id}/comments.json"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, auth=self.auth)
                response.raise_for_status()
                data = response.json()
                return data.get("comments", [])
            except httpx.HTTPError as e:
                print(f"Error fetching comments for ticket {ticket_id}: {e}")
                return []

    async def fetch_users_batch(self, user_ids: List[int]) -> Dict[int, Dict]:
        """
        Fetch user information in batch (for customer data).

        Args:
            user_ids: List of Zendesk user IDs

        Returns:
            Dictionary mapping user_id -> user data
        """
        if not user_ids:
            return {}

        # Zendesk allows max 100 users per batch request
        batch_size = 100
        all_users = {}

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(0, len(user_ids), batch_size):
                batch = user_ids[i:i + batch_size]
                ids_str = ",".join(map(str, batch))
                url = f"{self.base_url}/users/show_many.json?ids={ids_str}"

                try:
                    response = await client.get(url, auth=self.auth)
                    response.raise_for_status()
                    data = response.json()

                    for user in data.get("users", []):
                        all_users[user["id"]] = user

                    await asyncio.sleep(0.1)  # Rate limiting

                except httpx.HTTPError as e:
                    print(f"Error fetching users batch: {e}")

        return all_users

    def parse_ticket_to_feedback(self, ticket: Dict, comments: List[Dict], user_data: Optional[Dict] = None) -> Dict:
        """
        Convert Zendesk ticket to Compass feedback format.

        Args:
            ticket: Zendesk ticket dict
            comments: List of ticket comments
            user_data: Optional user/customer data

        Returns:
            Feedback dictionary ready for database insertion
        """
        # Combine ticket description with comments for full context
        description = ticket.get("description", "")
        comment_texts = [c.get("body", "") for c in comments if not c.get("public", True) == False]  # Only public comments
        full_text = f"{description}\n\n" + "\n\n".join(comment_texts[:5])  # Limit to first 5 comments

        # Extract customer info
        customer_name = None
        customer_revenue = None
        if user_data:
            customer_name = user_data.get("name") or user_data.get("email")
            # Try to extract revenue from custom fields or organization
            if "organization_fields" in user_data:
                customer_revenue = user_data["organization_fields"].get("annual_revenue")

        # Parse timestamps
        submitted_at = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))

        # Build external IDs
        external_ids = {
            "zendesk_ticket_id": str(ticket["id"]),
            "zendesk_url": ticket.get("url", "")
        }

        return {
            "source_id": self.source_id,
            "text": full_text[:10000],  # Limit text length
            "title": ticket.get("subject", "")[:500],
            "customer_name": customer_name,
            "customer_revenue": customer_revenue,
            "submitted_at": submitted_at,
            "ingested_at": datetime.utcnow(),
            "source_metadata": {
                "zendesk_ticket_id": ticket["id"],
                "zendesk_status": ticket.get("status"),
                "zendesk_priority": ticket.get("priority"),
                "zendesk_tags": ticket.get("tags", []),
                "zendesk_requester_id": ticket.get("requester_id"),
                "zendesk_type": ticket.get("type"),
                "comment_count": len(comments)
            },
            "external_ids": external_ids
        }

    async def import_tickets(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status_filter: Optional[List[str]] = None,
        fetch_comments: bool = True,
        fetch_users: bool = True,
        batch_size: int = 100
    ) -> Dict:
        """
        Full import pipeline: fetch tickets, comments, users, and save to database.

        Args:
            start_date: Earliest ticket date
            end_date: Latest ticket date
            status_filter: Filter by status
            fetch_comments: Whether to fetch ticket comments
            fetch_users: Whether to fetch user/customer data
            batch_size: Batch size for database commits

        Returns:
            Dictionary with import statistics
        """
        from models import Feedback

        print(f"Starting Zendesk import from {start_date or '5 years ago'} to {end_date or 'now'}...")

        # Fetch all tickets
        tickets = await self.fetch_tickets(start_date, end_date, status_filter)
        total_tickets = len(tickets)
        print(f"Fetched {total_tickets} tickets from Zendesk")

        if total_tickets == 0:
            return {"status": "success", "total_imported": 0, "failed": 0}

        # Fetch users in batch
        user_map = {}
        if fetch_users:
            print("Fetching customer data...")
            user_ids = list(set([t.get("requester_id") for t in tickets if t.get("requester_id")]))
            user_map = await self.fetch_users_batch(user_ids)
            print(f"Fetched {len(user_map)} users")

        # Process tickets in batches
        imported = 0
        failed = 0
        feedback_batch = []

        for idx, ticket in enumerate(tickets):
            try:
                # Fetch comments if enabled
                comments = []
                if fetch_comments:
                    comments = await self.fetch_ticket_comments(ticket["id"])

                # Get user data
                user_data = user_map.get(ticket.get("requester_id"))

                # Parse to feedback format
                feedback_data = self.parse_ticket_to_feedback(ticket, comments, user_data)
                feedback_batch.append(Feedback(**feedback_data))

                # Batch commit to database
                if len(feedback_batch) >= batch_size:
                    self.db.bulk_save_objects(feedback_batch)
                    self.db.commit()
                    imported += len(feedback_batch)
                    feedback_batch = []

                    # Progress callback
                    if self.progress_callback:
                        self.progress_callback(imported, total_tickets)

                    print(f"Imported {imported}/{total_tickets} tickets...")

            except Exception as e:
                print(f"Error importing ticket {ticket.get('id')}: {e}")
                failed += 1
                continue

        # Commit remaining batch
        if feedback_batch:
            self.db.bulk_save_objects(feedback_batch)
            self.db.commit()
            imported += len(feedback_batch)

        print(f"✓ Zendesk import complete: {imported} imported, {failed} failed")

        return {
            "status": "success",
            "total_imported": imported,
            "failed": failed,
            "total_tickets": total_tickets
        }
