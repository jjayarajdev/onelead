#!/usr/bin/env python3
"""
HPE OneLead System - Batch Analysis Runner
Quick analysis script to test the system and generate insights
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_processing.data_loader import OneleadDataLoader
from data_processing.feature_engineering import OneleadFeatureEngineer
from models.opportunity_predictor import OpportunityPredictor
from consultant_tools.recommendation_engine import ConsultantRecommendationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run complete OneLead analysis pipeline"""
    
    logger.info("Starting HPE OneLead Analysis Pipeline")
    
    # 1. Load and process data
    logger.info("Step 1: Loading and processing data...")
    data_path = "data/onelead_consolidated_data_new.xlsx"
    
    try:
        loader = OneleadDataLoader(data_path)
        processed_data = loader.process_all_data()
        data_summary = loader.get_data_summary()
        
        logger.info("Data loading completed:")
        for sheet, stats in data_summary.items():
            logger.info(f"  {sheet}: {stats['records']:,} records, {stats['columns']} columns")
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return
    
    # 2. Feature engineering
    logger.info("Step 2: Engineering features...")
    
    try:
        feature_engineer = OneleadFeatureEngineer(processed_data)
        features = feature_engineer.build_feature_set()
        
        logger.info(f"Feature engineering completed: {len(features)} customers, {len(features.columns)} features")
        
        # Show top opportunities from feature engineering
        top_feature_opps = feature_engineer.get_top_opportunities(n=10)
        logger.info(f"Top 10 opportunities by feature-based scoring:")
        for idx, row in top_feature_opps.iterrows():
            logger.info(f"  Customer {row['customer_id']}: {row['propensity_tier']} propensity (score: {row['opportunity_propensity_score']:.3f})")
        
    except Exception as e:
        logger.error(f"Error in feature engineering: {e}")
        return
    
    # 3. Train predictive model
    logger.info("Step 3: Training predictive model...")
    
    try:
        predictor = OpportunityPredictor()
        training_results = predictor.train_model(features)
        
        logger.info("Model training completed:")
        logger.info(f"  Training accuracy: {training_results['train_accuracy']:.3f}")
        logger.info(f"  Test accuracy: {training_results['test_accuracy']:.3f}")
        logger.info(f"  CV accuracy: {training_results['cv_scores'].mean():.3f} (+/- {training_results['cv_scores'].std() * 2:.3f})")
        
        # Show feature importance
        feature_importance = training_results['feature_importance']
        logger.info("Top 10 most important features:")
        for i, (feature, importance) in enumerate(list(feature_importance.items())[:10]):
            logger.info(f"  {i+1}. {feature}: {importance:.4f}")
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        return
    
    # 4. Generate predictions
    logger.info("Step 4: Generating predictions...")
    
    try:
        predictions = predictor.predict_opportunity_propensity(features)
        top_ml_opportunities = predictor.get_top_opportunities(features, n=10)
        
        logger.info(f"Predictions generated for {len(predictions)} customers")
        logger.info("Top 10 ML-predicted opportunities:")
        for idx, row in top_ml_opportunities.iterrows():
            logger.info(f"  Customer {row['customer_id']}: {row['predicted_propensity']} propensity (confidence: {row['prediction_confidence']:.3f})")
        
        # Generate insights
        insights = predictor.generate_opportunity_insights(features)
        logger.info("Business insights:")
        logger.info(f"  Total customers: {insights['total_customers']:,}")
        logger.info(f"  High propensity: {insights['high_propensity_count']:,}")
        logger.info(f"  Medium propensity: {insights['medium_propensity_count']:,}")
        logger.info(f"  Urgent opportunities: {insights['urgent_opportunities']:,}")
        logger.info(f"  Renewal opportunities: {insights['renewal_opportunities']:,}")
        logger.info(f"  Cross-sell opportunities: {insights['cross_sell_opportunities']:,}")
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        return
    
    # 5. Generate consultant recommendations
    logger.info("Step 5: Generating consultant recommendations...")
    
    try:
        rec_engine = ConsultantRecommendationEngine()
        recommendations = rec_engine.batch_generate_recommendations(features, predictions, top_n=20)
        
        logger.info(f"Generated recommendations for {len(recommendations)} top customers")
        
        # Show action summary
        action_summary = rec_engine.get_action_summary(recommendations)
        logger.info("Recommended actions summary:")
        logger.info(f"  Total recommendations: {action_summary['total_recommendations']}")
        logger.info(f"  High priority actions: {action_summary['high_priority_actions']}")
        
        logger.info("Action type breakdown:")
        for action_type, count in action_summary['action_breakdown'].items():
            logger.info(f"  {action_type}: {count}")
        
        logger.info("Urgency breakdown:")
        for urgency, count in action_summary['urgency_breakdown'].items():
            logger.info(f"  {urgency}: {count}")
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return
    
    # 6. Save results
    logger.info("Step 6: Saving results...")
    
    try:
        # Save predictions
        output_path = Path("data/outputs")
        output_path.mkdir(exist_ok=True)
        
        predictions.to_csv(output_path / "customer_predictions.csv", index=False)
        top_ml_opportunities.to_csv(output_path / "top_opportunities.csv", index=False)
        recommendations.to_csv(output_path / "consultant_recommendations.csv", index=False)
        
        # Save model
        model_path = Path("src/models")
        predictor.save_model(str(model_path / "trained_opportunity_model.pkl"))
        
        logger.info(f"Results saved to {output_path}")
        logger.info(f"Model saved to {model_path}")
        
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return
    
    logger.info("HPE OneLead Analysis Pipeline completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Review the generated CSV files in data/outputs/")
    logger.info("2. Run the Streamlit dashboard: streamlit run src/main.py")
    logger.info("3. Use the consultant recommendations to prioritize customer outreach")

if __name__ == "__main__":
    main()