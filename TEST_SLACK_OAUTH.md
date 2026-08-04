# 🎯 Test Slack OAuth Integration

## ✅ What I Just Fixed

The CollectTab was showing static "Connect" buttons that didn't do anything. I've now integrated the **real OAuth connector components** so when you click "Connect", it actually opens the OAuth popup!

## 🚀 How to Test

### Step 1: Pull the Latest Code
```bash
cd ~/compass
git pull origin main
```

### Step 2: Stop the Running Servers
Press **Ctrl+C** in your terminal to stop both backend and frontend.

### Step 3: Restart Compass
```bash
./start.sh
```

Wait ~5 seconds for both servers to start.

### Step 4: Open the UI
Open your browser to: **http://localhost:5173**

### Step 5: Test Slack OAuth
1. Click on the **"Collect"** tab
2. Find the **"Slack"** source card
3. Click the **"Connect"** button
4. A popup window should open with Slack's OAuth authorization page
5. Approve the app
6. The popup should close automatically
7. You should see a success message!

---

## 🎨 What You'll See

### In the Collect Tab
You'll see 5 source cards:
- **Slack** - ✅ Has "Connect" button (OAuth ready)
- **GitHub** - ✅ Has "Connect" button (OAuth ready)
- **Linear** - ✅ Has "Connect" button (OAuth ready)
- **Discord** - "Coming Soon" (no OAuth yet)
- **Reddit** - "Coming Soon" (no OAuth yet)

### When You Click Connect
A modal will slide up from the bottom with:
- OAuth connection button
- Instructions
- Status indicators

For Slack specifically, you'll see:
- "Connect Slack Workspace" button
- Your workspace will be displayed after connection
- Channel selector
- Sync controls

---

## 🐛 Troubleshooting

### "Module not found: SlackConnector"
This means the frontend didn't rebuild. Try:
```bash
cd ~/compass/frontend
rm -rf dist .vite
cd ~/compass
./start.sh
```

### Popup is blocked
Check your browser's popup blocker settings and allow popups from localhost:5173.

### OAuth callback fails
Make sure your `.env` file has:
```bash
SLACK_CLIENT_ID=11732108455319.11744094153269
SLACK_CLIENT_SECRET=56406fa9070a16c461e5245796fdde0d
SLACK_REDIRECT_URI=http://localhost:8000/api/auth/slack/callback
```

### "404 Not Found" on callback
This means the backend OAuth routes aren't loaded. Check terminal for errors.

---

## 📊 Expected Results

**✅ Success looks like:**
1. Popup opens with Slack OAuth page
2. You approve the app
3. Popup closes automatically
4. Green success toast: "Slack connected successfully!"
5. Slack card shows "Connected" badge
6. You can see your Slack channels in the dropdown

**❌ Failure looks like:**
- Popup doesn't open (check popup blocker)
- Popup opens but shows 404 (backend issue)
- Callback fails with error (check .env credentials)
- Nothing happens when you click Connect (frontend issue)

---

## 🔍 What Changed

### Before
```jsx
<button className="...">Connect</button>
// ☝️ This did NOTHING
```

### After
```jsx
<button onClick={() => setSelectedConnector('slack')}>Connect</button>
// ☝️ Opens the SlackConnector modal with OAuth flow

{selectedConnector === 'slack' && (
  <SlackConnector onClose={...} onSuccess={...} />
)}
```

---

## 🎉 Next Steps

Once Slack OAuth works:
1. ✅ Test GitHub OAuth
2. ✅ Test Linear OAuth
3. ✅ Sync messages from Slack channel
4. ✅ Run AI clustering on real feedback
5. ✅ Generate priority roadmap

**Let me know what happens when you click "Connect Slack Workspace"!** 🚀
