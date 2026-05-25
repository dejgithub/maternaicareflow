#!/bin/bash
# MaternAI CareFlow - Unix Setup Script
set -e

echo "======================================"
echo "  MaternAI CareFlow - Setup Script"
echo "======================================"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python: $(python3 --version)"
    PYTHON=python3
elif command -v python &> /dev/null; then
    echo "✓ Python: $(python --version)"
    PYTHON=python
else
    echo "✗ Python not found. Please install Python 3.10+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✓ Node.js: $(node --version)"
else
    echo "✗ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo ""
echo "Setting up Backend..."
cd backend
$PYTHON -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
fi
cd ..

echo ""
echo "Setting up Frontend..."
cd frontend
npm install
echo "✓ Frontend dependencies installed"
cd ..

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
