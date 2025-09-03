"""
HPE OneLead Opportunity Prediction Model
ML models for predicting customer propensity and opportunity scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class OpportunityPredictor:
    """ML model for predicting HPE customer opportunity propensity"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.is_trained = False
        
    def prepare_training_data(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data with synthetic labels based on business rules"""
        
        # Create synthetic target labels based on business logic
        # This simulates having historical opportunity outcomes
        features = features_df.copy()
        
        # Create more balanced synthetic labels using multiple criteria
        # Use rank-based scoring to ensure distribution
        
        scores = pd.Series(0.0, index=features.index)
        
        # Add scores based on various features
        if 'urgency_score' in features.columns and features['urgency_score'].std() > 0:
            scores += features['urgency_score'].rank(pct=True) * 2
        
        if 'eol_urgency_score' in features.columns and features['eol_urgency_score'].std() > 0:
            scores += features['eol_urgency_score'].rank(pct=True) * 2
        
        if 'has_active_opportunities' in features.columns:
            scores += features['has_active_opportunities'].astype(int) * 1.5
        
        if 'total_opportunities' in features.columns and features['total_opportunities'].std() > 0:
            scores += features['total_opportunities'].rank(pct=True) * 1
        
        if 'total_products' in features.columns and features['total_products'].std() > 0:
            scores += features['total_products'].rank(pct=True) * 0.5
        
        # Create balanced labels based on score distribution
        score_q33 = scores.quantile(0.33)
        score_q66 = scores.quantile(0.66)
        
        high_propensity_conditions = scores >= score_q66
        medium_propensity_conditions = (scores >= score_q33) & (scores < score_q66)
        
        # Force balanced distribution for training
        # Sort scores and assign labels evenly
        sorted_indices = scores.sort_values(ascending=False).index
        n_total = len(features)
        n_high = max(1, n_total // 3)
        n_medium = max(1, n_total // 3)
        
        labels = pd.Series('Low', index=features.index)
        labels.loc[sorted_indices[:n_high]] = 'High'
        labels.loc[sorted_indices[n_high:n_high+n_medium]] = 'Medium'
        
        # Convert to numpy array for consistency
        labels = labels.values
        
        target = pd.Series(labels, name='opportunity_label')
        
        return features, target
    
    def select_features(self, features_df: pd.DataFrame) -> List[str]:
        """Select relevant features for model training"""
        
        # Key business features for opportunity prediction
        feature_candidates = [
            # Urgency indicators
            'urgency_score', 'eol_urgency_score', 'eos_urgency_score',
            
            # Customer engagement
            'rfm_score', 'recency_score', 'frequency_score', 'monetary_score',
            
            # Product and service diversity
            'platform_diversity', 'practice_diversity', 'opportunity_product_lines',
            
            # Historical performance
            'project_success_rate', 'total_projects', 'avg_project_size',
            
            # Contract and service metrics
            'avg_credit_utilization', 'avg_delivery_rate', 'total_contracts',
            
            # Current status
            'has_active_opportunities', 'recent_engagement',
            'contract_renewal_urgency', 'low_utilization_risk',
            
            # Volume metrics
            'total_products', 'total_opportunities', 'successful_projects'
        ]
        
        # Filter to only include available features
        available_features = [f for f in feature_candidates if f in features_df.columns]
        
        # Add numeric features if not in the list above
        numeric_features = features_df.select_dtypes(include=[np.number]).columns
        for feature in numeric_features:
            if feature not in available_features and feature != 'customer_id':
                available_features.append(feature)
        
        self.feature_columns = available_features
        return available_features
    
    def train_model(self, features_df: pd.DataFrame, use_synthetic_labels: bool = True):
        """Train the opportunity prediction model"""
        
        if use_synthetic_labels:
            X, y = self.prepare_training_data(features_df)
        else:
            # If you have actual historical labels, use them
            X = features_df
            y = features_df['actual_opportunity_outcome']  # This would come from historical data
        
        # Select features
        feature_cols = self.select_features(X)
        X_features = X[feature_cols].fillna(0)
        
        # Encode target labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Check if we have enough samples for stratified split
        min_class_count = min(np.bincount(y_encoded))
        
        if len(X_features) < 20 or min_class_count < 2:
            # Too few samples for proper train/test split, use all data for training
            logger.warning(f"Limited data: {len(X_features)} samples. Using simplified training approach.")
            X_train, X_test = X_features, X_features
            y_train, y_test = y_encoded, y_encoded
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = X_train_scaled
        else:
            # Normal train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_features, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        logger.info("Training opportunity prediction model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Model training complete. Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")
        
        # Cross-validation (adjust folds based on data size)
        n_samples = len(X_train_scaled)
        n_folds = min(5, n_samples) if n_samples >= 5 else 2
        
        if n_samples >= n_folds:
            try:
                cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=n_folds)
                logger.info(f"Cross-validation ({n_folds}-fold) accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            except:
                logger.warning("Cross-validation failed due to insufficient data")
                cv_scores = np.array([train_score])
        else:
            logger.warning(f"Insufficient data for cross-validation (only {n_samples} samples)")
            cv_scores = np.array([train_score])
        
        # Predictions for detailed evaluation
        y_pred = self.model.predict(X_test_scaled)
        
        # Classification report
        class_names = self.label_encoder.classes_
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=class_names))
        
        self.is_trained = True
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_scores': cv_scores,
            'feature_importance': self.get_feature_importance()
        }
    
    def predict_opportunity_propensity(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Predict opportunity propensity for customers"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare features
        X = features_df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # Convert predictions back to labels
        predicted_labels = self.label_encoder.inverse_transform(predictions)
        
        # Create results DataFrame
        results = features_df.copy()
        results['predicted_propensity'] = predicted_labels
        
        # Add probability scores for each class
        class_names = self.label_encoder.classes_
        for i, class_name in enumerate(class_names):
            results[f'prob_{class_name.lower()}'] = probabilities[:, i]
        
        # Overall confidence score (max probability)
        results['prediction_confidence'] = probabilities.max(axis=1)
        
        return results
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores from the trained model"""
        
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = dict(zip(self.feature_columns, self.model.feature_importances_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def get_top_opportunities(self, features_df: pd.DataFrame, n: int = 50, 
                            min_confidence: float = 0.6) -> pd.DataFrame:
        """Get top opportunities ranked by predicted propensity and confidence"""
        
        predictions = self.predict_opportunity_propensity(features_df)
        
        # Filter by confidence and focus on High/Medium propensity
        high_confidence = predictions[
            (predictions['prediction_confidence'] >= min_confidence) &
            (predictions['predicted_propensity'].isin(['High', 'Medium']))
        ].copy()
        
        # Create composite score for ranking
        high_confidence['composite_score'] = (
            high_confidence['prob_high'] * 0.6 +
            high_confidence['prob_medium'] * 0.3 +
            high_confidence['prediction_confidence'] * 0.1
        )
        
        # Sort by composite score and return top N
        top_opportunities = high_confidence.nlargest(n, 'composite_score')
        
        return top_opportunities
    
    def generate_opportunity_insights(self, customer_data: pd.DataFrame) -> Dict:
        """Generate actionable insights for HPE consultants"""
        
        predictions = self.predict_opportunity_propensity(customer_data)
        
        insights = {
            'total_customers': len(predictions),
            'high_propensity_count': len(predictions[predictions['predicted_propensity'] == 'High']),
            'medium_propensity_count': len(predictions[predictions['predicted_propensity'] == 'Medium']),
            'low_propensity_count': len(predictions[predictions['predicted_propensity'] == 'Low']),
        }
        
        # High urgency opportunities (immediate action needed)
        urgent_filter = (predictions['predicted_propensity'] == 'High')
        if 'urgency_score' in predictions.columns:
            urgent_filter &= (predictions['urgency_score'] >= 3)
        urgent_opps = predictions[urgent_filter]
        insights['urgent_opportunities'] = len(urgent_opps)
        
        # Cross-sell opportunities (high diversity potential)
        cross_sell_filter = predictions['predicted_propensity'].isin(['High', 'Medium'])
        
        # Look for platform diversity column (it might have a different name)
        platform_col = None
        for col in predictions.columns:
            if 'platform' in col.lower() and 'diversity' in col.lower():
                platform_col = col
                break
        
        if platform_col:
            cross_sell_filter &= (predictions[platform_col] <= 2)
        
        cross_sell_opps = predictions[cross_sell_filter]
        insights['cross_sell_opportunities'] = len(cross_sell_opps)
        
        # Renewal opportunities (contract/product lifecycle)
        renewal_filter = pd.Series(False, index=predictions.index)
        if 'eol_urgency_score' in predictions.columns:
            renewal_filter |= (predictions['eol_urgency_score'] >= 2)
        if 'contract_renewal_urgency' in predictions.columns:
            renewal_filter |= (predictions['contract_renewal_urgency'] == 1)
        
        renewal_opps = predictions[renewal_filter]
        insights['renewal_opportunities'] = len(renewal_opps)
        
        # Service expansion opportunities (low utilization)
        service_filter = predictions['predicted_propensity'].isin(['High', 'Medium'])
        if 'low_utilization_risk' in predictions.columns:
            service_filter &= (predictions['low_utilization_risk'] == 1)
        
        service_expansion_opps = predictions[service_filter]
        insights['service_expansion_opportunities'] = len(service_expansion_opps)
        
        return insights
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")