# How to Push to GitHub from WSL

## From Windows Command Prompt:

```cmd
# Enter WSL
wsl

# Navigate to project
cd /home/wsl-user/compass

# Push to GitHub
git push -u origin main
```

When prompted:
- **Username**: nlevarun
- **Password**: Use a Personal Access Token (NOT your GitHub password)
  - Create at: https://github.com/settings/tokens
  - Select scopes: `repo` (full control of private repositories)

## Or use this one-liner from Windows CMD:
```cmd
wsl -e bash -c "cd /home/wsl-user/compass && git push -u origin main"
```

---

## Alternative: Set up SSH (One-time)

```bash
# In WSL
ssh-keygen -t ed25519 -C "nlevarun@gmail.com"
cat ~/.ssh/id_ed25519.pub
# Copy the output and add to: https://github.com/settings/keys

# Update remote to use SSH
cd /home/wsl-user/compass
git remote set-url origin git@github.com:nlevarun/compass.git
git push -u origin main
```
