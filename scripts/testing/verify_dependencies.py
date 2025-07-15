#!/usr/bin/env python3
"""
Verify dependencies and create setup instructions
"""
import sys
import subprocess
from pathlib import Path

def check_dependency_structure():
    """Check if dependency files are properly structured"""
    print("🔍 Checking dependency structure...")
    
    # Check if files exist
    files_to_check = [
        "requirements.txt",
        "requirements-dev.txt",
        "config/pyproject.toml"
    ]
    
    all_good = True
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_good = False
    
    return all_good

def parse_requirements(file_path):
    """Parse requirements file and return dependencies"""
    if not Path(file_path).exists():
        return []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-r'):
            deps.append(line)
    
    return deps

def check_requirements_consistency():
    """Check if requirements are consistent"""
    print("\n📋 Checking requirements consistency...")
    
    main_deps = parse_requirements("requirements.txt")
    dev_deps = parse_requirements("requirements-dev.txt")
    
    print(f"Main dependencies: {len(main_deps)}")
    print(f"Dev dependencies: {len(dev_deps)}")
    
    # Check for essential dependencies
    essential = [
        "fastapi>=0.110.0",
        "pytest>=8.0.0",
        "bandit[toml]>=1.7.5",
        "pydantic>=2.6.0",
        "sqlalchemy>=2.0.25"
    ]
    
    missing = []
    for dep in essential:
        dep_name = dep.split('>=')[0].split('[')[0]
        found = any(dep_name in line for line in main_deps + dev_deps)
        if not found:
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing essential dependencies: {missing}")
        return False
    else:
        print("✅ All essential dependencies found")
        return True

def generate_setup_instructions():
    """Generate setup instructions for the project"""
    print("\n📝 Generating setup instructions...")
    
    instructions = """
# 🚀 AI Teddy Bear Backend - Development Setup

## Prerequisites
- Python 3.12+
- pip (Python package manager)
- Virtual environment (recommended)

## Setup Instructions

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 2. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes testing, linting, security)
pip install -r requirements-dev.txt
```

### 3. Verify Installation
```bash
# Run basic tests
python3 simple_test_runner.py

# Run with pytest (after dependencies are installed)
pytest --cov=src --cov-report=term-missing

# Run security scan
bandit -r src/

# Run linting
ruff check src/
black --check src/
```

### 4. Environment Configuration
```bash
# Copy environment template
cp config/development.env .env

# Edit .env file with your configuration
```

## Troubleshooting

### If pip is not available:
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pip

# On macOS
brew install python3

# On Windows
Download Python from python.org (includes pip)
```

### If dependencies fail to install:
```bash
# Update pip
python3 -m pip install --upgrade pip

# Install dependencies one by one to identify issues
pip install fastapi
pip install pytest
# etc.
```
"""
    
    with open("SETUP_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Setup instructions saved to SETUP_INSTRUCTIONS.md")

def main():
    print("🧸 AI Teddy Bear - Dependency Verification")
    print("=" * 50)
    
    structure_ok = check_dependency_structure()
    consistency_ok = check_requirements_consistency()
    
    if structure_ok and consistency_ok:
        print("\n✅ Dependencies are properly configured!")
        print("✅ Task 1: Dependency Management - COMPLETED")
        generate_setup_instructions()
    else:
        print("\n❌ Dependency issues found")
        print("❌ Task 1: Dependency Management - FAILED")
        
    return structure_ok and consistency_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)