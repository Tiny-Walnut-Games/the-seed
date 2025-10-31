# Repository Safety & Best Practices Guide

**Last Updated:** 2025  
**Audience:** Solo developers working on The Seed project  
**Purpose:** Maintain a healthy, performant repository without Git LFS

---

## What We've Implemented

### 1. Enhanced `.gitignore` (Large File Protection)

Your `.gitignore` now includes strict protections against:

#### Binary Media (Game Assets)
- **Images**: `.png`, `.jpg`, `.gif`, `.bmp`, `.psd`, `.ai`, `.svg` (except docs)
- **3D Models**: `.fbx`, `.blend`, `.obj`, `.glb`, `.gltf`
- **Audio**: `.wav`, `.mp3`, `.ogg`, `.flac`, `.aac`
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

#### Code & Build Artifacts
- **Compiled code**: `.exe`, `.dll`, `.so`, `.dylib`, `.o`, `.a`, `.class`, `.jar`
- **Build outputs**: `build/`, `dist/`, `*.whl`, `*.egg`
- **Node modules**: `node_modules/`, `*.lock` files (package managers)
- **Python packages**: `.eggs/`, `.tox/`, `.nox/`

#### Data Files (No LFS)
- **Databases**: `.db`, `.sqlite`, `.sqlite3`
- **ML Models**: `.h5`, `.keras`, `.pth`, `.pt`, `.onnx`, `.pkl`, `.safetensors`
- **Archives**: `.zip`, `.7z`, `.rar`, `.tar.gz`

#### Unity-Specific
- **Build directories**: `/Library/`, `/Temp/`, `/Obj/`, `/Build/`
- **Meta files**: `*.meta` (unless explicitly tracked)
- **Generated code**: `.sln`, `.csproj`, `.unityproj`

### 2. New `.gitattributes` (Line Ending & Binary Handling)

Ensures:
- **Text files use LF** (Unix-style line endings) for consistency
- **Binary files marked correctly** so Git doesn't try to merge them
- **Proper diff strategies** for config files
- **No unexpected CRLF conversions** that could break shell scripts

---

## ⚠️ Important: Alternative Asset Storage

Since you're not using Git LFS, **you need an external system for game assets**:

### Recommended Approaches (Pick One)

#### Option 1: OneDrive / Google Drive (Free, Simple)
```
your-cloud-drive/
├── the-seed-assets/
│   ├── sprites/
│   ├── audio/
│   ├── models/
│   └── README.md (with sync instructions)
```
- Add `.gitignore` entry: `/Assets/Raw/` → sync manually before build
- **Pros**: Free, simple, no setup
- **Cons**: Manual sync, version tracking is basic

#### Option 2: GitHub Releases (Free for Bundles)
```
Release v0.1-assets
├── sprites-pack.zip
├── audio-pack.zip
└── models-pack.zip
```
- Upload as GitHub Release artifact
- Download during build/setup
- **Pros**: Versioned, tied to code releases
- **Cons**: Upload limits, not automatic

#### Option 3: Dedicated Artifact Server
- MinIO (self-hosted S3-like)
- Supabase Storage
- AWS S3 (minimal cost)

**For now**, I recommend **OneDrive approach** for solo dev simplicity.

---

## Safe Workflow: Preventing Accidents

### 1. **Pre-Commit Hook Setup** (Recommended)

Create `.git/hooks/pre-commit` (Windows: use Git Bash or WSL):

```bash
#!/bin/bash
# Prevent commits of large files

# Size limit: 10MB (adjust as needed)
SIZE_LIMIT=10485760

echo "🔍 Checking for large files..."

# Check staged files
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt "$SIZE_LIMIT" ]; then
            echo "❌ BLOCKED: $file is $(($size / 1024 / 1024))MB (limit: $(($SIZE_LIMIT / 1024 / 1024))MB)"
            exit 1
        fi
    fi
done

# Check for accidentally staged binary files
UNSAFE_EXTENSIONS="\.zip$|\.exe$|\.dll$|\.so$|\.mp4$|\.png$|\.blend$"
if git diff --cached --name-only | grep -E "$UNSAFE_EXTENSIONS"; then
    echo "⚠️  WARNING: Binary files detected in staging area"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

exit 0
```

### 2. **One-Time Setup** (After Pulling)

```powershell
# Windows (PowerShell)
$hookContent = @"
#!/bin/bash
SIZE_LIMIT=10485760

git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt "$SIZE_LIMIT" ]; then
            echo "❌ BLOCKED: $file is too large"
            exit 1
        fi
    fi
done
"@

New-Item -Path ".git/hooks" -ItemType Directory -Force
Set-Content -Path ".git/hooks/pre-commit" -Value $hookContent -Encoding UTF8
```

### 3. **Verify Your Commits Before Pushing**

```bash
# See what you're about to push
git diff --stat origin/main..HEAD

# Check largest files in staging
git ls-files --stage | awk '{print $4}' | xargs ls -lhS | head -20

# See total repo size
du -sh .git/
```

---

## 🚨 If You Accidentally Committed Large Files

### Immediate (Before Pushing)

```bash
# Option 1: Undo last commit (keep changes)
git reset --soft HEAD~1

# Option 2: Undo last commit (discard changes)
git reset --hard HEAD~1

# Option 3: Remove file from last commit (keep commit)
git rm --cached <large-file>
git commit --amend -m "Previous commit message"
```

### After Pushing (Harder to Fix)

```bash
# Nuclear option: Use git-filter-branch or BFG Repo-Cleaner
# This rewrites history - coordinate with any collaborators!

# Install BFG: https://rtyley.github.io/bfg-repo-cleaner/
bfg --delete-files <large-file> .

# Then force push
git push origin --force-with-lease
```

⚠️ **Force pushing rewrites history. Coordinate with team first!**

---

## Best Practices for Solo Dev

### 1. **Keep Your Local Clone Clean**

```powershell
# Weekly maintenance
git gc --aggressive
git prune
```

### 2. **Regular Backup**

```powershell
# Full backup (includes all history)
Copy-Item -Path ".git" -Destination "D:\backups\seed-git-$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### 3. **Monitor Repo Size**

```bash
# See what's taking space
git rev-list --all --objects | sort -k 2 | tail -30

# Find largest commits
git rev-list --all | while read rev; do
    echo "$(git cat-file -s $rev) $rev"
done | sort -n | tail -10
```

### 4. **Document Asset Locations**

Create `ASSETS.md`:

```markdown
# Asset Storage Guide

## Location
All game assets stored in: **OneDrive:/Tiny_Walnut_Games/seed-assets**

## Structure
- `sprites/` - Character and UI sprites (PNG)
- `audio/` - Sound effects and music (OGG, MP3)
- `models/` - 3D models and animations (FBX, BLEND)
- `fonts/` - Custom fonts (TTF, OTF)

## Sync Process
1. Before build: Download latest from OneDrive
2. After adding assets: Upload to OneDrive with timestamp
3. Update `ASSETS.md` with what's new

## Tools
- OneDrive Desktop App (auto-sync)
- Or manual: rclone, rsync, or robocopy
```

### 5. **Smart `.gitignore` Exceptions**

If you need small versions (thumbnails, samples):

```gitignore
# Ignore all PNG
*.png

# BUT include thumbnails in docs
!docs/screenshots/*.png
!docs/reference/*.png

# Ignore all video
*.mp4

# BUT include demo clips under 5MB
!docs/tutorials/clips/*.mp4
```

---

## Daily Workflow Checklist

Before committing:

- [ ] **Size check**: `git add` only source code and configs
- [ ] **Extension check**: No `.zip`, `.exe`, `.mp4`, `.blend` in staging
- [ ] **Review**: `git diff --cached` to see exactly what's staged
- [ ] **Verify**: `git status` shows no surprise large files

Before pushing:

- [ ] **Local test**: `git log --oneline` last 5 commits look correct
- [ ] **Size review**: `git ls-files --stage | sort -k 2` no large files
- [ ] **Fetch first**: `git fetch origin` to check for conflicts
- [ ] **Push carefully**: `git push --dry-run` then `git push`

---

## Troubleshooting

### "I see a huge `.blob` file in `.git/objects`"
**Cause**: Previously committed large file  
**Fix**: Use BFG Repo-Cleaner to remove it from history

### "Clone takes forever"
**Cause**: Large files in git history  
**Fix**: Check `git rev-list --all --objects | sort -k 2 | tail -20`

### "My push rejected - 'file too large'"
**Cause**: Git hook (if enabled) or GitHub limits  
**Fix**: Remove file before committing (see "If You Accidentally Committed")

### "Line endings changed on every file?"
**Cause**: `.gitattributes` not applied  
**Fix**: 
```bash
git add --renormalize .
git commit -m "Fix line endings"
```

---

## Community Standards for Solo Dev

✅ **DO**:
- Commit frequently (small, logical changes)
- Write clear commit messages
- Use branches for experimental features
- Document your setup
- Backup `.git` directory regularly
- Review commits before pushing

❌ **DON'T**:
- Commit build artifacts (unless intentional)
- Mix whitespace changes with logic changes
- Rewrite public history (force push)
- Ignore warnings from Git hooks
- Let `.git` grow beyond 1GB

---

## Resources

- [Git Attributes Reference](https://git-scm.com/docs/gitattributes)
- [GitHub's Gitignore Collection](https://github.com/github/gitignore)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git Hook Guide](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

---

**Questions?** Check your commit before pushing! 🚀