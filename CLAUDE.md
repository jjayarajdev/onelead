# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OneLead Business Intelligence & Recommendation System - A Python-based Streamlit application for business intelligence, data analysis, and machine learning recommendations.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application (when main app exists)
streamlit run src/main.py
```

### Testing & Quality
```bash
# Run tests
pytest

# Code formatting
black .

# Linting
flake8

# Type checking
mypy .
```

## Project Architecture

Based on the .gitignore structure, this project follows a data science/ML engineering pattern:

- **Data Layer**: `data/` directory with raw, processed, and output subdirectories
- **Source Code**: `src/` directory expected to contain main application logic
- **Models**: `src/models/` for ML model artifacts and training code
- **Configuration**: `config/` for environment-specific settings
- **Analysis Outputs**: `data/outputs/` for generated reports and visualizations

### Expected Directory Structure
```
onelead_system/
├── src/
│   ├── main.py              # Streamlit main application
│   ├── models/              # ML models and training scripts
│   └── data_processing/     # Data ETL and processing modules
├── data/
│   ├── raw/                 # Source data files (ignored in git)
│   ├── processed/           # Cleaned/transformed data (ignored)
│   └── outputs/             # Analysis results and visualizations
├── config/                  # Configuration files
└── logs/                    # Application logs
```

## Technology Stack

- **Framework**: Streamlit for web interface
- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn, scipy
- **Visualization**: plotly, seaborn, matplotlib
- **Data I/O**: openpyxl, xlrd for Excel files
- **Database**: SQLite (built-in)

## Data Handling

- Raw data files (CSV, Excel, JSON, DB) are git-ignored for security
- Processed data and model artifacts are cached locally but not committed
- The project handles Excel files specifically (onelead_consolidated_data_new.xlsx)

## Security Considerations

- Sensitive data files are excluded from version control
- Configuration files with secrets (production.py, secrets.py, .env) are ignored
- Streamlit secrets (secrets.toml) are not committed