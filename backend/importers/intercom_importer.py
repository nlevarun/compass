"""
Intercom Historical Data Importer

Import all historical conversations from Intercom.
Handles conversations, messages, tags, and user data.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import asyncio
from sqlalchemy.orm import Session


class IntercomImporter:
    """Import historical conversations from Intercom API"""

    def __init__(
        self,
        access_token: str,
        source_id: int,
        db: Session,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize Intercom importer.

        Args:
            access_token: Intercom API access token
            source_id: Compass source ID for imported conversations
            db: Database session
            progress_callback: Optional callback for progress updates
        """
        self.access_token = access_token
        self.source_id = source_id
        self.db = db
        self.progress_callback = progress_callback
        self.base_url = "https://api.intercom.io"

        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Intercom-Version": "2.11"
        }

    async def fetch_conversations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        state_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch conversations from Intercom API with pagination.

        Args:
            start_date: Earliest conversation date (default: 5 years ago)
            end_date: Latest conversation date (default: now)
            state_filter: Filter by state ("open", "closed", "snoozed")

        Returns:
            List of conversation dictionaries
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=365 * 5)  # 5 years
        if end_date is None:
            end_date = datetime.utcnow()

        all_conversations = []
        url = f"{self.base_url}/conversations/search"

        # Build search query
        query = {
            "query": {
                "operator": "AND",
                "value": [
                    {
                        "field": "created_at",
                        "operator": ">",
                        "value": int(start_date.timestamp())
                    },
                    {
                        "field": "created_at",
                        "operator": "<",
                        "value": int(end_date.timestamp())
                    }
                ]
            },
            "pagination": {
                "per_page": 150  # Max allowed by Intercom
            }
        }

        # Add state filter if specified
        if state_filter:
            query["query"]["value"].append({
                "field": "state",
                "operator": "=",
                "value": state_filter
            })

        async with httpx.AsyncClient(timeout=30.0) as client:
            starting_after = None

            while True:
                try:
                    # Add pagination cursor if exists
                    if starting_after:
                        query["pagination"]["starting_after"] = starting_after

                    response = await client.post(
                        url,
                        json=query,
                        headers=self.headers
                    )
                    response.raise_for_status()
                    data = response.json()

                    conversations = data.get("conversations", [])
                    all_conversations.extend(conversations)

                    # Update progress
                    if self.progress_callback:
                        self.progress_callback(len(all_conversations), len(all_conversations))

                    # Check for next page
                    pages = data.get("pages", {})
                    if pages.get("next"):
                        starting_after = pages["next"].get("starting_after")
                    else:
                        break

                    # Rate limiting: Intercom has rate limits
                    await asyncio.sleep(0.2)

                except httpx.HTTPError as e:
                    print(f"Error fetching Intercom conversations: {e}")
                    raise

        return all_conversations

    async def fetch_conversation_parts(self, conversation_id: str) -> List[Dict]:
        """
        Fetch all message parts for a conversation.

        Args:
            conversation_id: Intercom conversation ID

        Returns:
            List of conversation part dictionaries
        """
        url = f"{self.base_url}/conversations/{conversation_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("conversation_parts", {}).get("conversation_parts", [])
            except httpx.HTTPError as e:
                print(f"Error fetching conversation parts for {conversation_id}: {e}")
                return []

    async def fetch_user(self, user_id: str) -> Optional[Dict]:
        """
        Fetch user/contact information.

        Args:
            user_id: Intercom user ID

        Returns:
            User data dictionary or None
        """
        url = f"{self.base_url}/contacts/{user_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching user {user_id}: {e}")
                return None

    def parse_conversation_to_feedback(
        self,
        conversation: Dict,
        parts: List[Dict],
        user_data: Optional[Dict] = None
    ) -> Dict:
        """
        Convert Intercom conversation to Compass feedback format.

        Args:
            conversation: Intercom conversation dict
            parts: List of conversation parts (messages)
            user_data: Optional user/contact data

        Returns:
            Feedback dictionary ready for database insertion
        """
        # Extract all user messages (not admin messages)
        source_info = conversation.get("source", {})
        first_message = source_info.get("body", "")

        user_messages = [first_message] if first_message else []
        for part in parts:
            if part.get("part_type") == "comment" and part.get("author", {}).get("type") == "user":
                body = part.get("body", "")
                if body:
                    user_messages.append(body)

        # Combine messages
        full_text = "\n\n".join(user_messages[:10])  # Limit to first 10 messages

        # Extract customer info
        customer_name = None
        customer_revenue = None
        if user_data:
            customer_name = user_data.get("name") or user_data.get("email")
            # Try to extract revenue from custom attributes
            custom_attrs = user_data.get("custom_attributes", {})
            if "annual_revenue" in custom_attrs:
                customer_revenue = custom_attrs["annual_revenue"]
            elif "mrr" in custom_attrs:  # Monthly recurring revenue
                customer_revenue = custom_attrs["mrr"] * 12

        # Parse timestamps
        submitted_at = datetime.fromtimestamp(conversation["created_at"])

        # Extract tags
        tags = [tag.get("name") for tag in conversation.get("tags", {}).get("tags", [])]

        # Build external IDs
        external_ids = {
            "intercom_conversation_id": conversation["id"],
            "intercom_url": f"https://app.intercom.com/a/inbox/{conversation['id']}"
        }

        return {
            "source_id": self.source_id,
            "text": full_text[:10000],  # Limit text length
            "title": source_info.get("subject", "")[:500] if source_info.get("subject") else None,
            "customer_name": customer_name,
            "customer_revenue": customer_revenue,
            "submitted_at": submitted_at,
            "ingested_at": datetime.utcnow(),
            "source_metadata": {
                "intercom_conversation_id": conversation["id"],
                "intercom_state": conversation.get("state"),
                "intercom_priority": conversation.get("priority"),
                "intercom_tags": tags,
                "intercom_user_id": conversation.get("source", {}).get("author", {}).get("id"),
                "message_count": len(parts) + 1,
                "conversation_rating": conversation.get("conversation_rating", {}).get("rating")
            },
            "external_ids": external_ids
        }

    async def import_conversations(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        state_filter: Optional[str] = None,
        fetch_parts: bool = True,
        fetch_users: bool = True,
        batch_size: int = 100
    ) -> Dict:
        """
        Full import pipeline: fetch conversations, parts, users, and save to database.

        Args:
            start_date: Earliest conversation date
            end_date: Latest conversation date
            state_filter: Filter by state ("open", "closed", "snoozed")
            fetch_parts: Whether to fetch conversation parts
            fetch_users: Whether to fetch user data
            batch_size: Batch size for database commits

        Returns:
            Dictionary with import statistics
        """
        from models import Feedback

        print(f"Starting Intercom import from {start_date or '5 years ago'} to {end_date or 'now'}...")

        # Fetch all conversations
        conversations = await self.fetch_conversations(start_date, end_date, state_filter)
        total_conversations = len(conversations)
        print(f"Fetched {total_conversations} conversations from Intercom")

        if total_conversations == 0:
            return {"status": "success", "total_imported": 0, "failed": 0}

        # Process conversations in batches
        imported = 0
        failed = 0
        feedback_batch = []

        for idx, conversation in enumerate(conversations):
            try:
                # Fetch conversation parts if enabled
                parts = []
                if fetch_parts:
                    parts = await self.fetch_conversation_parts(conversation["id"])

                # Fetch user data if enabled
                user_data = None
                if fetch_users:
                    user_id = conversation.get("source", {}).get("author", {}).get("id")
                    if user_id:
                        user_data = await self.fetch_user(user_id)

                # Parse to feedback format
                feedback_data = self.parse_conversation_to_feedback(conversation, parts, user_data)
                feedback_batch.append(Feedback(**feedback_data))

                # Batch commit to database
                if len(feedback_batch) >= batch_size:
                    self.db.bulk_save_objects(feedback_batch)
                    self.db.commit()
                    imported += len(feedback_batch)
                    feedback_batch = []

                    # Progress callback
                    if self.progress_callback:
                        self.progress_callback(imported, total_conversations)

                    print(f"Imported {imported}/{total_conversations} conversations...")

                # Rate limiting
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"Error importing conversation {conversation.get('id')}: {e}")
                failed += 1
                continue

        # Commit remaining batch
        if feedback_batch:
            self.db.bulk_save_objects(feedback_batch)
            self.db.commit()
            imported += len(feedback_batch)

        print(f"✓ Intercom import complete: {imported} imported, {failed} failed")

        return {
            "status": "success",
            "total_imported": imported,
            "failed": failed,
            "total_conversations": total_conversations
        }
