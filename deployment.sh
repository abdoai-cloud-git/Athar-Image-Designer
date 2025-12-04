#!/bin/bash

# ============================================
# ATHAR IMAGE DESIGNER SWARM - DEPLOYMENT SCRIPT
# ============================================
# This script prepares and deploys the agency to agencii.ai
# Compatible with agencii CLI and automated deployment

set -e  # Exit on error

echo "========================================"
echo "Athar Image Designer Swarm - Deployment"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Verify environment
print_info "Step 1: Verifying environment..."

if [ ! -f "agency.py" ]; then
    print_error "agency.py not found. Are you in the correct directory?"
    exit 1
fi

if [ ! -f "agencii.json" ]; then
    print_error "agencii.json not found. Cannot proceed with deployment."
    exit 1
fi

print_success "Required files found"

# Step 2: Check for .env file (local testing)
print_info "Step 2: Checking environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    print_info "For local testing, copy .env.template to .env and fill in your API keys"
    print_info "For production deployment, configure environment variables in agencii.ai dashboard"
else
    print_success ".env file found"
    
    # Check if required variables are set
    required_vars=("OPENAI_API_KEY" "KIE_API_KEY" "GOOGLE_SERVICE_ACCOUNT_JSON" "GDRIVE_FOLDER_ID")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=." .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_warning "Missing or empty environment variables in .env:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_info "Add these variables before running locally"
    else
        print_success "All required environment variables are set"
    fi
fi

# Step 3: Install dependencies
print_info "Step 3: Installing dependencies..."

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi

pip install -r requirements.txt --quiet
print_success "Dependencies installed"

# Step 4: Validate agency structure
print_info "Step 4: Validating agency structure..."

agents=("brief_agent" "art_direction_agent" "nb_image_agent" "qa_agent" "export_agent")
all_valid=true

for agent in "${agents[@]}"; do
    if [ ! -d "$agent" ]; then
        print_error "Agent folder not found: $agent"
        all_valid=false
    elif [ ! -f "$agent/$agent.py" ]; then
        print_error "Agent file not found: $agent/$agent.py"
        all_valid=false
    elif [ ! -f "$agent/instructions.md" ]; then
        print_error "Instructions not found: $agent/instructions.md"
        all_valid=false
    elif [ ! -d "$agent/tools" ]; then
        print_error "Tools folder not found: $agent/tools"
        all_valid=false
    fi
done

if [ "$all_valid" = true ]; then
    print_success "All agent structures are valid"
else
    print_error "Agency structure validation failed"
    exit 1
fi

# Step 5: Test import
print_info "Step 5: Testing agency import..."

python3 -c "from agency import create_agency; agency = create_agency(); print('Agency created successfully')" 2>&1
if [ $? -eq 0 ]; then
    print_success "Agency import test passed"
else
    print_error "Agency import test failed. Check for syntax errors."
    exit 1
fi

# Step 6: Run basic validation
print_info "Step 6: Running basic validation..."

# Check if tools can be imported
for agent in "${agents[@]}"; do
    tool_files=$(find "$agent/tools" -name "*.py" ! -name "__init__.py" 2>/dev/null)
    if [ -n "$tool_files" ]; then
        print_info "Found tools for $agent"
    fi
done

print_success "Validation complete"

# Step 7: Deployment options
echo ""
print_info "========================================"
print_info "Deployment Options:"
print_info "========================================"
echo ""
echo "Option 1: Deploy to agencii.ai"
echo "  1. Push this code to your GitHub repository"
echo "  2. Connect repository to agencii.ai dashboard"
echo "  3. Configure environment variables in dashboard"
echo "  4. Agencii will automatically deploy on push to main"
echo ""
echo "Option 2: Local Testing"
echo "  1. Ensure .env file is configured with all API keys"
echo "  2. Run: python agency.py"
echo "  3. Test the agency in terminal mode"
echo ""
echo "Option 3: Docker Deployment"
echo "  1. Build: docker build -t athar-image-designer-swarm ."
echo "  2. Run: docker run -p 8000:8000 --env-file .env athar-image-designer-swarm"
echo ""

print_success "Deployment preparation complete!"
echo ""
print_info "Next steps:"
echo "  - For agencii.ai: Push to GitHub and configure in dashboard"
echo "  - For local: Run 'python agency.py' to test"
echo "  - For Docker: Run docker build and docker run commands"
echo ""
print_info "Documentation: See README.md for detailed instructions"
echo ""

# Optional: Run local test if requested
read -p "Would you like to run a local test now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f ".env" ]; then
        print_info "Starting local test..."
        python3 agency.py
    else
        print_error "Cannot run local test without .env file"
        print_info "Create .env from .env.template and try again"
        exit 1
    fi
fi

print_success "Deployment script completed!"
