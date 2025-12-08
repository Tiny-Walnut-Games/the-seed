# Warbler CDA - HuggingFace Deployment Complete Guide

## 🎯 What Was Created

A complete, production-ready Python package extracted from The Seed project, specifically designed for HuggingFace deployment.

### Package Contents

- **25 Python files** with 8,645 lines of code
- **21 core RAG/FractalStat files** from the original system
- **11 infrastructure files** for deployment
- **Package size**: 372KB (source), ~2GB with dependencies

## 🚀 Deployment Options

### Option 1: Automatic GitLab CI/CD → HuggingFace (RECOMMENDED)

This is the **kudos-worthy** automatic sync pipeline!

#### Setup (One-time)

1. **Get HuggingFace Token**
   - Go to <https://huggingface.co/settings/tokens>
   - Create a new token with "write" access
   - Copy the token

2. **Configure GitLab CI/CD**
   - Go to <https://gitlab.com/tiny-walnut-games/the-seed/-/settings/ci_cd>
   - Expand "Variables"
   - Add variable:
     - Key: `HF_TOKEN`
     - Value: (paste your HuggingFace token)
     - Masked: ✓ (checked)
   - Add variable:
     - Key: `HF_SPACE_NAME`
     - Value: `your-username/warbler-cda` (customize this)

3. **Create HuggingFace Space**
   - Go to <https://huggingface.co/new-space>
   - Name: `warbler-cda`
   - SDK: Gradio
   - Visibility: Public or Private
   - Click "Create Space"

### Deploy

#### **First: Verify paths**

```bash
# Ensure that the following is on path for most executables to be available
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Restart the terminal
source ~/.bashrc
```

#### **Method A: Tag-based (Automatic)**

```bash
git add warbler-cda-package/
git commit -m "Add Warbler CDA HuggingFace package"
git tag v0.1.0
git push origin main --tags
```

The pipeline will automatically deploy to HuggingFace! ✨

#### **Method B: Manual Trigger**

```bash
git add warbler-cda-package/
git commit -m "Add Warbler CDA HuggingFace package"
git push origin main
```

Then go to CI/CD > Pipelines and manually trigger the `deploy-huggingface` job.

#### What Happens

1. GitLab CI detects the push/tag
2. Runs the `deploy-huggingface` job
3. Installs `huggingface_hub`
4. Logs in with your token
5. Syncs `warbler-cda-package/` to your Space
6. Your Space is live! 🎉

### Option 2: Manual HuggingFace Upload

```bash
cd warbler-cda-package

# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload to Space
huggingface-cli upload your-username/warbler-cda . --repo-type=space --commit-message="Initial release"
```

### Option 3: Local Testing First

```bash
cd warbler-cda-package

# Setup
./setup.sh

# Run Gradio demo
python app.py
```

Open <http://localhost:7860> to test locally before deploying.

## 🔧 Configuration

### Environment Variables (Optional)

For the HuggingFace Space, you can set these in Space Settings:

- `OPENAI_API_KEY` - For OpenAI embeddings (optional)
- `MAX_RESULTS` - Default max results (default: 10)
- `ENABLE_FractalStat` - Enable FractalStat hybrid scoring (default: true)

### Customizing the Space

Edit `app.py` to customize:

- Sample documents
- UI layout
- Default settings
- Branding

## 📊 Features in the Demo

The Gradio demo includes:

1. **Query Tab**
   - Semantic search
   - FractalStat hybrid scoring toggle
   - Adjustable weights
   - Real-time results

2. **Add Document Tab**
   - Add custom documents
   - Set realm type/label
   - Immediate indexing

3. **System Stats Tab**
   - Performance metrics
   - Cache statistics
   - Quality distribution

4. **About Tab**
   - System documentation
   - FractalStat explanation
   - Links to resources

## 🧪 Testing the Deployment

After deployment, test these queries:

1. **Basic Semantic**: "wisdom about courage"
2. **Technical**: "how does FractalStat work"
3. **Narrative**: "ancient library keeper"
4. **Pattern**: "connections between events"

Expected results:

- 3-5 relevant documents per query
- Relevance scores > 0.6
- Sub-second response time

## 🐛 Troubleshooting

### Pipeline Fails

**Error**: "HF_TOKEN not set"

- **Fix**: Add HF_TOKEN to GitLab CI/CD variables

**Error**: "Space not found"

- **Fix**: Create the Space on HuggingFace first, or update HF_SPACE_NAME

### Space Fails to Build

**Error**: "Module not found"

- **Fix**: Check requirements.txt includes all dependencies

**Error**: "Out of memory"

- **Fix**: HuggingFace Spaces have memory limits. Consider using CPU-only versions of PyTorch

### Gradio Not Loading

**Error**: "Application startup failed"

- **Fix**: Check app.py for syntax errors
- **Fix**: Ensure all imports are correct

## 📈 Monitoring

### GitLab CI/CD

Monitor deployments at:
<https://gitlab.com/tiny-walnut-games/the-seed/-/pipelines>

### HuggingFace Space

Monitor your Space at:
<https://huggingface.co/spaces/YOUR_USERNAME/warbler-cda>

Check:

- Build logs
- Runtime logs
- Usage statistics

## 🔄 Updating the Space

### Automatic (via GitLab CI/CD)

Just push changes to main or create a new tag:

```bash
git add warbler-cda-package/
git commit -m "Update: improved query performance"
git push origin main
```

Or for versioned releases:

```bash
git tag v0.1.1
git push origin v0.1.1
```

### Manual

```bash
cd warbler-cda-package
huggingface-cli upload your-username/warbler-cda . --repo-type=space --commit-message="Update"
```

## 📚 Additional Resources

- **HuggingFace Spaces Docs**: <https://huggingface.co/docs/hub/spaces>
- **Gradio Docs**: <https://gradio.app/docs/>
- **GitLab CI/CD Docs**: <https://docs.gitlab.com/ee/ci/>

## ✅ Checklist

Before deploying:

- [ ] HF_TOKEN set in GitLab CI/CD variables
- [ ] HF_SPACE_NAME set in GitLab CI/CD variables
- [ ] HuggingFace Space created
- [ ] Package tested locally (`./setup.sh && python app.py`)
- [ ] All files committed to Git
- [ ] README.md reviewed and customized

After deploying:

- [ ] Space builds successfully
- [ ] Gradio interface loads
- [ ] Sample queries work
- [ ] Add Document feature works
- [ ] System stats display correctly

## 🎉 Success

Once deployed, your Warbler CDA Space will be live at:

**<https://huggingface.co/spaces/YOUR_USERNAME/warbler-cda>**

Share it with the world! 🌍
