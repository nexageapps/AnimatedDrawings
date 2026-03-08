# Git Workflow Guide

## Repository Status

**Original repo is ARCHIVED** (read-only as of Sep 4, 2025) - No more updates expected!

This means:
- Your fork is now the active development version
- No need to sync with upstream (it won't change)
- You have full control over the direction

## Branch Strategy

### Main Branches
- **`main`**: Your stable production branch (based on archived original)
- **`develop`**: Your integration branch for ongoing development
- **`feature/*`**: Individual feature branches

## Current Setup

```bash
origin    → https://github.com/nexageapps/AnimatedDrawings.git (your fork - ACTIVE)
upstream  → https://github.com/facebookresearch/AnimatedDrawings.git (archived - READ-ONLY)
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
**NOT NEEDED** - Original repo is archived and won't receive updates.

If you ever want to check the archived state:
```bash
git fetch upstream
```

### Promoting to Main (Production Release)
```bash
# When develop is stable and ready for release
git checkout main
git merge develop
git push origin main

# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
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

- Keep `main` as your stable release branch
- Do all development in `feature/*` branches
- Merge features into `develop` for testing
- Promote `develop` to `main` when ready for release
- Use descriptive branch names: `feature/api-integration`, `fix/animation-bug`
- Commit often with clear messages
- Consider semantic versioning for releases (v1.0.0, v1.1.0, etc.)

## Your Advantages

Since the original is archived:
- You can make breaking changes without worrying about upstream conflicts
- You own the roadmap and feature direction
- No need to maintain compatibility with upstream updates
- Your fork becomes the canonical version for your use case
