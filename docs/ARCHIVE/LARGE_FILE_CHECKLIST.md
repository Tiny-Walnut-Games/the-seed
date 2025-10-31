# Large File Safety Checklist

Quick reference for keeping your repo lean and safe.

---

## 🔍 **BEFORE COMMITTING**

```bash
# See what you're about to commit
git status

# Check staged files - should see only .py, .md, .json, .yaml, etc.
git diff --name-only --cached

# Check file sizes of staged files
git diff --cached --name-only | xargs ls -lh

# STOP if you see any of these extensions:
# .png .jpg .mp4 .avi .exe .dll .zip .db .blend .fbx .wav .mp3
# → Use Ctrl+C and unstage the file
```

---

## 🚫 **NEVER COMMIT**

| Type | Extensions | Why |
|------|-----------|-----|
| Images | `.png`, `.jpg`, `.gif`, `.psd`, `.ai` | Binary, use OneDrive |
| 3D Models | `.fbx`, `.blend`, `.obj`, `.glb` | Very large files |
| Audio | `.wav`, `.mp3`, `.ogg`, `.flac` | High bitrate, stream instead |
| Video | `.mp4`, `.avi`, `.mov`, `.mkv` | Huge files |
| Executables | `.exe`, `.dll`, `.so`, `.jar` | Build artifacts |
| Databases | `.db`, `.sqlite`, `.sqlite3` | Data, not code |
| Archives | `.zip`, `.7z`, `.rar` | Redundant storage |
| ML Models | `.pth`, `.h5`, `.onnx`, `.pkl` | Huge weights |

---

## ✅ **DO COMMIT**

- `.py` - Python source
- `.md` - Documentation  
- `.json`, `.yaml`, `.toml` - Config
- `.js`, `.ts`, `.cs` - Code
- `.txt`, `.rst` - Text docs
- `.sh`, `.ps1` - Scripts
- `.gitignore`, `.gitattributes` - Git config

---

## 🛑 **IF YOU ALREADY COMMITTED A LARGE FILE**

### **Before pushing** (easy fix):

```bash
# See your recent commits
git log --oneline -10

# Undo last commit, keep changes
git reset --soft HEAD~1

# Or undo and discard
git reset --hard HEAD~1

# Or remove file from last commit
git rm --cached <filename>
git commit --amend --no-edit
```

### **After pushing** (harder, rewrites history):

```bash
# Option 1: Use BFG Repo-Cleaner (download: https://rtyley.github.io/bfg-repo-cleaner/)
bfg --delete-files <filename> .

# Option 2: Git native (slower)
git filter-branch --tree-filter 'rm -f <filename>' -- --all

# Then:
git push origin --force-with-lease
```

⚠️ **Force pushing changes history. Back up `.git/` first!**

---

## 📊 **MONITOR REPO HEALTH**

```bash
# Total repo size
du -sh .git/

# Largest files currently tracked
git ls-files -z | xargs -0 du -h | sort -hr | head -20

# Largest objects ever committed
git rev-list --all --objects | sort -k 2 | tail -20

# Largest commits
git log --pretty=format:"%H %s" --reverse | while read hash msg; do
    echo "$(git cat-file -s $hash | numfmt --to=iec) - $msg"
done | sort -hr | head -10
```

---

## 🔧 **QUICK COMMANDS**

```bash
# Check if file is ignored
git check-ignore -v <filename>

# Stage only code files
git add *.py *.md *.json

# Preview what you're committing
git diff --stat --cached

# Unstage everything
git reset

# Unstage specific file
git reset <filename>

# See what's in staging
git ls-files --stage

# Clean up local repo
git gc --aggressive
```

---

## 🎯 **DAILY WORKFLOW**

```bash
# 1. Make changes to source code only
nano script.py

# 2. Stage your changes
git add script.py

# 3. Review before commit
git diff --cached

# 4. Commit with clear message
git commit -m "Feature: Add script validation"

# 5. Before push, verify
git log -1 --name-status
git diff --stat HEAD~1

# 6. Push safely
git push
```

---

## 📍 **WHERE TO STORE LARGE FILES**

### **Game Assets** → OneDrive (linked in ASSETS.md)
- Sprites, 3D models, audio, video
- Sync before build, upload after changes

### **Code Assets** → GitHub (under 100MB total)
- Source code, configs, documentation
- Everything in this repo

### **Build Artifacts** → Ignored
- Use `.gitignore` to prevent accidental commits
- Rebuild locally as needed

---

## ⚠️ **RED FLAGS**

Stop and unstage if you see:

- [ ] File size > 10MB
- [ ] File extension in NEVER COMMIT list
- [ ] `node_modules/` directory
- [ ] `/Library/` or `/Build/` directory (Unity)
- [ ] Database files (`.db`, `.sqlite`)
- [ ] Compressed archives (`.zip`, `.rar`)

---

## 💡 **TIPS**

✨ Use `.gitignore` exceptions carefully:
```gitignore
# Block all images
*.png

# Except small docs/screenshots
!docs/screenshots/*.png
```

✨ Verify file is ignored:
```bash
git status
# If file doesn't appear → it's ignored ✓
```

✨ Create `.gitattributes` exceptions only for essential files:
```
!important.pdf export-ignore
```

---

**Need help?** Check `.github/REPO_SAFETY_GUIDE.md` for detailed instructions.