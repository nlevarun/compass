"""
Event System for Compass - Real-Time Event Emission

Emits events to WebSocket clients when data changes occur.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventEmitter:
    """
    Event emitter for broadcasting application events.

    Event Types:
    - feedback.new: New feedback ingested
    - feedback.synced: Bulk feedback sync completed
    - cluster.created: New cluster created
    - cluster.updated: Cluster updated
    - roadmap.generated: Roadmap generated
    - roadmap.updated: Roadmap item updated
    - stats.updated: Dashboard stats changed
    """

    def __init__(self, websocket_manager=None):
        """
        Initialize event emitter.

        Args:
            websocket_manager: WebSocket ConnectionManager instance
        """
        self.manager = websocket_manager
        self.event_history: List[dict] = []
        self.max_history = 100  # Keep last 100 events
        logger.info("EventEmitter initialized")

    def set_manager(self, manager):
        """
        Set or update the WebSocket manager.

        Args:
            manager: ConnectionManager instance
        """
        self.manager = manager
        logger.info("WebSocket manager attached to EventEmitter")

    async def emit(self, event_type: str, data: dict, room: Optional[str] = None):
        """
        Emit an event to connected clients.

        Args:
            event_type: Type of event (e.g., "feedback.new")
            data: Event data payload
            room: Optional room to broadcast to
        """
        event = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Broadcast via WebSocket
        if self.manager:
            try:
                await self.manager.broadcast(event, room_name=room)
                logger.info(f"Event emitted: {event_type} to room={room or 'all'}")
            except Exception as e:
                logger.error(f"Error emitting event {event_type}: {e}")
        else:
            logger.warning(f"No WebSocket manager - event {event_type} not broadcast")

    # --- Feedback Events ---

    async def emit_feedback_new(self, feedback_data: dict):
        """
        Emit when new feedback is ingested.

        Args:
            feedback_data: Feedback item details
        """
        await self.emit("feedback.new", feedback_data, room="feedback")

    async def emit_feedback_synced(self, sync_results: dict):
        """
        Emit when feedback sync completes.

        Args:
            sync_results: Sync statistics and results
        """
        await self.emit("feedback.synced", sync_results, room="feedback")

    async def emit_feedback_batch(self, feedback_list: List[dict]):
        """
        Emit batch of new feedback items.

        Args:
            feedback_list: List of feedback items
        """
        await self.emit("feedback.batch", {
            "count": len(feedback_list),
            "items": feedback_list[:10]  # Send first 10 for preview
        }, room="feedback")

    # --- Cluster Events ---

    async def emit_cluster_created(self, cluster_data: dict):
        """
        Emit when a new cluster is created.

        Args:
            cluster_data: Cluster details
        """
        await self.emit("cluster.created", cluster_data, room="clusters")

    async def emit_clustering_complete(self, clustering_results: dict):
        """
        Emit when clustering process completes.

        Args:
            clustering_results: Clustering statistics and metrics
        """
        await self.emit("clustering.complete", clustering_results, room="clusters")

    async def emit_cluster_updated(self, cluster_id: int, updates: dict):
        """
        Emit when a cluster is updated.

        Args:
            cluster_id: Cluster ID
            updates: Updated fields
        """
        await self.emit("cluster.updated", {
            "cluster_id": cluster_id,
            "updates": updates
        }, room="clusters")

    # --- Roadmap Events ---

    async def emit_roadmap_generated(self, roadmap_data: dict):
        """
        Emit when roadmap is generated.

        Args:
            roadmap_data: Roadmap generation results
        """
        await self.emit("roadmap.generated", roadmap_data, room="roadmap")

    async def emit_roadmap_updated(self, item_id: int, updates: dict):
        """
        Emit when a roadmap item is updated.

        Args:
            item_id: Roadmap item ID
            updates: Updated fields
        """
        await self.emit("roadmap.updated", {
            "item_id": item_id,
            "updates": updates
        }, room="roadmap")

    # --- Stats Events ---

    async def emit_stats_updated(self, stats: dict):
        """
        Emit when dashboard statistics change.

        Args:
            stats: Current statistics
        """
        await self.emit("stats.updated", stats, room="dashboard")

    # --- Progress Events ---

    async def emit_progress(self, task: str, progress: int, total: int, message: str = ""):
        """
        Emit progress updates for long-running tasks.

        Args:
            task: Task identifier (e.g., "clustering", "sync")
            progress: Current progress count
            total: Total items to process
            message: Optional progress message
        """
        await self.emit("progress.update", {
            "task": task,
            "progress": progress,
            "total": total,
            "percentage": round((progress / total) * 100, 1) if total > 0 else 0,
            "message": message
        })

    async def emit_task_started(self, task: str, message: str = ""):
        """
        Emit when a long-running task starts.

        Args:
            task: Task identifier
            message: Task description
        """
        await self.emit("task.started", {
            "task": task,
            "message": message
        })

    async def emit_task_completed(self, task: str, results: dict):
        """
        Emit when a task completes.

        Args:
            task: Task identifier
            results: Task results
        """
        await self.emit("task.completed", {
            "task": task,
            "results": results
        })

    async def emit_task_error(self, task: str, error: str):
        """
        Emit when a task encounters an error.

        Args:
            task: Task identifier
            error: Error message
        """
        await self.emit("task.error", {
            "task": task,
            "error": error
        })

    # --- Generic Events ---

    async def emit_notification(self, level: str, title: str, message: str):
        """
        Emit a user notification.

        Args:
            level: Notification level ("info", "success", "warning", "error")
            title: Notification title
            message: Notification message
        """
        await self.emit("notification", {
            "level": level,
            "title": title,
            "message": message
        })

    def get_recent_events(self, count: int = 10) -> List[dict]:
        """
        Get recent event history.

        Args:
            count: Number of events to retrieve

        Returns:
            List of recent events
        """
        return self.event_history[-count:]


# Global event emitter instance
event_emitter = EventEmitter()


# Helper functions for async/sync contexts

def emit_sync(event_type: str, data: dict, room: Optional[str] = None):
    """
    Emit event from synchronous context.

    Args:
        event_type: Event type
        data: Event data
        room: Optional room name
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create task in running loop
            asyncio.create_task(event_emitter.emit(event_type, data, room))
        else:
            # Run in new loop
            loop.run_until_complete(event_emitter.emit(event_type, data, room))
    except Exception as e:
        logger.error(f"Error in sync emit: {e}")


async def emit_async(event_type: str, data: dict, room: Optional[str] = None):
    """
    Emit event from async context.

    Args:
        event_type: Event type
        data: Event data
        room: Optional room name
    """
    await event_emitter.emit(event_type, data, room)


# Context manager for task tracking

class TaskTracker:
    """
    Context manager for tracking long-running tasks with progress.

    Usage:
        async with TaskTracker("clustering", "Running NLP clustering"):
            # do work
            await tracker.progress(50, 100, "Processing embeddings")
    """

    def __init__(self, task_name: str, description: str = ""):
        self.task_name = task_name
        self.description = description
        self.start_time = None

    async def __aenter__(self):
        self.start_time = datetime.utcnow()
        await event_emitter.emit_task_started(self.task_name, self.description)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Task failed
            await event_emitter.emit_task_error(self.task_name, str(exc_val))
        else:
            # Task succeeded
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()
            await event_emitter.emit_task_completed(self.task_name, {
                "elapsed_time": round(elapsed, 2)
            })

    async def progress(self, current: int, total: int, message: str = ""):
        """
        Update task progress.

        Args:
            current: Current progress
            total: Total items
            message: Progress message
        """
        await event_emitter.emit_progress(self.task_name, current, total, message)
