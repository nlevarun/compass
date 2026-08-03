"""
SQLAlchemy models for Compass - Customer Feedback Intelligence Platform

Designed for SQLite MVP with easy PostgreSQL migration path.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Source(Base):
    """Feedback source configuration (Slack, Email, Support, etc.)"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # "Slack", "Email", etc.
    source_type = Column(String(50), nullable=False)  # "real" or "mock"
    is_active = Column(Boolean, default=True)
    config = Column(JSON)  # OAuth tokens, API keys, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)

    # Relationships
    feedback = relationship("Feedback", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type='{self.source_type}')>"


class Feedback(Base):
    """Individual feedback entry from any source"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    # Content
    text = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)  # For emails, tickets

    # Metadata
    customer_name = Column(String(200), nullable=True)
    customer_revenue = Column(Float, nullable=True)  # Annual revenue for prioritization
    sentiment_score = Column(Float, nullable=True)  # -1 to 1

    # Timestamps
    submitted_at = Column(DateTime, nullable=False)  # When customer submitted
    ingested_at = Column(DateTime, default=datetime.utcnow)  # When we ingested

    # Clustering
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    embedding = Column(JSON, nullable=True)  # Serialized vector for similarity search

    # Source-specific metadata
    source_metadata = Column(JSON)  # email_id, ticket_id, slack_msg_id, etc.

    # External integrations
    external_ids = Column(JSON)  # {"zendesk": "12345", "jira": "PROJ-123", etc.}

    # Relationships
    source = relationship("Source", back_populates="feedback")
    cluster = relationship("Cluster", back_populates="feedback")

    # Indexes for performance
    __table_args__ = (
        Index("idx_source_submitted", "source_id", "submitted_at"),
        Index("idx_cluster", "cluster_id"),
        Index("idx_sentiment", "sentiment_score"),
    )

    def __repr__(self):
        return f"<Feedback(id={self.id}, customer='{self.customer_name}', sentiment={self.sentiment_score:.2f})>"


class Cluster(Base):
    """NLP-generated cluster of similar feedback"""
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True)

    # Cluster info
    label = Column(String(200), nullable=False)  # Auto-generated: "Mobile App Performance Issues"
    description = Column(Text, nullable=True)  # Longer summary
    size = Column(Integer, default=0)  # Number of feedback items

    # Priority metrics
    priority_score = Column(Float, default=0.0)  # Calculated from revenue, frequency, sentiment
    total_revenue = Column(Float, default=0.0)  # Sum of customer revenues
    avg_sentiment = Column(Float, default=0.0)  # Average sentiment

    # Clustering metadata
    centroid = Column(JSON, nullable=True)  # Cluster center embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    feedback = relationship("Feedback", back_populates="cluster")
    roadmap_items = relationship("RoadmapItem", back_populates="cluster")

    # Indexes
    __table_args__ = (
        Index("idx_priority", "priority_score"),
    )

    def __repr__(self):
        return f"<Cluster(id={self.id}, label='{self.label}', size={self.size}, priority={self.priority_score:.2f})>"


class RoadmapItem(Base):
    """Prioritized roadmap feature derived from clusters"""
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)

    # Roadmap info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="proposed")  # proposed, planned, in_progress, shipped

    # Priority
    rank = Column(Integer, nullable=False)  # 1 = highest priority
    priority_score = Column(Float, nullable=False)

    # Effort estimation
    estimated_effort = Column(String(50), nullable=True)  # "small", "medium", "large"
    estimated_value = Column(String(50), nullable=True)  # "low", "medium", "high"

    # Metrics
    request_count = Column(Integer, default=0)
    impacted_revenue = Column(Float, default=0.0)

    # Build tracking (for closed-loop feedback)
    build_started_at = Column(DateTime, nullable=True)  # When development started
    shipped_at = Column(DateTime, nullable=True)  # When feature was released
    outcome_metrics = Column(JSON, nullable=True)  # Post-release metrics: {satisfaction_delta, churn_reduction, adoption_rate}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cluster = relationship("Cluster", back_populates="roadmap_items")
    jira_issues = relationship("JiraIssue", back_populates="roadmap_item")
    feature_builds = relationship("FeatureBuild", back_populates="roadmap_item", cascade="all, delete-orphan")
    releases = relationship("Release", secondary="feature_release_mapping", back_populates="roadmap_items")

    # Indexes
    __table_args__ = (
        Index("idx_rank", "rank"),
        Index("idx_status", "status"),
        Index("idx_shipped_at", "shipped_at"),
    )

    def __repr__(self):
        return f"<RoadmapItem(id={self.id}, rank={self.rank}, title='{self.title}')>"


class ImportJob(Base):
    """Track historical data import jobs"""
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), nullable=False)  # "zendesk", "intercom", "csv"
    status = Column(String(50), default="pending")  # pending, running, completed, failed

    # Progress tracking
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)

    # Configuration
    config = Column(JSON)  # Import-specific config (API keys, filters, etc.)

    # Results
    result_summary = Column(JSON)  # Stats, errors, warnings
    error_log = Column(Text, nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # User tracking
    initiated_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index("idx_job_status", "status"),
        Index("idx_job_type", "job_type"),
    )

    def __repr__(self):
        return f"<ImportJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"


class JiraIssue(Base):
    """Track Jira issues linked to feedback/clusters"""
    __tablename__ = "jira_issues"

    id = Column(Integer, primary_key=True)

    # Jira identifiers
    jira_key = Column(String(50), nullable=False, unique=True)  # "PROJ-123"
    jira_id = Column(String(50), nullable=False)  # Numeric ID
    jira_url = Column(String(500), nullable=False)

    # Link to Compass entities
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id"), nullable=True)

    # Jira data snapshot
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)  # "To Do", "In Progress", "Done"
    priority = Column(String(50), nullable=True)  # "High", "Medium", "Low"
    assignee = Column(String(200), nullable=True)
    issue_type = Column(String(50), nullable=True)  # "Story", "Bug", "Epic"

    # Sync tracking
    sync_direction = Column(String(20), default="bidirectional")  # bidirectional, compass_to_jira, jira_to_compass
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String(50), default="synced")  # synced, pending, error

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cluster = relationship("Cluster")
    roadmap_item = relationship("RoadmapItem", back_populates="jira_issues")

    __table_args__ = (
        Index("idx_jira_key", "jira_key"),
        Index("idx_cluster_jira", "cluster_id"),
        Index("idx_roadmap_jira", "roadmap_item_id"),
    )

    def __repr__(self):
        return f"<JiraIssue(id={self.id}, key='{self.jira_key}', status='{self.status}')>"


class LinearIssue(Base):
    """Track Linear issues linked to feedback/clusters"""
    __tablename__ = "linear_issues"

    id = Column(Integer, primary_key=True)

    # Linear identifiers
    linear_id = Column(String(100), nullable=False, unique=True)  # UUID
    linear_identifier = Column(String(50), nullable=False)  # "PROJ-123"
    linear_url = Column(String(500), nullable=False)

    # Link to Compass entities
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id"), nullable=True)

    # Linear data snapshot
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)  # "Todo", "In Progress", "Done"
    priority = Column(Integer, nullable=True)  # 0-4 (0=none, 1=urgent, 2=high, 3=medium, 4=low)
    assignee = Column(String(200), nullable=True)

    # Sync tracking
    sync_direction = Column(String(20), default="bidirectional")
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String(50), default="synced")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cluster = relationship("Cluster")
    roadmap_item = relationship("RoadmapItem")

    __table_args__ = (
        Index("idx_linear_id", "linear_id"),
        Index("idx_cluster_linear", "cluster_id"),
        Index("idx_roadmap_linear", "roadmap_item_id"),
    )

    def __repr__(self):
        return f"<LinearIssue(id={self.id}, identifier='{self.linear_identifier}', status='{self.status}')>"


class Release(Base):
    """Track product releases with shipped features"""
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True)

    # Release info
    version = Column(String(50), nullable=False, unique=True)  # "v1.2.3"
    release_name = Column(String(200), nullable=True)  # "Spring 2026 Release"
    changelog = Column(Text, nullable=True)  # Markdown changelog
    release_notes_url = Column(String(500), nullable=True)

    # Timestamps
    released_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roadmap_items = relationship("RoadmapItem", secondary="feature_release_mapping", back_populates="releases")

    # Indexes
    __table_args__ = (
        Index("idx_released_at", "released_at"),
    )

    def __repr__(self):
        return f"<Release(id={self.id}, version='{self.version}', released_at='{self.released_at}')>"


class FeatureBuild(Base):
    """Track development work (commits, PRs) linked to roadmap items"""
    __tablename__ = "feature_builds"

    id = Column(Integer, primary_key=True)
    roadmap_item_id = Column(Integer, ForeignKey("roadmap_items.id"), nullable=False)

    # GitHub/Git metadata
    commit_sha = Column(String(40), nullable=True)  # Git commit hash
    branch_name = Column(String(200), nullable=True)
    pr_number = Column(Integer, nullable=True)
    pr_url = Column(String(500), nullable=True)
    pr_title = Column(String(500), nullable=True)
    pr_state = Column(String(20), nullable=True)  # "open", "closed", "merged"

    # Developer info
    author = Column(String(200), nullable=True)
    committer = Column(String(200), nullable=True)

    # Velocity tracking
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)

    # Timestamps
    committed_at = Column(DateTime, nullable=True)
    pr_created_at = Column(DateTime, nullable=True)
    pr_merged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roadmap_item = relationship("RoadmapItem", back_populates="feature_builds")

    # Indexes
    __table_args__ = (
        Index("idx_roadmap_build", "roadmap_item_id"),
        Index("idx_pr_number", "pr_number"),
        Index("idx_commit_sha", "commit_sha"),
    )

    def __repr__(self):
        return f"<FeatureBuild(id={self.id}, roadmap_item_id={self.roadmap_item_id}, pr_number={self.pr_number})>"


# Association table for many-to-many relationship between RoadmapItem and Release
from sqlalchemy import Table

feature_release_mapping = Table(
    'feature_release_mapping',
    Base.metadata,
    Column('roadmap_item_id', Integer, ForeignKey('roadmap_items.id'), primary_key=True),
    Column('release_id', Integer, ForeignKey('releases.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


# Database utility functions for easy PostgreSQL migration
def get_connection_string(db_type: str = "sqlite", db_path: str = "compass.db") -> str:
    """
    Get database connection string.

    For PostgreSQL migration, change to:
    postgresql://user:password@host:port/dbname
    """
    if db_type == "sqlite":
        return f"sqlite:///{db_path}"
    elif db_type == "postgresql":
        # Placeholder for PostgreSQL migration
        return "postgresql://user:password@localhost:5432/compass"
    else:
        raise ValueError(f"Unsupported db_type: {db_type}")
