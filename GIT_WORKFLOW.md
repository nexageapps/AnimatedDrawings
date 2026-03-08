# Git Workflow Guide

## Branch Strategy

### Main Branches
- **`main`**: Synced with upstream (original Facebook Research repo). Keep this clean!
- **`develop`**: Your integration branch for ongoing development
- **`feature/*`**: Individual feature branches

## Current Setup

```bash
origin    → https://github.com/nexageapps/AnimatedDrawings.git (your fork)
upstream  → https://github.com/facebookresearch/AnimatedDrawings.git (original)
```

## Daily Workflow

### Starting a New Feature
```bash
# Make sure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### Working on a Feature
```bash
# Make changes, then commit
git add .
git commit -m "feat: description of changes"

# Push to your fork
git push origin feature/your-feature-name
```

### Merging a Feature
```bash
# Switch to develop
git checkout develop

# Merge feature
git merge feature/your-feature-name

# Push to your fork
git push origin develop

# Optional: Delete feature branch
git branch -d feature/your-feature-name
```

### Syncing with Upstream (Original Repo)
```bash
# Fetch updates from original repo
git fetch upstream

# Update main branch
git checkout main
git merge upstream/main
git push origin main

# Update develop with latest from main
git checkout develop
git merge main
git push origin develop
```

## Current Feature Branch

You're currently on: **`feature/themed-animation-platform`**

This branch contains your themed animation platform work. Commit and push when ready:

```bash
git add .
git commit -m "feat: add themed animation platform spec"
git push origin feature/themed-animation-platform
```

## Tips

- Keep `main` clean - only sync with upstream
- Do all development in `feature/*` branches
- Merge features into `develop` for testing
- Use descriptive branch names: `feature/api-integration`, `fix/animation-bug`
- Commit often with clear messages
