# Frontend Debugging Guide

## Quick Start

### 1. Install Dependencies
```bash
cd /home/wsl-user/compass/frontend
npm install
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env if your backend is not running on localhost:8000
nano .env
```

### 3. Start Development Server
```bash
npm run dev
```

The app should now be accessible at `http://localhost:5173`

## Common Issues & Solutions

### Issue: Blank Page / White Screen

**Symptoms:**
- Browser shows blank white page
- Console may show errors

**Solutions:**

1. **Check Browser Console**
   ```
   Press F12 to open Developer Tools
   Look for red error messages in Console tab
   ```

2. **Verify Backend Connection**
   - Ensure backend is running on http://localhost:8000
   - Check `.env` file has correct `VITE_API_URL`
   - Test backend: `curl http://localhost:8000/api/stats`

3. **Clear Browser Cache**
   ```
   Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   ```

4. **Rebuild**
   ```bash
   rm -rf node_modules dist
   npm install
   npm run dev
   ```

### Issue: WebSocket Connection Failed

**Symptoms:**
- "Offline" indicator shows in UI
- Console shows WebSocket errors

**Solutions:**

1. **Backend WebSocket Not Running**
   - Verify backend supports WebSocket at `ws://localhost:8000/ws`
   - Check backend logs for WebSocket errors

2. **Graceful Degradation**
   - App will still work without WebSocket
   - Real-time updates won't work, but manual refresh will

3. **Disable WebSocket (if needed)**
   - Edit `src/services/websocket.js`
   - Comment out auto-connect code

### Issue: API Calls Failing

**Symptoms:**
- Components show "Loading..." indefinitely
- Console shows network errors

**Solutions:**

1. **Check Backend Status**
   ```bash
   curl http://localhost:8000/api/stats
   ```

2. **CORS Issues**
   - Backend must allow CORS from frontend origin
   - Check backend CORS configuration

3. **Timeout Issues**
   - Default timeout is 30 seconds
   - Check `src/services/api.js` timeout setting

### Issue: Component Crashes

**Symptoms:**
- Error boundary shows "Something went wrong"
- Specific tab/feature doesn't load

**Solutions:**

1. **Check Error Details**
   - Click "Error details" in error boundary
   - Look for specific component/line number

2. **Data Validation**
   - All components now handle null/undefined data
   - Check if backend returns expected data structure

3. **Reset to Dashboard**
   - Click "Try Again" or "Reload Page"
   - Switch to Dashboard tab first

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |
| `VITE_WS_URL` | `ws://localhost:8000/ws` | WebSocket endpoint |

### Configuration for Different Environments

**Local Development (default):**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

**Remote Backend:**
```env
VITE_API_URL=https://api.yourcompany.com
VITE_WS_URL=wss://api.yourcompany.com/ws
```

**Custom Port:**
```env
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000/ws
```

## Features & Error Handling

### Error Boundaries
- Each tab wrapped in error boundary
- Crashes isolated to individual components
- "Try Again" button resets component state

### Defensive Coding
- All API responses validated
- Arrays checked with `Array.isArray()`
- Objects checked for null/undefined
- Default values provided on error

### Loading States
- Spinner shown during data fetch
- User-friendly loading messages
- Timeout handling (30 seconds)

### Offline Support
- Online/offline detection
- Offline banner shows connection status
- App continues to work with cached data
- Service Worker for offline caching

### WebSocket Resilience
- Automatic reconnection with exponential backoff
- Connection state monitoring
- Graceful degradation if WebSocket unavailable
- Message queuing when offline

## Testing

### Manual Testing Checklist

- [ ] App loads without errors
- [ ] Dashboard tab displays correctly
- [ ] Feedback tab loads (even if empty)
- [ ] Clusters tab loads (even if empty)
- [ ] Roadmap tab loads (even if empty)
- [ ] Priority Analysis tab loads
- [ ] Error messages are user-friendly
- [ ] Backend connection failures handled gracefully
- [ ] WebSocket connection handled gracefully
- [ ] Offline banner works correctly

### Component Import Test

Run the import validation test:
```bash
npm run test
```

This verifies all components can be imported without syntax errors.

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Debugging Tips

### Enable Detailed Logging

1. **API Requests**
   - Check Network tab in DevTools
   - Look for failed requests (red)
   - Check response data

2. **WebSocket Messages**
   - Open Console in DevTools
   - Filter by `[WS]` to see WebSocket logs
   - Look for connection/disconnection messages

3. **React State**
   - Install React DevTools extension
   - Inspect component state and props

### Common Console Messages

**Normal:**
```
[WS] Connecting to: ws://localhost:8000/ws
[WS] Connected successfully
[WS] Client ID assigned: xxx
```

**Expected Warnings:**
```
API Network Error: No response received
// When backend is not running - this is OK, handled gracefully
```

**Errors to Investigate:**
```
Uncaught TypeError: Cannot read property 'x' of undefined
// This indicates missing null check - please report
```

## Performance

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Getting Help

1. **Check Console First**
   - Press F12
   - Look at Console tab
   - Note any error messages

2. **Check Network Tab**
   - See which API calls are failing
   - Check response status codes

3. **Report Issues**
   - Include browser console logs
   - Include network tab screenshots
   - Describe steps to reproduce

## Architecture

### Component Hierarchy
```
App
├── ErrorBoundary
│   ├── Dashboard
│   ├── FeedbackInbox
│   ├── ClusterView
│   ├── RoadmapDashboard
│   └── PriorityAnalysis
├── OfflineBanner
├── InstallPrompt
└── Toast
```

### Data Flow
1. Component mounts
2. useEffect triggers data fetch
3. API service makes HTTP request
4. Response validated and parsed
5. State updated with data or empty default
6. Component renders with data
7. WebSocket provides real-time updates

### Error Handling Flow
1. Try API call
2. Catch error in component
3. Log error to console
4. Set default/empty state
5. Show user-friendly message
6. Component continues to function

## Maintenance

### Adding New Components

1. Create component in `src/components/`
2. Add defensive null checks for all props
3. Add loading state
4. Handle API errors gracefully
5. Wrap in ErrorBoundary if needed
6. Add to import test

### Adding New API Endpoints

1. Add function to `src/services/api.js`
2. Export the function
3. Add error handling in component
4. Validate response data structure
5. Provide default values on error

## Security Notes

- No sensitive data in `.env` files committed to git
- API calls use axios with timeout
- XSS protection via React's default escaping
- CORS must be configured on backend
- WebSocket connections validated on backend

## Support

For issues specific to this frontend implementation, check:
1. This debug guide first
2. Browser console errors
3. Network tab for failed requests
4. Backend logs for API errors
