# Windows Users Guide - Accessing Compass in WSL

If you're on Windows and trying to access the Compass project in WSL, follow these instructions.

## Quick Access

### Option 1: Use File Explorer
1. Open File Explorer
2. In the address bar, type: `\\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass`
3. Press Enter
4. You can now see all files and double-click `push.bat` or `open-wsl.bat`

### Option 2: Use Provided Batch Files

**From Windows Explorer (easiest):**
1. Navigate to: `\\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass`
2. Double-click **`push.bat`** to push to GitHub
3. Or double-click **`open-wsl.bat`** to open terminal in project directory

**From Windows Command Prompt:**
```cmd
\\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass\push.bat
```

### Option 3: Use WSL Command

From Windows Command Prompt:
```cmd
wsl
cd /home/wsl-user/compass
git push -u origin main
```

## First Time GitHub Push

When pushing for the first time, Git will ask for credentials:

### Method 1: Personal Access Token (Recommended)
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Generate and copy the token
5. When prompted for password, paste the token (NOT your GitHub password)

### Method 2: SSH Key
```bash
# In WSL
ssh-keygen -t ed25519 -C "nlevarun@gmail.com"
cat ~/.ssh/id_ed25519.pub
# Copy the output

# Add to GitHub: https://github.com/settings/keys
# Click "New SSH key", paste the output

# Update remote to use SSH
cd /home/wsl-user/compass
git remote set-url origin git@github.com:nlevarun/compass.git
git push -u origin main
```

## Running Compass from Windows

### Backend (Python API)
From Windows Command Prompt:
```cmd
wsl -e bash -c "cd /home/wsl-user/compass/backend && python3 main.py"
```

Or open WSL and run:
```bash
wsl
cd /home/wsl-user/compass/backend
python3 main.py
```

### Frontend (React)
From Windows Command Prompt:
```cmd
wsl -e bash -c "cd /home/wsl-user/compass/frontend && npm run dev"
```

Or open WSL and run:
```bash
wsl
cd /home/wsl-user/compass/frontend
npm run dev
```

## Accessing from Windows Browser

Once servers are running in WSL, access from Windows browser:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

WSL networking is bridged, so `localhost` works from Windows!

## Common Issues

### Issue: "fatal: not a git repository"
**Problem**: You're not in the right directory
**Solution**: Make sure you're in `/home/wsl-user/compass` inside WSL

### Issue: "The system cannot find the path specified"
**Problem**: Using Linux paths in Windows Command Prompt
**Solution**: Use `wsl` command first:
```cmd
wsl
cd /home/wsl-user/compass
```

### Issue: Permission denied when pushing
**Problem**: GitHub authentication failed
**Solution**: Use Personal Access Token (see above) instead of password

### Issue: Can't see files in File Explorer
**Problem**: WSL distribution name mismatch
**Solution**: In File Explorer address bar, try:
- `\\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass`
- `\\wsl$\Ubuntu\home\wsl-user\compass`
- Or just `\\wsl$\` and navigate manually

## VS Code Integration

Open Compass in VS Code from Windows:
```cmd
code \\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass
```

Or install "Remote - WSL" extension in VS Code, then:
1. Open VS Code
2. Press F1
3. Type "WSL: Open Folder in WSL"
4. Navigate to `/home/wsl-user/compass`

## Quick Command Reference

```cmd
REM Enter WSL
wsl

REM Run command in WSL from Windows
wsl -e bash -c "your-command-here"

REM Open project in WSL
wsl --cd /home/wsl-user/compass

REM List WSL distributions
wsl --list

REM Access files in File Explorer
\\wsl$\Ubuntu-24.04-Anthropic\home\wsl-user\compass
```

## Need Help?

Create an issue: https://github.com/nlevarun/compass/issues
