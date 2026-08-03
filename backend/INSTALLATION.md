# Compass WebSocket - Installation & Setup

## Quick Installation

### 1. Install Dependencies

```bash
cd /home/wsl-user/compass/backend
pip3 install -r requirements-minimal.txt
```

This will install:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `sqlalchemy` - Database ORM
- And other dependencies

### 2. Verify Installation

```bash
python3 -c "import fastapi, uvicorn, websockets; print('✓ All dependencies installed')"
```

### 3. Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🚀 Starting Compass API...
✓ Compass API ready!
✓ WebSocket support enabled at /ws
```

### 4. Test WebSocket Connection

In a new terminal:

```bash
cd /home/wsl-user/compass/backend
python3 test_websocket.py
```

Or run the example client:

```bash
python3 example_websocket_client.py
```

## Testing the Real-Time Features

### Terminal 1: Start Server
```bash
cd /home/wsl-user/compass/backend
uvicorn main:app --reload
```

### Terminal 2: Connect WebSocket Client
```bash
cd /home/wsl-user/compass/backend
python3 example_websocket_client.py
```

### Terminal 3: Trigger Events
```bash
# Sync feedback (triggers feedback.synced and stats.updated events)
curl -X POST http://localhost:8000/api/sources/sync

# Run clustering (triggers clustering.complete and cluster.created events)
curl -X POST http://localhost:8000/api/clustering/run

# Generate roadmap (triggers roadmap.generated event)
curl -X POST http://localhost:8000/api/roadmap/generate
```

You should see real-time events appear in Terminal 2!

## Troubleshooting

### "ModuleNotFoundError: No module named 'websockets'"

Install dependencies:
```bash
pip3 install websockets
```

### "Connection refused" when testing

Make sure the server is running:
```bash
uvicorn main:app --reload
```

### Port 8000 already in use

Use a different port:
```bash
uvicorn main:app --reload --port 8001
```

Then connect to `ws://localhost:8001/ws`

## Next Steps

1. **Run the test suite** - `python3 test_websocket.py`
2. **Try the interactive client** - `python3 test_websocket.py --interactive`
3. **Read the documentation** - `WEBSOCKET_README.md`
4. **Integrate with frontend** - See WebSocket protocol docs

## Production Deployment

For production, use gunicorn with uvicorn workers:

```bash
pip3 install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

And use WSS (secure WebSocket) with nginx reverse proxy.

See `WEBSOCKET_README.md` for security considerations.
