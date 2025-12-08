#!/bin/bash
# One-command deployment to HuggingFace

echo "🦜 Warbler CDA - HuggingFace Deployment"
echo "======================================="
echo ""

# Check if HF CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "Installing huggingface_hub..."
    pip install huggingface_hub
fi

# Check if logged in
if ! huggingface-cli whoami &> /dev/null; then
    echo ""
    echo "Please login to HuggingFace:"
    huggingface-cli login
fi

# Get Space name
if [ -z "$1" ]; then
    echo ""
    read -p "Enter your HuggingFace Space name (e.g., username/warbler-cda): " SPACE_NAME
else
    SPACE_NAME=$1
fi

echo ""
echo "Deploying to: $SPACE_NAME"
echo ""

# Upload to Space
cd warbler-cda-package || exit 1

huggingface-cli upload "$SPACE_NAME" . \
    --repo-type=space \
    --commit-message="Deploy Warbler CDA v0.1.0"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your Space is live at:"
    echo "   https://huggingface.co/spaces/$SPACE_NAME"
    echo ""
    echo "It may take a few minutes to build. Check the Space page for status."
else
    echo ""
    echo "❌ Deployment failed. Check the error messages above."
    exit 1
fi
