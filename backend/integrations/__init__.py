"""
External Integrations Module for Compass

Bidirectional sync with project management tools:
- Jira (issue tracking)
- Linear (modern issue tracking)
"""

from .jira_sync import JiraSync
from .linear_sync import LinearSync

__all__ = ["JiraSync", "LinearSync"]
