# MCP Implementation Guide for Compass
## Practical Step-by-Step Implementation

**Purpose**: Detailed technical guide for implementing MCP server for Compass
**Target Audience**: Developers building Compass MCP integration
**Timeline**: Q4 2026 (4-6 weeks)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Week 1: MCP Server Basics](#week-1-mcp-server-basics)
3. [Week 2: Resources Implementation](#week-2-resources-implementation)
4. [Week 3: Tools Implementation](#week-3-tools-implementation)
5. [Week 4: Prompts & Templates](#week-4-prompts--templates)
6. [Week 5: Security & Performance](#week-5-security--performance)
7. [Week 6: Testing & Launch](#week-6-testing--launch)
8. [Deployment](#deployment)
9. [Monitoring](#monitoring)

---

## Prerequisites

### Required Knowledge
- Python 3.12+
- FastAPI
- Async/await patterns
- JSON-RPC protocol basics
- Compass codebase familiarity

### Required Tools
```bash
# Install MCP Python SDK
pip install mcp

# Install testing tools
pip install pytest pytest-asyncio httpx

# Install Claude Desktop (for testing)
# Download from: https://claude.ai/desktop
```

### Compass Components Needed
- Database access (`/home/wsl-user/compass/backend/database.py`)
- Models (`/home/wsl-user/compass/backend/models.py`)
- NLP clustering (`/home/wsl-user/compass/backend/nlp/clustering.py`)
- Priority calculator (`/home/wsl-user/compass/backend/priority/calculator.py`)

---

## Week 1: MCP Server Basics

### Day 1: Project Setup

**Create MCP Server Directory**:
```bash
cd /home/wsl-user/compass/backend
mkdir mcp_server
cd mcp_server

# Create files
touch __init__.py
touch server.py
touch config.py
touch resources.py
touch tools.py
touch prompts.py
```

**File: `config.py`**
```python
"""MCP Server Configuration"""
import os
from typing import Optional

class MCPConfig:
    """Configuration for Compass MCP Server"""

    # Server info
    SERVER_NAME = "compass-mcp-server"
    SERVER_VERSION = "1.0.0"
    PROTOCOL_VERSION = "2024-11-05"

    # Database
    DATABASE_PATH = os.getenv(
        "COMPASS_DB_PATH",
        "/home/wsl-user/compass/backend/compass.db"
    )

    # Authentication
    API_KEY_HEADER = "X-Compass-API-Key"
    REQUIRE_AUTH = True

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_RESOURCE_SIZE_MB = 10

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "mcp_server.log"

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not os.path.exists(cls.DATABASE_PATH):
            raise ValueError(f"Database not found: {cls.DATABASE_PATH}")

        if cls.REQUIRE_AUTH and not os.getenv("COMPASS_API_KEY"):
            print("Warning: REQUIRE_AUTH is True but no API key set")
```

### Day 2: Basic Server Structure

**File: `server.py`**
```python
"""Compass MCP Server"""
import sys
import asyncio
import logging
from typing import Optional
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    Prompt,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from config import MCPConfig
from resources import CompassResources
from tools import CompassTools
from prompts import CompassPrompts

# Configure logging
logging.basicConfig(
    level=getattr(logging, MCPConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(MCPConfig.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompassMCPServer:
    """Compass MCP Server Implementation"""

    def __init__(self):
        self.server = Server(MCPConfig.SERVER_NAME)
        self.resources = CompassResources()
        self.tools = CompassTools()
        self.prompts = CompassPrompts()

        # Setup handlers
        self._setup_handlers()

        logger.info(f"Initialized {MCPConfig.SERVER_NAME} v{MCPConfig.SERVER_VERSION}")

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        # Resources
        @self.server.list_resources()
        async def list_resources():
            """List available resources"""
            logger.debug("list_resources called")
            return await self.resources.list()

        @self.server.read_resource()
        async def read_resource(uri: str):
            """Read a specific resource"""
            logger.debug(f"read_resource called: {uri}")
            return await self.resources.read(uri)

        # Tools
        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            logger.debug("list_tools called")
            return await self.tools.list()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Execute a tool"""
            logger.info(f"call_tool: {name} with args: {arguments}")
            return await self.tools.call(name, arguments)

        # Prompts
        @self.server.list_prompts()
        async def list_prompts():
            """List available prompts"""
            logger.debug("list_prompts called")
            return await self.prompts.list()

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Optional[dict] = None):
            """Get a specific prompt"""
            logger.debug(f"get_prompt called: {name}")
            return await self.prompts.get(name, arguments)

    def run(self):
        """Run the MCP server"""
        try:
            MCPConfig.validate()
            logger.info(f"Starting {MCPConfig.SERVER_NAME}...")
            self.server.run()
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    server = CompassMCPServer()
    server.run()
```

### Day 3-5: Database Connection Layer

**File: `db.py`**
```python
"""Database utilities for MCP server"""
import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager

from config import MCPConfig

class CompassDatabase:
    """Database access for MCP server"""

    def __init__(self):
        self.db_path = MCPConfig.DATABASE_PATH

    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    async def get_all_feedback(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all feedback entries"""
        with self.get_connection() as conn:
            query = "SELECT * FROM feedback"
            params = []

            if source:
                query += " WHERE source_name = ?"
                params.append(source)

            query += " ORDER BY created_at DESC"

            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    'id': row['id'],
                    'text': row['text'],
                    'source': row['source_name'],
                    'sentiment': row['sentiment'],
                    'created_at': row['created_at'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
                for row in rows
            ]

    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict[str, Any]]:
        """Get specific feedback"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM feedback WHERE id = ?",
                (feedback_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return {
                'id': row['id'],
                'text': row['text'],
                'source': row['source_name'],
                'sentiment': row['sentiment'],
                'created_at': row['created_at'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            }

    async def get_all_clusters(self) -> List[Dict[str, Any]]:
        """Get all feedback clusters"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    c.*,
                    COUNT(f.id) as feedback_count,
                    AVG(f.sentiment) as avg_sentiment
                FROM clusters c
                LEFT JOIN feedback f ON f.cluster_id = c.id
                GROUP BY c.id
                ORDER BY c.priority_score DESC
            """)
            rows = cursor.fetchall()

            return [
                {
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'],
                    'feedback_count': row['feedback_count'],
                    'avg_sentiment': row['avg_sentiment'],
                    'priority_score': row['priority_score'],
                    'created_at': row['created_at']
                }
                for row in rows
            ]

    async def get_cluster_by_id(self, cluster_id: int) -> Optional[Dict[str, Any]]:
        """Get specific cluster with feedback"""
        with self.get_connection() as conn:
            # Get cluster
            cursor = conn.execute(
                "SELECT * FROM clusters WHERE id = ?",
                (cluster_id,)
            )
            cluster_row = cursor.fetchone()

            if not cluster_row:
                return None

            # Get feedback in cluster
            cursor = conn.execute(
                "SELECT * FROM feedback WHERE cluster_id = ?",
                (cluster_id,)
            )
            feedback_rows = cursor.fetchall()

            return {
                'id': cluster_row['id'],
                'title': cluster_row['title'],
                'description': cluster_row['description'],
                'priority_score': cluster_row['priority_score'],
                'created_at': cluster_row['created_at'],
                'feedback': [
                    {
                        'id': f['id'],
                        'text': f['text'],
                        'source': f['source_name'],
                        'sentiment': f['sentiment']
                    }
                    for f in feedback_rows
                ]
            }

    async def get_roadmap(self) -> List[Dict[str, Any]]:
        """Get current roadmap"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM roadmap_items
                ORDER BY rank ASC
            """)
            rows = cursor.fetchall()

            return [
                {
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'],
                    'rank': row['rank'],
                    'priority': row['priority'],
                    'cluster_id': row['cluster_id'],
                    'created_at': row['created_at']
                }
                for row in rows
            ]

    async def create_feedback(self, data: Dict[str, Any]) -> int:
        """Create new feedback entry"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO feedback (text, source_name, sentiment, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['text'],
                data.get('source', 'mcp'),
                data.get('sentiment', 0.0),
                json.dumps(data.get('metadata', {})),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    async def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        with self.get_connection() as conn:
            # Feedback count
            cursor = conn.execute("SELECT COUNT(*) as count FROM feedback")
            feedback_count = cursor.fetchone()['count']

            # Cluster count
            cursor = conn.execute("SELECT COUNT(*) as count FROM clusters")
            cluster_count = cursor.fetchone()['count']

            # Average sentiment
            cursor = conn.execute("SELECT AVG(sentiment) as avg FROM feedback")
            avg_sentiment = cursor.fetchone()['avg'] or 0.0

            # Sources
            cursor = conn.execute("""
                SELECT source_name, COUNT(*) as count
                FROM feedback
                GROUP BY source_name
            """)
            sources = {row['source_name']: row['count'] for row in cursor.fetchall()}

            return {
                'total_feedback': feedback_count,
                'total_clusters': cluster_count,
                'avg_sentiment': round(avg_sentiment, 3),
                'sources': sources
            }
```

---

## Week 2: Resources Implementation

### Resources Definition

**File: `resources.py`**
```python
"""MCP Resources for Compass"""
import json
from typing import List
from mcp.types import Resource, TextContent

from db import CompassDatabase

class CompassResources:
    """Manage Compass resources for MCP"""

    def __init__(self):
        self.db = CompassDatabase()

    async def list(self) -> List[Resource]:
        """List all available resources"""
        return [
            # Feedback resources
            Resource(
                uri="compass://feedback",
                name="All Feedback",
                mimeType="application/json",
                description="All feedback entries from all sources"
            ),
            Resource(
                uri="compass://feedback/{id}",
                name="Feedback by ID",
                mimeType="application/json",
                description="Get specific feedback entry by ID"
            ),

            # Cluster resources
            Resource(
                uri="compass://clusters",
                name="Feedback Clusters",
                mimeType="application/json",
                description="NLP-generated feedback clusters"
            ),
            Resource(
                uri="compass://clusters/{id}",
                name="Cluster by ID",
                mimeType="application/json",
                description="Get specific cluster with all feedback"
            ),

            # Roadmap resources
            Resource(
                uri="compass://roadmap",
                name="Product Roadmap",
                mimeType="application/json",
                description="Prioritized product roadmap"
            ),

            # Stats resources
            Resource(
                uri="compass://stats",
                name="Statistics",
                mimeType="application/json",
                description="Overall statistics and metrics"
            ),

            # Source-specific resources
            Resource(
                uri="compass://feedback/slack",
                name="Slack Feedback",
                mimeType="application/json",
                description="Feedback from Slack"
            ),
            Resource(
                uri="compass://feedback/github",
                name="GitHub Feedback",
                mimeType="application/json",
                description="Feedback from GitHub issues"
            ),
            Resource(
                uri="compass://feedback/discord",
                name="Discord Feedback",
                mimeType="application/json",
                description="Feedback from Discord"
            ),
            Resource(
                uri="compass://feedback/reddit",
                name="Reddit Feedback",
                mimeType="application/json",
                description="Feedback from Reddit"
            ),
        ]

    async def read(self, uri: str) -> TextContent:
        """Read a specific resource"""

        # Parse URI
        if uri == "compass://feedback":
            data = await self.db.get_all_feedback()
            return self._json_response(data)

        if uri.startswith("compass://feedback/") and "/" in uri[19:]:
            # compass://feedback/{id}
            feedback_id = int(uri.split("/")[-1])
            data = await self.db.get_feedback_by_id(feedback_id)
            if not data:
                raise ValueError(f"Feedback not found: {feedback_id}")
            return self._json_response(data)

        if uri == "compass://clusters":
            data = await self.db.get_all_clusters()
            return self._json_response(data)

        if uri.startswith("compass://clusters/"):
            cluster_id = int(uri.split("/")[-1])
            data = await self.db.get_cluster_by_id(cluster_id)
            if not data:
                raise ValueError(f"Cluster not found: {cluster_id}")
            return self._json_response(data)

        if uri == "compass://roadmap":
            data = await self.db.get_roadmap()
            return self._json_response(data)

        if uri == "compass://stats":
            data = await self.db.get_stats()
            return self._json_response(data)

        # Source-specific feedback
        if uri.startswith("compass://feedback/"):
            source = uri.split("/")[-1]
            data = await self.db.get_all_feedback(source=source)
            return self._json_response(data)

        raise ValueError(f"Unknown resource: {uri}")

    def _json_response(self, data) -> TextContent:
        """Create JSON text content response"""
        return TextContent(
            type="text",
            text=json.dumps(data, indent=2)
        )
```

---

## Week 3: Tools Implementation

### Tools Definition

**File: `tools.py`**
```python
"""MCP Tools for Compass"""
import json
from typing import List, Dict, Any
from mcp.types import Tool

from db import CompassDatabase

# Import Compass components
import sys
sys.path.append('/home/wsl-user/compass/backend')

from nlp.clustering import ClusteringEngine
from nlp.sentiment import SentimentAnalyzer
from priority.calculator import PriorityCalculator


class CompassTools:
    """Manage Compass tools for MCP"""

    def __init__(self):
        self.db = CompassDatabase()
        self.clustering_engine = ClusteringEngine()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.priority_calculator = PriorityCalculator()

    async def list(self) -> List[Tool]:
        """List all available tools"""
        return [
            # Analysis tools
            Tool(
                name="analyze_sentiment",
                description="Analyze sentiment of feedback text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Feedback text to analyze"
                        }
                    },
                    "required": ["text"]
                }
            ),

            Tool(
                name="analyze_feedback_batch",
                description="Analyze sentiment for multiple feedback entries",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feedback_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of feedback IDs to analyze"
                        }
                    },
                    "required": ["feedback_ids"]
                }
            ),

            # Clustering tools
            Tool(
                name="create_clusters",
                description="Run NLP clustering on feedback",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "eps": {
                            "type": "number",
                            "description": "DBSCAN epsilon parameter (0.1-1.0)",
                            "default": 0.3
                        },
                        "min_samples": {
                            "type": "integer",
                            "description": "Minimum samples per cluster",
                            "default": 3
                        },
                        "source_filter": {
                            "type": "string",
                            "description": "Filter by source (optional)"
                        }
                    }
                }
            ),

            Tool(
                name="find_similar_feedback",
                description="Find feedback similar to given text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Reference text"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 10
                        }
                    },
                    "required": ["text"]
                }
            ),

            # Priority tools
            Tool(
                name="calculate_priority",
                description="Calculate priority score for a cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_id": {
                            "type": "integer",
                            "description": "Cluster ID"
                        }
                    },
                    "required": ["cluster_id"]
                }
            ),

            Tool(
                name="generate_roadmap",
                description="Generate prioritized roadmap from clusters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_items": {
                            "type": "integer",
                            "description": "Maximum roadmap items",
                            "default": 20
                        }
                    }
                }
            ),

            # CRUD tools
            Tool(
                name="create_feedback",
                description="Create new feedback entry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Feedback text"
                        },
                        "source": {
                            "type": "string",
                            "description": "Source name"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        }
                    },
                    "required": ["text", "source"]
                }
            ),

            # Search tools
            Tool(
                name="search_feedback",
                description="Search feedback by keywords",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "source": {
                            "type": "string",
                            "description": "Filter by source"
                        },
                        "sentiment_min": {
                            "type": "number",
                            "description": "Minimum sentiment (-1 to 1)"
                        },
                        "sentiment_max": {
                            "type": "number",
                            "description": "Maximum sentiment (-1 to 1)"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 50
                        }
                    },
                    "required": ["query"]
                }
            ),
        ]

    async def call(self, name: str, arguments: dict) -> str:
        """Execute a tool"""

        if name == "analyze_sentiment":
            sentiment = await self.sentiment_analyzer.analyze(arguments['text'])
            return json.dumps({
                "sentiment": sentiment,
                "interpretation": self._interpret_sentiment(sentiment)
            })

        if name == "analyze_feedback_batch":
            results = []
            for feedback_id in arguments['feedback_ids']:
                feedback = await self.db.get_feedback_by_id(feedback_id)
                if feedback:
                    sentiment = await self.sentiment_analyzer.analyze(feedback['text'])
                    results.append({
                        "id": feedback_id,
                        "sentiment": sentiment,
                        "text_preview": feedback['text'][:100]
                    })
            return json.dumps({"results": results, "count": len(results)})

        if name == "create_clusters":
            eps = arguments.get('eps', 0.3)
            min_samples = arguments.get('min_samples', 3)
            source_filter = arguments.get('source_filter')

            # Get feedback
            feedback = await self.db.get_all_feedback(source=source_filter)

            # Run clustering
            clusters = await self.clustering_engine.cluster(
                feedback,
                eps=eps,
                min_samples=min_samples
            )

            return json.dumps({
                "clusters_created": len(clusters),
                "clusters": clusters
            })

        if name == "find_similar_feedback":
            similar = await self.clustering_engine.find_similar(
                arguments['text'],
                limit=arguments.get('limit', 10)
            )
            return json.dumps({"similar_feedback": similar})

        if name == "calculate_priority":
            cluster = await self.db.get_cluster_by_id(arguments['cluster_id'])
            if not cluster:
                raise ValueError(f"Cluster not found: {arguments['cluster_id']}")

            priority = await self.priority_calculator.calculate(cluster)
            return json.dumps({
                "cluster_id": cluster['id'],
                "priority_score": priority,
                "factors": self.priority_calculator.get_factors(cluster)
            })

        if name == "generate_roadmap":
            max_items = arguments.get('max_items', 20)

            # Get all clusters
            clusters = await self.db.get_all_clusters()

            # Calculate priorities
            roadmap = await self.priority_calculator.generate_roadmap(
                clusters,
                max_items=max_items
            )

            return json.dumps({
                "roadmap_items": roadmap,
                "total_items": len(roadmap)
            })

        if name == "create_feedback":
            feedback_id = await self.db.create_feedback(arguments)
            return json.dumps({
                "status": "created",
                "feedback_id": feedback_id
            })

        if name == "search_feedback":
            # Simple search implementation
            all_feedback = await self.db.get_all_feedback(
                source=arguments.get('source'),
                limit=arguments.get('limit', 50)
            )

            # Filter by query
            query = arguments['query'].lower()
            results = [
                f for f in all_feedback
                if query in f['text'].lower()
            ]

            # Filter by sentiment
            if 'sentiment_min' in arguments:
                results = [f for f in results if f['sentiment'] >= arguments['sentiment_min']]
            if 'sentiment_max' in arguments:
                results = [f for f in results if f['sentiment'] <= arguments['sentiment_max']]

            return json.dumps({
                "results": results,
                "count": len(results),
                "query": query
            })

        raise ValueError(f"Unknown tool: {name}")

    def _interpret_sentiment(self, sentiment: float) -> str:
        """Human-readable sentiment interpretation"""
        if sentiment > 0.5:
            return "Very positive"
        elif sentiment > 0.1:
            return "Positive"
        elif sentiment > -0.1:
            return "Neutral"
        elif sentiment > -0.5:
            return "Negative"
        else:
            return "Very negative"
```

---

## Week 4: Prompts & Templates

**File: `prompts.py`**
```python
"""MCP Prompts for Compass"""
from typing import List, Optional
from mcp.types import Prompt, PromptMessage, TextContent

class CompassPrompts:
    """Manage prompt templates for Compass"""

    async def list(self) -> List[Prompt]:
        """List all available prompts"""
        return [
            Prompt(
                name="analyze_feedback_summary",
                description="Generate summary of feedback",
                arguments=[
                    {
                        "name": "source",
                        "description": "Filter by source (optional)",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="roadmap_recommendation",
                description="Recommend roadmap priorities",
                arguments=[]
            ),
            Prompt(
                name="sentiment_analysis",
                description="Analyze sentiment trends",
                arguments=[
                    {
                        "name": "timeframe",
                        "description": "Timeframe (day/week/month)",
                        "required": False
                    }
                ]
            ),
        ]

    async def get(self, name: str, arguments: Optional[dict] = None) -> PromptMessage:
        """Get a specific prompt"""
        arguments = arguments or {}

        if name == "analyze_feedback_summary":
            source = arguments.get('source', 'all sources')
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""
                    Analyze the feedback from {source} and provide a comprehensive summary.

                    Please include:
                    1. Key themes and patterns
                    2. Most common requests
                    3. Sentiment overview
                    4. Priority recommendations
                    5. Actionable insights

                    Use the following MCP resources:
                    - compass://feedback/{source if source != 'all sources' else ''}
                    - compass://clusters
                    - compass://stats

                    Format your response in markdown with clear sections.
                    """
                )
            )

        if name == "roadmap_recommendation":
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="""
                    Based on current feedback and clusters, recommend a prioritized roadmap.

                    Steps:
                    1. Read compass://clusters
                    2. Read compass://stats
                    3. Use calculate_priority tool for each cluster
                    4. Use generate_roadmap tool
                    5. Provide rationale for top priorities

                    Format as:
                    # Recommended Roadmap

                    ## High Priority
                    - Item 1: [Reason]
                    - Item 2: [Reason]

                    ## Medium Priority
                    - ...

                    ## Rationale
                    [Explanation of prioritization logic]
                    """
                )
            )

        if name == "sentiment_analysis":
            timeframe = arguments.get('timeframe', 'week')
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""
                    Analyze sentiment trends over the past {timeframe}.

                    1. Read compass://feedback
                    2. Use analyze_feedback_batch tool
                    3. Group by source and time
                    4. Identify sentiment trends
                    5. Flag any concerning patterns

                    Report format:
                    # Sentiment Analysis ({timeframe})

                    ## Overall Sentiment
                    [Score and trend]

                    ## By Source
                    - Slack: [Sentiment + trend]
                    - GitHub: [Sentiment + trend]
                    - Discord: [Sentiment + trend]

                    ## Concerns
                    [Any negative trends or issues]

                    ## Recommendations
                    [Actions to take]
                    """
                )
            )

        raise ValueError(f"Unknown prompt: {name}")
```

---

## Week 5: Security & Performance

### Authentication

**File: `auth.py`**
```python
"""Authentication for MCP Server"""
import os
import hashlib
import secrets
from typing import Optional

class MCPAuthenticator:
    """Handle MCP server authentication"""

    def __init__(self):
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> dict:
        """Load API keys from environment/database"""
        keys = {}

        # Load from environment
        env_key = os.getenv('COMPASS_API_KEY')
        if env_key:
            keys[self._hash_key(env_key)] = {
                'name': 'env_key',
                'permissions': ['read', 'write']
            }

        # TODO: Load from database
        # keys.update(self._load_from_db())

        return keys

    def verify_key(self, api_key: str) -> bool:
        """Verify API key"""
        key_hash = self._hash_key(api_key)
        return key_hash in self.api_keys

    def get_permissions(self, api_key: str) -> list:
        """Get permissions for API key"""
        key_hash = self._hash_key(api_key)
        if key_hash in self.api_keys:
            return self.api_keys[key_hash]['permissions']
        return []

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def generate_key() -> str:
        """Generate new API key"""
        return secrets.token_urlsafe(32)
```

### Rate Limiting

**File: `rate_limiter.py`**
```python
"""Rate limiting for MCP server"""
import time
from collections import defaultdict, deque

class RateLimiter:
    """Rate limiter for MCP requests"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def allow_request(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Clean old requests
        while self.requests[client_id] and self.requests[client_id][0] < now - self.window_seconds:
            self.requests[client_id].popleft()

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Record request
        self.requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests"""
        return max(0, self.max_requests - len(self.requests[client_id]))
```

---

## Week 6: Testing & Launch

### Unit Tests

**File: `test_mcp_server.py`**
```python
"""Tests for MCP server"""
import pytest
import asyncio
from server import CompassMCPServer
from resources import CompassResources
from tools import CompassTools

@pytest.mark.asyncio
async def test_list_resources():
    """Test listing resources"""
    resources = CompassResources()
    result = await resources.list()

    assert len(result) > 0
    assert any(r.uri == "compass://feedback" for r in result)
    assert any(r.uri == "compass://clusters" for r in result)

@pytest.mark.asyncio
async def test_read_feedback_resource():
    """Test reading feedback resource"""
    resources = CompassResources()
    result = await resources.read("compass://feedback")

    assert result is not None
    assert result.type == "text"

@pytest.mark.asyncio
async def test_list_tools():
    """Test listing tools"""
    tools = CompassTools()
    result = await tools.list()

    assert len(result) > 0
    assert any(t.name == "analyze_sentiment" for t in result)
    assert any(t.name == "create_clusters" for t in result)

@pytest.mark.asyncio
async def test_analyze_sentiment_tool():
    """Test sentiment analysis tool"""
    tools = CompassTools()
    result = await tools.call("analyze_sentiment", {
        "text": "This is a great feature!"
    })

    assert "sentiment" in result
    assert "interpretation" in result
```

### Integration Test with Claude

**File: `test_with_claude.py`**
```bash
# Start MCP server
python server.py &
SERVER_PID=$!

# Test with Claude Desktop
# (Manual testing via Claude Desktop app)

# Cleanup
kill $SERVER_PID
```

### Launch Checklist

- [ ] All unit tests passing
- [ ] Integration tests with Claude successful
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance testing done
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup plan ready

---

## Deployment

### Local Development

```bash
# Start server (stdio transport)
python server.py

# Or with logging
python server.py --log-level DEBUG
```

### Claude Desktop Configuration

**File: `~/.claude/config.json`**
```json
{
  "mcpServers": {
    "compass": {
      "command": "python",
      "args": ["/home/wsl-user/compass/backend/mcp_server/server.py"],
      "env": {
        "COMPASS_DB_PATH": "/home/wsl-user/compass/backend/compass.db",
        "COMPASS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Production Deployment (SSE Transport)

**File: `mcp_server_sse.py`**
```python
"""MCP Server with SSE transport"""
from fastapi import FastAPI
from mcp.server.sse import create_sse_transport

app = FastAPI()

# Create SSE transport
transport = create_sse_transport("/mcp/sse")

# Mount to FastAPI
app.mount("/mcp", transport)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Docker Deployment

**File: `Dockerfile.mcp`**
```dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY mcp_server/ ./mcp_server/
COPY database.py models.py ./
COPY nlp/ ./nlp/
COPY priority/ ./priority/

CMD ["python", "mcp_server/server.py"]
```

```bash
# Build and run
docker build -f Dockerfile.mcp -t compass-mcp .
docker run -v /path/to/compass.db:/app/compass.db compass-mcp
```

---

## Monitoring

### Logging

```python
# Log all requests
logger.info(f"MCP Request: {method} {params}")

# Log errors
logger.error(f"Error in {method}: {error}", exc_info=True)
```

### Metrics

```python
"""Collect metrics"""
from prometheus_client import Counter, Histogram

request_count = Counter('mcp_requests_total', 'Total MCP requests')
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration')

@request_duration.time()
async def handle_request():
    request_count.inc()
    # ... handle request
```

### Health Check

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        await db.get_stats()

        return {
            "status": "healthy",
            "version": MCPConfig.SERVER_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## Conclusion

### Summary

You now have a complete guide to implementing MCP for Compass:

1. ✅ Basic server structure
2. ✅ Resources (feedback, clusters, roadmap)
3. ✅ Tools (analysis, clustering, priority)
4. ✅ Prompts (common queries)
5. ✅ Security (auth, rate limiting)
6. ✅ Testing strategy
7. ✅ Deployment options

### Next Steps

1. Start with Week 1 (basics)
2. Test each component incrementally
3. Integration test with Claude Desktop
4. Deploy to production
5. Monitor and iterate

### Resources

- Code location: `/home/wsl-user/compass/backend/mcp_server/`
- Compass database: `/home/wsl-user/compass/backend/compass.db`
- MCP spec: https://spec.modelcontextprotocol.io
- Claude Desktop: https://claude.ai/desktop

---

**Ready to build!**
