#!/usr/bin/env python3
"""
Verification script for Athar Image Designer Swarm
Checks that all components are properly configured and ready for deployment
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print result"""
    exists = Path(filepath).exists()
    symbol = "✓" if exists else "✗"
    print(f"  {symbol} {description}: {filepath}")
    return exists

def check_agent_structure(agent_name):
    """Check if an agent has all required files"""
    print(f"\n{agent_name}:")
    base = Path(agent_name)
    
    checks = [
        (base / "__init__.py", "__init__.py"),
        (base / f"{agent_name}.py", f"{agent_name}.py"),
        (base / "instructions.md", "instructions.md"),
        (base / "tools", "tools directory"),
    ]
    
    all_good = all(check_file_exists(path, desc) for path, desc in checks)
    
    # Check for tools
    tools_dir = base / "tools"
    if tools_dir.exists():
        tool_files = list(tools_dir.glob("*.py"))
        tool_files = [f for f in tool_files if f.name != "__init__.py"]
        if tool_files:
            print(f"  ✓ Found {len(tool_files)} tool(s)")
            for tool in tool_files:
                print(f"    - {tool.name}")
        else:
            print(f"  ✗ No tools found in {tools_dir}")
            all_good = False
    
    return all_good

def main():
    print("=" * 60)
    print("ATHAR IMAGE DESIGNER SWARM - BUILD VERIFICATION")
    print("=" * 60)
    
    # Check core files
    print("\n📋 Core Files:")
    core_files = [
        ("agency.py", "Main agency file"),
        ("requirements.txt", "Dependencies"),
        (".env.template", "Environment template"),
        ("shared_instructions.md", "Shared instructions"),
        ("agencii.json", "Deployment config"),
        ("deployment.sh", "Deployment script"),
        ("README.md", "README"),
        ("DEPLOYMENT_GUIDE.md", "Deployment guide"),
        ("PROJECT_SUMMARY.md", "Project summary"),
    ]
    
    core_ok = all(check_file_exists(path, desc) for path, desc in core_files)
    
    # Check agents
    print("\n🤖 Agent Structures:")
    agents = [
        "brief_agent",
        "art_direction_agent", 
        "nb_image_agent",
        "qa_agent",
        "export_agent"
    ]
    
    agents_ok = all(check_agent_structure(agent) for agent in agents)
    
    # Try to import agency
    print("\n🔍 Import Test:")
    try:
        from agency import create_agency
        agency = create_agency()
        print(f"  ✓ Agency imports successfully")
        print(f"  ✓ Agency name: {agency.name}")
        print(f"  ✓ Number of agents: {len(agency.agents)}")
        import_ok = True
    except Exception as e:
        print(f"  ✗ Failed to import agency: {e}")
        import_ok = False
    
    # Check environment variables
    print("\n🔑 Environment Variables:")
    env_vars = [
        "OPENAI_API_KEY",
        "KIE_API_KEY",
        "KIE_API_BASE",
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "GDRIVE_FOLDER_ID"
    ]
    
    env_file = Path(".env")
    if env_file.exists():
        print(f"  ✓ .env file exists")
        with open(env_file) as f:
            content = f.read()
            for var in env_vars:
                if f"{var}=" in content and len(content.split(f"{var}=")[1].split("\n")[0].strip()) > 0:
                    print(f"  ✓ {var} is set")
                else:
                    print(f"  ⚠ {var} is not set (required for operation)")
    else:
        print(f"  ⚠ .env file not found (use .env.template to create)")
    
    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_checks = [
        ("Core files", core_ok),
        ("Agent structures", agents_ok),
        ("Import test", import_ok),
    ]
    
    for check_name, result in all_checks:
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check_name}: {'PASS' if result else 'FAIL'}")
    
    if all(result for _, result in all_checks):
        print("\n✨ BUILD VERIFICATION: SUCCESS")
        print("The Athar Image Designer Swarm is ready for deployment!")
        print("\nNext steps:")
        print("1. Add API keys to .env (copy from .env.template)")
        print("2. Run: python3 agency.py")
        print("3. Or deploy to agencii.ai (see DEPLOYMENT_GUIDE.md)")
        return 0
    else:
        print("\n❌ BUILD VERIFICATION: FAILED")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
