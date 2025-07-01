#!/usr/bin/env python3
"""
Configuration Helper for Bitbucket MCP Server

This script helps you find the correct configuration for Claude Desktop
and tests that everything is set up correctly.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def find_python_path():
    """Find the Python executable path"""
    # Try different common Python locations
    python_paths = [
        sys.executable,  # Current Python being used
        subprocess.check_output(['which', 'python3']).decode().strip(),
        subprocess.check_output(['which', 'python']).decode().strip(),
        '/usr/bin/python3',
        '/usr/local/bin/python3',
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for path in python_paths:
        if path and path not in seen:
            seen.add(path)
            unique_paths.append(path)
    
    return unique_paths

def test_imports():
    """Test that required modules can be imported"""
    required_modules = ['fastmcp', 'httpx', 'dotenv']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing")
            missing_modules.append(module)
    
    return missing_modules

def test_environment():
    """Test environment variables"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['BITBUCKET_USERNAME', 'BITBUCKET_APP_PASSWORD', 'BITBUCKET_WORKSPACE']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} - Set")
        else:
            print(f"❌ {var} - Missing")
            missing_vars.append(var)
    
    return missing_vars

def generate_config():
    """Generate Claude Desktop configuration"""
    python_paths = find_python_path()
    current_dir = Path.cwd().absolute()
    server_script = current_dir / "mcp_server.py"  # Updated for new structure
    
    print(f"\n🔧 Recommended Claude Desktop Configuration:")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {python_paths[0]}")
    print(f"Server script: {server_script}")
    
    config = {
        "mcpServers": {
            "bitbucket": {
                "command": str(python_paths[0]),
                "args": [str(server_script)],
                "env": {
                    "BITBUCKET_USERNAME": "your_username",
                    "BITBUCKET_APP_PASSWORD": "your_app_password",
                    "BITBUCKET_WORKSPACE": "your_workspace"
                }
            }
        }
    }
    
    print("\n📋 Configuration JSON:")
    print(json.dumps(config, indent=2))
    
    print(f"\n📍 Claude Desktop config file locations:")
    print(f"  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print(f"  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")

def main():
    print("🧪 Bitbucket MCP Server Configuration Helper")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Find all Python paths
    print(f"\n🔍 Available Python paths:")
    try:
        paths = find_python_path()
        for i, path in enumerate(paths):
            print(f"  {i+1}. {path}")
    except Exception as e:
        print(f"❌ Error finding Python paths: {e}")
        return
    
    # Test module imports
    print(f"\n📦 Testing required modules:")
    missing_modules = test_imports()
    
    if missing_modules:
        print(f"\n❌ Missing modules. Install with:")
        print(f"   pip install {' '.join(missing_modules)}")
        return
    
    # Test environment variables
    print(f"\n🔐 Testing environment variables:")
    missing_vars = test_environment()
    
    if missing_vars:
        print(f"\n❌ Missing environment variables. Create .env file with:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
    
    # Test server import
    print(f"\n🖥️  Testing server import:")
    try:
        from mcp_server import mcp  # Updated import for new structure
        print("✅ Server imports successfully")
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return
    
    # Generate configuration
    generate_config()
    
    print(f"\n🎉 Configuration helper complete!")
    print(f"📋 Next steps:")
    print(f"   1. Copy the configuration JSON above")
    print(f"   2. Add it to your Claude Desktop config file")
    print(f"   3. Update the environment variables with your actual values")
    print(f"   4. Restart Claude Desktop")

if __name__ == "__main__":
    main()
