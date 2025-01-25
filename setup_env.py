import os
import subprocess
import sys
from pathlib import Path
import venv
import platform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_virtual_environment(venv_path):
    """Create a virtual environment."""
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        logger.info(f"Created virtual environment at {venv_path}")
        
        # Get pip path
        pip_path = venv_path / "bin" / "pip"
        
        # Upgrade pip
        logger.info("Upgrading pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        raise

def install_dependencies(venv_path):
    """Install project dependencies."""
    try:
        pip_path = venv_path / "bin" / "pip"
        
        # Install core dependencies first
        logger.info("Installing core dependencies...")
        subprocess.run([
            str(pip_path), "install", "-e", "."
        ], check=True)
        
        # Install dev dependencies separately
        logger.info("Installing development dependencies...")
        subprocess.run([
            str(pip_path), "install", 
            "pytest==8.3.4",
            "pytest-mockito==0.0.4",
            "black==24.2.0",
            "isort==5.13.0",
            "flake8==7.0.0"
        ], check=True)
        
        # Install playwright
        logger.info("Installing and setting up Playwright...")
        subprocess.run([
            str(pip_path), "install", "playwright"
        ], check=True)
        playwright_path = venv_path / "bin" / "playwright"
        subprocess.run([str(playwright_path), "install"], check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Output: {e.output if hasattr(e, 'output') else 'No output'}")
        raise

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("GROQ_API_KEY=\n")
            f.write("OLLAMA_API_TOKEN=\n")
        logger.info("Created .env file")

def main():
    """Main setup function."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 or higher is required")

        # Get project root directory
        project_root = Path(__file__).parent
        venv_path = project_root / ".venv"

        # Create virtual environment if it doesn't exist
        if not venv_path.exists():
            create_virtual_environment(venv_path)
        
        # Install dependencies
        install_dependencies(venv_path)
        
        # Create .env file
        create_env_file()
        
        logger.info("\nSetup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update the .env file with your API keys")
        logger.info("2. Activate the virtual environment:")
        logger.info("   source .venv/bin/activate")
        logger.info("3. Run the application: python -m streamlit run src/crawlgpt/ui/chat_app.py")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()