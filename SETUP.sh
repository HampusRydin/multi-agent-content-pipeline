#!/bin/bash
# Quick setup script for Multi-Agent Content Pipeline
# This script helps you set up the project quickly

set -e

echo "=========================================="
echo "Multi-Agent Content Pipeline Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
        echo "   Required: SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, SERPAPI_API_KEY"
        echo ""
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Python setup
echo ""
echo "🐍 Setting up Python backend..."
cd python-agents

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Check if migrations need to be run
echo ""
echo "📊 Database Setup"
echo "Please run these SQL migrations in Supabase SQL Editor:"
echo "  1. python-agents/migrations/001_create_agent_logs.sql"
echo "  2. python-agents/migrations/002_create_posts.sql"
echo "  3. python-agents/migrations/003_add_post_id_to_agent_logs.sql"
echo ""
read -p "Have you run the migrations? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please run the migrations before starting the server"
    echo "   See python-agents/migrations/README.md for instructions"
fi

cd ..

# Next.js setup
echo ""
echo "⚛️  Setting up Next.js frontend..."
cd nextjs-app

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "✅ Node.js dependencies already installed"
fi

cd ..

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run Supabase migrations (see python-agents/migrations/README.md)"
echo "3. Start the backend:"
echo "   cd python-agents && source venv/bin/activate && python main.py"
echo "4. Start the frontend (in another terminal):"
echo "   cd nextjs-app && npm run dev"
echo ""
echo "Then visit http://localhost:3000"
echo ""

