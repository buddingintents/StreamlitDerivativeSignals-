#!/usr/bin/env python3
"""
Setup script for Perplexity API Streamlit Application
"""

import os
import sys
import hashlib
import json
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'services',
        'models',
        'pages',
        'utils',
        '.streamlit'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_default_config():
    """Create default configuration files"""
    
    # Create default credentials
    default_password = "admin123"
    password_hash = hashlib.sha256(default_password.encode()).hexdigest()
    
    credentials = {
        "username": "admin",
        "password": password_hash
    }
    
    with open('data/credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✅ Created default credentials (admin/{default_password})")
    
    # Create API config template
    api_config = {
        "api_key": "",
        "base_url": "https://api.perplexity.ai",
        "default_model": "sonar-pro",
        "default_max_tokens": 1000,
        "default_temperature": 0.7
    }
    
    with open('data/config.json', 'w') as f:
        json.dump(api_config, f, indent=2)
    
    print("✅ Created API configuration template")

def install_dependencies():
    """Install Python dependencies"""
    try:
        import subprocess
        print("📦 Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up Perplexity API Streamlit Application...")
    
    # Create directories
    create_directories()
    
    # Create default configuration
    create_default_config()
    
    # Install dependencies
    if '--install-deps' in sys.argv:
        install_dependencies()
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your Perplexity API key in data/config.json or .streamlit/secrets.toml")
    print("2. Run the application: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("4. Login with username: admin, password: admin123")

if __name__ == "__main__":
    main()
