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

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cluster = relationship("Cluster", back_populates="roadmap_items")

    # Indexes
    __table_args__ = (
        Index("idx_rank", "rank"),
        Index("idx_status", "status"),
    )

    def __repr__(self):
        return f"<RoadmapItem(id={self.id}, rank={self.rank}, title='{self.title}')>"


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
