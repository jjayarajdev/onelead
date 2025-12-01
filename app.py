"""
OneLead - Streamlit Cloud Entry Point
Main application file for deployment to https://oneleads.streamlit.app/
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

# Import and run the Three-Category Lead System with Account Filter
from src.app.onelead_complete_backup import main

if __name__ == "__main__":
    main()
