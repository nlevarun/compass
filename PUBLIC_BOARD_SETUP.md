# Public Feedback Board - Setup Guide

## Overview

This guide will help you set up and deploy the Public Feedback Board feature (Compass's Canny competitor).

---

## Installation Steps

### Step 1: Install Dependencies

#### Backend (already done)
The backend dependencies are already installed, but ensure the database has the new models:

```bash
cd /home/wsl-user/compass/backend
source venv/bin/activate

# Run database migration to add public board tables
python migrate_db.py

# Or initialize from scratch (WARNING: This will reset the database)
python database.py
```

#### Frontend (React Router needed)
Install React Router for the new public board routes:

```bash
cd /home/wsl-user/compass/frontend

# Install react-router-dom
npm install react-router-dom@6.22.0

# Or replace package.json with the new version
cp package.json.new package.json
npm install
```

---

### Step 2: Update Frontend App.jsx

Replace the current App.jsx with the new routed version:

```bash
cd /home/wsl-user/compass/frontend/src
mv App.jsx App.old.jsx
mv App.new.jsx App.jsx
```

This enables routing for:
- `/boards/create` - Create new board
- `/boards/:slug` - Public board view
- `/boards/:slug/admin` - Admin dashboard

---

### Step 3: Verify Backend Integration

The public board API should already be integrated in `main.py`. Verify:

```bash
cd /home/wsl-user/compass/backend
grep "public_board_router" main.py
```

Expected output:
```python
from public_board_api import router as public_board_router
app.include_router(public_board_router)
```

If not present, add these lines to `main.py`:
1. Import: `from public_board_api import router as public_board_router`
2. Include: `app.include_router(public_board_router)` (after other routers)

---

### Step 4: Generate Demo Data

Create a demo board with sample data:

```bash
cd /home/wsl-user/compass/backend
python setup_demo_board.py
```

This creates:
- Demo board at: `http://localhost:5173/boards/compass-demo`
- 10 sample posts
- 50+ votes with revenue weighting
- Sample comments
- Admin email: `demo@compass.app`

---

### Step 5: Start the Application

#### Terminal 1: Backend
```bash
cd /home/wsl-user/compass/backend
source venv/bin/activate
python main.py
```

Expected output:
```
🚀 Starting Compass API...
✓ Database initialized at sqlite:///compass.db
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Terminal 2: Frontend
```bash
cd /home/wsl-user/compass/frontend
npm run dev
```

Expected output:
```
VITE v5.4.11  ready in 523 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### Step 6: Test the Demo Board

1. Open browser: `http://localhost:5173/boards/compass-demo`
2. You should see:
   - Board header with title and description
   - List of feedback posts with vote buttons
   - Sort dropdown (Most Votes, Revenue-Weighted, Recent, Trending)
3. Try voting:
   - Enter your email
   - Click the upvote button on any post
   - Vote count should increment instantly
4. Try sorting:
   - Switch to "Revenue-Weighted"
   - Notice posts with enterprise votes rank higher

---

## File Structure

Here's what was created:

```
compass/
├── backend/
│   ├── models.py                  # Added: PublicBoard, PublicPost, Vote, Comment
│   ├── public_board_api.py        # NEW: Public board API endpoints
│   ├── setup_demo_board.py        # NEW: Demo data generator
│   └── main.py                    # Updated: Include public_board_router
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PublicBoard.jsx    # NEW: Public board view
│   │   │   ├── BoardCreator.jsx   # NEW: Create board page
│   │   │   └── BoardAdmin.jsx     # NEW: Admin dashboard
│   │   ├── App.jsx                # Updated: Add routing
│   │   └── package.json           # Updated: Add react-router-dom
├── PUBLIC_BOARD_TEST.md           # NEW: Testing guide
├── DEMO_PUBLIC_BOARD.md           # NEW: Demo script
└── PUBLIC_BOARD_SETUP.md          # This file
```

---

## API Endpoints

The following endpoints are now available:

### Public Endpoints (no auth required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/public-boards/boards` | Create new board |
| GET | `/api/public-boards/boards/{slug}` | Get board by slug |
| GET | `/api/public-boards/boards` | List all public boards |
| POST | `/api/public-boards/boards/{slug}/posts` | Submit feedback |
| GET | `/api/public-boards/boards/{slug}/posts` | Get posts (with sorting/filtering) |
| POST | `/api/public-boards/posts/{post_id}/vote` | Vote on post |
| DELETE | `/api/public-boards/posts/{post_id}/vote` | Remove vote |
| POST | `/api/public-boards/posts/{post_id}/comments` | Add comment |
| GET | `/api/public-boards/posts/{post_id}/comments` | Get comments |

### Admin Endpoints (require admin email)

| Method | Endpoint | Description |
|--------|----------|-------------|
| PATCH | `/api/public-boards/posts/{post_id}/status` | Update post status |
| GET | `/api/public-boards/boards/{slug}/analytics` | Get board analytics |

---

## Database Schema

New tables added:

### `public_boards`
- `id` (UUID, primary key)
- `slug` (unique URL slug)
- `organization_name`, `title`, `description`
- `is_public`, `allow_anonymous`
- `theme_color`, `owner_email`
- `created_at`, `updated_at`

### `public_posts`
- `id` (UUID, primary key)
- `board_id` (foreign key)
- `title`, `description`, `category`, `status`
- `vote_count`, `revenue_weighted_score` (KEY FEATURE!)
- `author_email`, `author_name`
- `created_at`, `updated_at`

### `votes`
- `id` (UUID, primary key)
- `post_id` (foreign key)
- `user_email`, `user_name`
- `user_revenue` (for revenue-weighted scoring!)
- `voted_at`

### `comments`
- `id` (UUID, primary key)
- `post_id` (foreign key)
- `text`, `author_email`, `author_name`
- `is_admin` (board owner response)
- `created_at`, `updated_at`

---

## Revenue-Weighted Voting Formula

The key differentiator from Canny:

```python
def calculate_revenue_weighted_score(post, votes):
    total_score = 0.0
    for vote in votes:
        if vote.user_revenue > 0:
            # Logarithmic scaling: enterprise votes have more weight
            revenue_weight = 1 + log10(max(vote.user_revenue / 1000, 1))
            total_score += revenue_weight
        else:
            # Free users = 1 point
            total_score += 1.0
    return total_score
```

**Examples:**
- Free user vote: 1.0 point
- $1k customer: ~1.0 point
- $10k customer: ~2.0 points
- $100k customer: ~3.0 points
- $500k customer: ~3.7 points

This ensures enterprise feedback is prioritized without completely drowning out free users.

---

## Configuration Options

### Board Settings

When creating a board, you can configure:

- **Organization Name**: Your company name
- **Title**: Board title (e.g., "Product Feedback")
- **Description**: Board description
- **Theme Color**: Hex color for branding
- **Allow Anonymous**: Let users post without names
- **Owner Email**: Admin email for moderation

### Post Categories

Available categories:
- `feature` - Feature requests
- `bug` - Bug reports
- `improvement` - Improvements to existing features
- `question` - Questions

### Post Status

Admins can set status:
- `open` - New feedback
- `planned` - Accepted, planning to build
- `in_progress` - Currently being built
- `completed` - Feature shipped
- `closed` - Won't implement

---

## WebSocket Integration

The public board uses WebSockets for real-time updates:

### Events Emitted

```javascript
// When someone votes
{
  type: "vote_added",
  post_id: "uuid",
  vote_count: 47,
  revenue_weighted_score: 89.2
}

// When post is created
{
  type: "post_created",
  board_slug: "compass-demo",
  post: { id, title, author }
}

// When status changes
{
  type: "status_updated",
  post_id: "uuid",
  status: "planned"
}
```

All connected clients receive updates instantly (<1 second latency).

---

## Customization

### Branding

1. **Theme Color**: Set in board creation (`theme_color` field)
2. **Custom Domain**: Future feature (currently using slugs)
3. **Logo**: Future feature

### Embed on Website

Get embed code from admin dashboard:

```html
<iframe
  src="https://your-compass-domain.com/boards/your-slug"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>
```

---

## Troubleshooting

### Issue: "Board not found"
**Solution:** Check that:
1. Board slug is correct
2. Board exists in database: `SELECT * FROM public_boards;`
3. Backend is running on port 8000

### Issue: "Vote not working"
**Solution:** Check that:
1. User email is entered
2. User hasn't already voted (check browser console)
3. WebSocket is connected (green dot in header)

### Issue: "Revenue score not updating"
**Solution:**
- Revenue score is calculated when vote is cast
- To set customer revenue, use API:
  ```bash
  curl -X POST http://localhost:8000/api/public-boards/posts/{post_id}/vote \
    -H "Content-Type: application/json" \
    -d '{"user_email": "customer@enterprise.com", "user_revenue": 100000}'
  ```

### Issue: "Frontend routes not working"
**Solution:** Check that:
1. `react-router-dom` is installed: `npm list react-router-dom`
2. App.jsx has been updated with routing
3. Frontend dev server was restarted

---

## Production Deployment

### Backend

1. **Set environment variables**:
   ```bash
   export DATABASE_URL=postgresql://user:pass@host:5432/compass
   export API_SECRET_KEY=your-secret-key
   ```

2. **Use PostgreSQL** instead of SQLite:
   - Update `get_connection_string()` in `models.py`
   - Run migrations

3. **Enable authentication**:
   - Add JWT tokens for admin endpoints
   - Verify board ownership before status updates

4. **Add rate limiting**:
   - Prevent vote spam (1 vote per email per post)
   - Limit post creation (5 per hour per IP)

### Frontend

1. **Update API URL**:
   ```javascript
   const API_BASE = import.meta.env.VITE_API_URL || 'https://api.compass.app';
   ```

2. **Build for production**:
   ```bash
   npm run build
   ```

3. **Deploy static files** to CDN (Vercel, Netlify, etc.)

4. **Set up custom domain**:
   - Point `compass.app` to your frontend
   - Point `api.compass.app` to your backend

---

## Next Steps

1. **Test thoroughly** using `PUBLIC_BOARD_TEST.md`
2. **Practice demo** using `DEMO_PUBLIC_BOARD.md`
3. **Add integrations**:
   - Sync customer revenue from Stripe
   - Auto-create posts from support tickets
   - Send notifications to Slack
4. **Marketing**:
   - Create landing page
   - Highlight revenue-weighted voting
   - Position as "Canny alternative"

---

## Support

If you need help:

1. Check backend logs: `tail -f backend/logs/app.log`
2. Check browser console for errors
3. Test API directly:
   ```bash
   curl http://localhost:8000/api/public-boards/boards
   ```
4. Reset demo data:
   ```bash
   python setup_demo_board.py
   ```

---

**You're all set! 🚀**

The public feedback board is now ready to use. Create your first board at:
`http://localhost:5173/boards/create`
