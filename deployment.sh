#!/bin/bash

# Deployment script for Athar Image Designer Swarm
# Compatible with agencii.ai dashboard deployment

set -e

echo "🚀 Deploying Athar Image Designer Swarm..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.template..."
    cp .env.template .env
    echo "📝 Please update .env with your API keys before deployment."
fi

# Check for required environment variables
echo "🔍 Checking environment variables..."
source .env

required_vars=("OPENAI_API_KEY" "KIE_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables: ${missing_vars[*]}"
    echo "Please set these in your .env file before deployment."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "import agency_swarm; print(f'Agency Swarm version: {agency_swarm.__version__}')"

# Test agency creation
echo "🧪 Testing agency creation..."
python -c "from agency import create_agency; agency = create_agency(); print('✅ Agency created successfully')"

# Build for production
echo "🏗️  Building for production..."
# Agency Swarm handles FastAPI setup automatically via main.py

echo "✅ Deployment preparation complete!"
echo ""
echo "To run locally:"
echo "  python main.py"
echo ""
echo "To deploy to agencii.ai:"
echo "  Use the agencii CLI or dashboard to deploy this directory"
echo ""
echo "Required environment variables:"
echo "  - OPENAI_API_KEY (required)"
echo "  - KIE_API_KEY (required)"
echo "  - KIE_API_BASE (optional, defaults to https://api.kie.ai/api/v1)"
echo "  - GOOGLE_SERVICE_ACCOUNT_JSON (required for export)"
echo "  - GDRIVE_FOLDER_ID (required for export)"
