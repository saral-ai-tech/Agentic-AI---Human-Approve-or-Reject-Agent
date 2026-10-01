#!/usr/bin/env python3
"""
Quick validation script to check that all modules import correctly.
Run this to verify the project structure is sound before running the app.
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Check that all modules can be imported without errors."""
    modules = [
        "config",
        "utils",
        "prompts",
        "tools",
        "models",
        "llm",
        "nodes",
        "graph",
    ]
    
    print("🔍 Checking module imports...")
    print()
    
    failed = []
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            failed.append((module_name, e))
    
    print()
    if failed:
        print(f"❌ {len(failed)} module(s) failed to import:")
        for module_name, error in failed:
            print(f"   - {module_name}: {error}")
        return False
    else:
        print("✅ All modules imported successfully!")
        return True

def check_dependencies():
    """Check that required packages are installed."""
    packages = [
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("langchain_anthropic", "LangChain Anthropic"),
        ("dotenv", "python-dotenv"),
    ]
    
    print("🔍 Checking external dependencies...")
    print()
    
    failed = []
    for package_name, display_name in packages:
        try:
            __import__(package_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} not installed")
            failed.append(package_name)
    
    print()
    if failed:
        print(f"❌ {len(failed)} package(s) missing. Install with:")
        print(f"   pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def check_env():
    """Check if .env file exists."""
    from pathlib import Path
    
    print("🔍 Checking configuration...")
    print()
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file exists")
        return True
    elif env_example.exists():
        print("⚠️  .env file not found, but .env.example exists")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your credentials")
        return True
    else:
        print("❌ Neither .env nor .env.example found")
        return False

def main():
    """Run all checks."""
    print("=" * 50)
    print("Human-in-the-Loop Agent - Project Validation")
    print("=" * 50)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Modules", check_imports),
        ("Configuration", check_env),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
        print()
    
    print("=" * 50)
    if all_passed:
        print("✅ All checks passed! Ready to run:")
        print("   python run.py")
        print("   OR")
        print("   streamlit run app.py")
    else:
        print("❌ Some checks failed. See above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
