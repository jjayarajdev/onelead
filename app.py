"""
OneLead - Streamlit Cloud Entry Point
Main application file for deployment to https://oneleads.streamlit.app/
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

# Import and run the Premium Dashboard
from src.app.dashboard_premium import main

if __name__ == "__main__":
    main()
