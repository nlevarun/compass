#!/usr/bin/env python3
"""
Setup Demo Public Board

Creates a demo board with sample data for testing and demonstrations.
"""

import sys
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PublicBoard, PublicPost, Vote, Comment
import random


def generate_demo_board(db: Session):
    """Generate demo board with sample data"""

    print("Creating demo public feedback board...")

    # Create board
    board = PublicBoard(
        id=str(uuid.uuid4()),
        slug="compass-demo",
        organization_name="Compass Demo",
        title="Compass Product Feedback",
        description="Help us build better customer feedback tools! This is a demo board showcasing revenue-weighted voting.",
        is_public=True,
        allow_anonymous=True,
        theme_color="#4F46E5",
        owner_email="demo@compass.app"
    )
    db.add(board)
    db.commit()
    print(f"✓ Created board: {board.slug}")

    # Sample posts
    sample_posts = [
        {
            "title": "Add Dark Mode Support",
            "description": "We need a dark mode for nighttime usage. Many team members work late and find the bright interface straining.",
            "category": "feature",
            "status": "planned",
            "author": "Sarah Chen"
        },
        {
            "title": "Better Search Functionality",
            "description": "Current search is too basic. We need fuzzy matching, filters, and the ability to search within comments.",
            "category": "improvement",
            "status": "in_progress",
            "author": "Mike Johnson"
        },
        {
            "title": "Mobile App for iOS and Android",
            "description": "We need native mobile apps to access feedback on the go. Web browser on mobile isn't cutting it.",
            "category": "feature",
            "status": "open",
            "author": "Emily Rodriguez"
        },
        {
            "title": "Excel Export Broken for Large Datasets",
            "description": "When exporting more than 1000 rows to Excel, the file is corrupted. Getting error: 'invalid zipfile'.",
            "category": "bug",
            "status": "completed",
            "author": "David Park"
        },
        {
            "title": "Slack Integration for Real-Time Notifications",
            "description": "Would love to get Slack notifications when new high-priority feedback comes in.",
            "category": "feature",
            "status": "open",
            "author": "Jessica Williams"
        },
        {
            "title": "API Rate Limits Too Restrictive",
            "description": "We're hitting rate limits (100 req/min) during our daily sync. Need at least 500/min for our use case.",
            "category": "improvement",
            "status": "planned",
            "author": "Alex Kumar"
        },
        {
            "title": "Custom Fields for Feedback Items",
            "description": "We need to add custom fields like 'Product Line', 'Region', 'Customer Tier' to categorize feedback better.",
            "category": "feature",
            "status": "open",
            "author": "Rachel Green"
        },
        {
            "title": "Performance Issues on Clustering Page",
            "description": "The clustering view takes 30+ seconds to load with 10k+ feedback items. Need optimization.",
            "category": "bug",
            "status": "in_progress",
            "author": "Tom Anderson"
        },
        {
            "title": "SSO Support (SAML/OIDC)",
            "description": "Enterprise requirement: We need SSO integration with our identity provider (Okta).",
            "category": "feature",
            "status": "open",
            "author": "Lisa Thompson"
        },
        {
            "title": "Bulk Edit for Post Status",
            "description": "As an admin, I want to select multiple posts and change their status in bulk (e.g., mark 10 as 'planned').",
            "category": "improvement",
            "status": "open",
            "author": "Chris Martinez"
        }
    ]

    posts = []
    for i, post_data in enumerate(sample_posts):
        post = PublicPost(
            id=str(uuid.uuid4()),
            board_id=board.id,
            title=post_data["title"],
            description=post_data["description"],
            category=post_data["category"],
            status=post_data["status"],
            author_email=f"{post_data['author'].lower().replace(' ', '.')}@example.com",
            author_name=post_data["author"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        posts.append(post)
        db.add(post)

    db.commit()
    print(f"✓ Created {len(posts)} sample posts")

    # Sample enterprise customers with revenue
    enterprise_customers = [
        {"email": "john.smith@acmecorp.com", "name": "John Smith", "revenue": 150000},
        {"email": "jane.doe@techgiant.com", "name": "Jane Doe", "revenue": 250000},
        {"email": "bob.wilson@startupxyz.com", "name": "Bob Wilson", "revenue": 50000},
        {"email": "alice.brown@enterprise.com", "name": "Alice Brown", "revenue": 500000},
        {"email": "charlie.davis@bigco.com", "name": "Charlie Davis", "revenue": 100000},
    ]

    # Free/small customers
    free_customers = [
        {"email": "user1@gmail.com", "name": "Free User 1", "revenue": 0},
        {"email": "user2@gmail.com", "name": "Free User 2", "revenue": 0},
        {"email": "startup@small.com", "name": "Small Startup", "revenue": 1000},
        {"email": "indie@dev.com", "name": "Indie Developer", "revenue": 500},
        {"email": "test@user.com", "name": "Test User", "revenue": 0},
    ]

    all_customers = enterprise_customers + free_customers

    # Generate votes
    vote_count = 0
    for post in posts:
        # Each post gets 5-20 votes
        num_votes = random.randint(5, 20)
        voters = random.sample(all_customers, min(num_votes, len(all_customers)))

        for voter in voters:
            vote = Vote(
                id=str(uuid.uuid4()),
                post_id=post.id,
                user_email=voter["email"],
                user_name=voter["name"],
                user_revenue=voter["revenue"],
                voted_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(vote)
            vote_count += 1

        # Update post vote count
        post.vote_count = num_votes

        # Calculate revenue-weighted score
        revenue_score = 0.0
        for voter in voters:
            if voter["revenue"] > 0:
                import math
                revenue_weight = 1 + math.log10(max(voter["revenue"] / 1000, 1))
                revenue_score += revenue_weight
            else:
                revenue_score += 1.0

        post.revenue_weighted_score = round(revenue_score, 2)

    db.commit()
    print(f"✓ Created {vote_count} votes")

    # Generate some comments
    comment_texts = [
        "Great idea! We really need this.",
        "This would save us so much time.",
        "Strong +1 from our team.",
        "Is this being worked on? Any ETA?",
        "We've built a workaround but would love native support.",
        "This is critical for our enterprise deployment.",
        "Can you provide more details on the use case?",
        "Already voted! Looking forward to this.",
    ]

    comment_count = 0
    for post in random.sample(posts, 7):  # Add comments to 7 posts
        num_comments = random.randint(1, 5)
        for _ in range(num_comments):
            commenter = random.choice(all_customers)
            comment = Comment(
                id=str(uuid.uuid4()),
                post_id=post.id,
                text=random.choice(comment_texts),
                author_email=commenter["email"],
                author_name=commenter["name"],
                is_admin=False,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 25))
            )
            db.add(comment)
            comment_count += 1

    db.commit()
    print(f"✓ Created {comment_count} comments")

    print("\n" + "="*60)
    print("✅ Demo board created successfully!")
    print("="*60)
    print(f"\n📊 Board URL: http://localhost:5173/boards/{board.slug}")
    print(f"🔧 Admin URL: http://localhost:5173/boards/{board.slug}/admin")
    print(f"\n📧 Admin Email: {board.owner_email}")
    print(f"\n📈 Stats:")
    print(f"   - {len(posts)} posts")
    print(f"   - {vote_count} votes")
    print(f"   - {comment_count} comments")
    print(f"   - {len(enterprise_customers)} enterprise customers")
    print(f"   - {len(free_customers)} free/small customers")

    print(f"\n💡 Try this:")
    print(f"   1. Visit the board URL above")
    print(f"   2. Sort by 'Revenue-Weighted' to see enterprise votes prioritized")
    print(f"   3. Compare with 'Most Votes' sorting")
    print(f"   4. Vote on a post (use any email)")
    print(f"   5. Visit admin dashboard to manage posts")

    print(f"\n🎯 Key Feature to Demo:")
    print(f"   The '$500k enterprise' customer votes have ~3x weight vs free users!")
    print(f"   This is what Canny can't do - revenue-weighted voting!\n")


def main():
    db = SessionLocal()
    try:
        # Check if demo board already exists
        existing = db.query(PublicBoard).filter(PublicBoard.slug == "compass-demo").first()
        if existing:
            response = input("Demo board already exists. Delete and recreate? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return

            # Delete existing board (cascade will delete posts, votes, comments)
            db.delete(existing)
            db.commit()
            print("✓ Deleted existing demo board")

        generate_demo_board(db)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
