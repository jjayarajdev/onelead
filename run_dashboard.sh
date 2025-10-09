#!/bin/bash

# OneLead Dashboard Launcher

echo "🎯 OneLead Sales Intelligence Platform"
echo "=========================================="
echo ""
echo "Select dashboard version:"
echo ""
echo "  1) Premium Intelligence Dashboard - NEW & RECOMMENDED ⭐"
echo "     → World-class design with actionable insights"
echo "     → Perfect for executive presentations and daily use"
echo ""
echo "  2) Business Story Dashboard"
echo "     → Narrative-driven, tells you what to do"
echo "     → Perfect for sales teams and executives"
echo ""
echo "  3) Enhanced Data Dashboard"
echo "     → Detailed analytics and filtering"
echo "     → For data analysts and power users"
echo ""
echo "  4) Basic Dashboard"
echo "     → Simple tables and charts"
echo "     → For quick data access"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Premium Intelligence Dashboard..."
        echo "World-class design with AI-powered insights"
        echo "Opening http://localhost:8501 in your browser..."
        streamlit run src/app/dashboard_premium.py
        ;;
    2)
        echo ""
        echo "🚀 Launching Business Story Dashboard..."
        echo "This version tells you the story behind the numbers"
        echo "Opening http://localhost:8501 in your browser..."
        streamlit run src/app/dashboard_business.py
        ;;
    3)
        echo ""
        echo "🚀 Launching Enhanced Dashboard..."
        echo "Opening http://localhost:8501 in your browser..."
        streamlit run src/app/dashboard_v2.py
        ;;
    4)
        echo ""
        echo "🚀 Launching Basic Dashboard..."
        echo "Opening http://localhost:8501 in your browser..."
        streamlit run src/app/dashboard.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
