# OneLead Testing Framework & Validation Strategy

## Testing Pyramid

```
         /\
        /E2E\        (5%) - End-to-end tests
       /------\
      /  Integ \     (15%) - Integration tests
     /----------\
    / Component  \   (30%) - Component tests
   /--------------\
  /   Unit Tests   \ (50%) - Unit tests
 /------------------\
```

## Test Structure

### 1. Unit Tests

#### Model Tests
```python
# tests/unit/models/test_opportunity_predictor.py
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
from src.models.opportunity_predictor import OpportunityPredictor

class TestOpportunityPredictor:
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003'],
            'revenue': [100000, 200000, 150000],
            'contract_value': [50000, 75000, 60000],
            'service_count': [3, 5, 4],
            'risk_score': [0.2, 0.5, 0.3]
        })
    
    @pytest.fixture
    def predictor(self):
        """Create predictor instance"""
        return OpportunityPredictor()
    
    def test_initialization(self, predictor):
        """Test model initialization"""
        assert predictor.model is not None
        assert predictor.scaler is not None
        assert predictor.label_encoder is not None
    
    def test_feature_preparation(self, predictor, sample_data):
        """Test feature preparation"""
        features = predictor.prepare_features(sample_data)
        assert isinstance(features, pd.DataFrame)
        assert len(features) == len(sample_data)
        assert all(col in features.columns for col in predictor.feature_columns)
    
    def test_prediction_output_format(self, predictor, sample_data):
        """Test prediction output format"""
        predictions = predictor.predict_opportunity_propensity(sample_data)
        assert 'predicted_opportunity' in predictions.columns
        assert 'confidence_score' in predictions.columns
        assert len(predictions) == len(sample_data)
    
    def test_model_training_with_insufficient_data(self, predictor):
        """Test model behavior with insufficient training data"""
        small_data = pd.DataFrame({'feature1': [1, 2], 'target': [0, 1]})
        with pytest.raises(ValueError, match="Insufficient data"):
            predictor.train_model(small_data)
    
    @patch('src.models.opportunity_predictor.joblib.dump')
    def test_model_saving(self, mock_dump, predictor, sample_data):
        """Test model saving functionality"""
        predictor.save_model('test_model.pkl')
        mock_dump.assert_called_once()
    
    def test_prediction_probabilities(self, predictor, sample_data):
        """Test that prediction probabilities sum to 1"""
        predictions = predictor.predict_opportunity_propensity(sample_data)
        prob_columns = [col for col in predictions.columns if col.startswith('prob_')]
        if prob_columns:
            prob_sums = predictions[prob_columns].sum(axis=1)
            np.testing.assert_array_almost_equal(prob_sums, np.ones(len(predictions)))
```

#### Data Processing Tests
```python
# tests/unit/data_processing/test_feature_engineering.py
import pytest
import pandas as pd
import numpy as np
from src.data_processing.feature_engineering import FeatureEngineer

class TestFeatureEngineering:
    
    @pytest.fixture
    def engineer(self):
        return FeatureEngineer()
    
    @pytest.fixture
    def raw_data(self):
        return pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003'],
            'revenue': [100000, 200000, None],
            'contract_date': ['2024-01-01', '2024-02-01', '2024-03-01'],
            'service_type': ['Type_A', 'Type_B', 'Type_A']
        })
    
    def test_missing_value_handling(self, engineer, raw_data):
        """Test missing value imputation"""
        processed = engineer.handle_missing_values(raw_data)
        assert processed['revenue'].isna().sum() == 0
    
    def test_feature_scaling(self, engineer, raw_data):
        """Test feature scaling"""
        scaled = engineer.scale_features(raw_data[['revenue']].fillna(0))
        assert scaled.mean().abs().max() < 1e-7  # Close to 0
        assert abs(scaled.std() - 1.0).max() < 0.1  # Close to 1
    
    def test_categorical_encoding(self, engineer, raw_data):
        """Test categorical variable encoding"""
        encoded = engineer.encode_categorical(raw_data)
        assert 'service_type_encoded' in encoded.columns
        assert encoded['service_type_encoded'].dtype in ['int64', 'float64']
    
    def test_date_features(self, engineer, raw_data):
        """Test date feature extraction"""
        date_features = engineer.extract_date_features(raw_data)
        assert 'contract_year' in date_features.columns
        assert 'contract_month' in date_features.columns
        assert 'contract_dayofweek' in date_features.columns
```

### 2. Integration Tests

```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from src.api.app import app
import json

class TestAPIIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def valid_prediction_request(self):
        return {
            "customer_id": "C001",
            "revenue": 150000,
            "contract_value": 75000,
            "service_count": 4
        }
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_prediction_endpoint_valid_request(self, client, valid_prediction_request):
        """Test prediction with valid request"""
        response = client.post(
            "/predict",
            json=valid_prediction_request
        )
        assert response.status_code == 200
        result = response.json()
        assert "prediction" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
    
    def test_prediction_endpoint_invalid_request(self, client):
        """Test prediction with invalid request"""
        invalid_request = {"customer_id": "C001"}  # Missing required fields
        response = client.post("/predict", json=invalid_request)
        assert response.status_code == 422
    
    def test_batch_prediction_endpoint(self, client):
        """Test batch prediction endpoint"""
        batch_request = {
            "customers": [
                {"customer_id": "C001", "revenue": 100000},
                {"customer_id": "C002", "revenue": 200000}
            ]
        }
        response = client.post("/batch_predict", json=batch_request)
        assert response.status_code == 200
        results = response.json()
        assert len(results["predictions"]) == 2
    
    @pytest.mark.parametrize("endpoint,method", [
        ("/predict", "POST"),
        ("/batch_predict", "POST"),
        ("/metrics", "GET")
    ])
    def test_authentication_required(self, client, endpoint, method):
        """Test that endpoints require authentication"""
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        assert response.status_code == 401  # Unauthorized
```

### 3. End-to-End Tests

```python
# tests/e2e/test_ml_pipeline.py
import pytest
import pandas as pd
from src.data_processing.data_loader import DataLoader
from src.data_processing.feature_engineering import FeatureEngineer
from src.models.opportunity_predictor import OpportunityPredictor
from src.services.prediction import PredictionService

class TestMLPipeline:
    
    @pytest.fixture
    def sample_input_file(self, tmp_path):
        """Create a sample input file"""
        df = pd.DataFrame({
            'customer_id': [f'C{i:03d}' for i in range(100)],
            'revenue': np.random.uniform(50000, 500000, 100),
            'contract_value': np.random.uniform(25000, 250000, 100)
        })
        file_path = tmp_path / "test_data.csv"
        df.to_csv(file_path, index=False)
        return file_path
    
    def test_complete_ml_pipeline(self, sample_input_file):
        """Test complete ML pipeline from data loading to prediction"""
        # Load data
        loader = DataLoader()
        raw_data = loader.load_csv(sample_input_file)
        assert len(raw_data) == 100
        
        # Engineer features
        engineer = FeatureEngineer()
        features = engineer.transform(raw_data)
        assert len(features) == len(raw_data)
        
        # Train model
        predictor = OpportunityPredictor()
        predictor.train_model(features)
        assert predictor.model is not None
        
        # Make predictions
        service = PredictionService(predictor)
        predictions = service.predict_batch(features)
        assert len(predictions) == len(features)
        assert all(col in predictions.columns for col in ['prediction', 'confidence'])
    
    def test_model_reproducibility(self, sample_input_file):
        """Test that model produces consistent results"""
        loader = DataLoader()
        data = loader.load_csv(sample_input_file)
        
        # Train two models with same data and seed
        predictor1 = OpportunityPredictor(random_state=42)
        predictor1.train_model(data)
        predictions1 = predictor1.predict_opportunity_propensity(data)
        
        predictor2 = OpportunityPredictor(random_state=42)
        predictor2.train_model(data)
        predictions2 = predictor2.predict_opportunity_propensity(data)
        
        # Predictions should be identical
        pd.testing.assert_frame_equal(predictions1, predictions2)
```

### 4. Performance Tests

```python
# tests/performance/test_model_performance.py
import pytest
import time
import pandas as pd
import numpy as np
from src.models.opportunity_predictor import OpportunityPredictor

class TestModelPerformance:
    
    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for performance testing"""
        n_samples = 10000
        return pd.DataFrame({
            'customer_id': [f'C{i:05d}' for i in range(n_samples)],
            'revenue': np.random.uniform(50000, 500000, n_samples),
            'contract_value': np.random.uniform(25000, 250000, n_samples),
            'service_count': np.random.randint(1, 10, n_samples)
        })
    
    def test_prediction_latency(self, large_dataset):
        """Test prediction latency requirements"""
        predictor = OpportunityPredictor()
        
        # Single prediction
        single_row = large_dataset.iloc[:1]
        start_time = time.time()
        predictor.predict_opportunity_propensity(single_row)
        latency = (time.time() - start_time) * 1000  # ms
        
        assert latency < 100, f"Single prediction latency {latency}ms exceeds 100ms SLA"
    
    def test_batch_prediction_throughput(self, large_dataset):
        """Test batch prediction throughput"""
        predictor = OpportunityPredictor()
        
        batch_size = 1000
        batch = large_dataset.iloc[:batch_size]
        
        start_time = time.time()
        predictions = predictor.predict_opportunity_propensity(batch)
        duration = time.time() - start_time
        
        throughput = batch_size / duration
        assert throughput > 100, f"Throughput {throughput} predictions/sec below 100/sec requirement"
    
    def test_memory_usage(self, large_dataset):
        """Test memory usage during prediction"""
        import tracemalloc
        
        predictor = OpportunityPredictor()
        
        tracemalloc.start()
        predictor.predict_opportunity_propensity(large_dataset)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 500, f"Peak memory usage {peak_mb}MB exceeds 500MB limit"
```

## Test Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
    --strict-markers
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
```

### conftest.py
```python
# tests/conftest.py
import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/1",
        "model_path": "/tmp/test_models",
        "log_level": "DEBUG"
    }

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_mlflow(monkeypatch):
    """Mock MLflow for testing"""
    import mlflow
    monkeypatch.setattr(mlflow, "log_metric", lambda *args, **kwargs: None)
    monkeypatch.setattr(mlflow, "log_param", lambda *args, **kwargs: None)
    monkeypatch.setattr(mlflow, "log_artifact", lambda *args, **kwargs: None)
```

## Validation Framework

### Model Validation
```python
# src/validation/model_validator.py
class ModelValidator:
    
    def validate_model_performance(self, model, test_data, test_labels):
        """Comprehensive model validation"""
        metrics = {}
        
        # Performance metrics
        predictions = model.predict(test_data)
        metrics['accuracy'] = accuracy_score(test_labels, predictions)
        metrics['precision'] = precision_score(test_labels, predictions, average='weighted')
        metrics['recall'] = recall_score(test_labels, predictions, average='weighted')
        metrics['f1'] = f1_score(test_labels, predictions, average='weighted')
        
        # Statistical tests
        metrics['ks_statistic'] = self.calculate_ks_statistic(test_labels, predictions)
        metrics['psi'] = self.calculate_psi(test_labels, predictions)
        
        # Business metrics
        metrics['business_value'] = self.calculate_business_value(predictions)
        
        return metrics
    
    def validate_data_quality(self, data):
        """Validate data quality"""
        issues = []
        
        # Check for missing values
        missing_pct = data.isnull().sum() / len(data)
        if (missing_pct > 0.1).any():
            issues.append("High missing value percentage")
        
        # Check for outliers
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            q1 = data[col].quantile(0.25)
            q3 = data[col].quantile(0.75)
            iqr = q3 - q1
            outliers = ((data[col] < q1 - 3*iqr) | (data[col] > q3 + 3*iqr)).sum()
            if outliers > len(data) * 0.05:
                issues.append(f"High outlier percentage in {col}")
        
        return issues
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run linting
      run: |
        flake8 src tests
        black --check src tests
        mypy src
    
    - name: Run unit tests
      run: pytest tests/unit -v --cov=src
    
    - name: Run integration tests
      run: pytest tests/integration -v
    
    - name: Run e2e tests
      run: pytest tests/e2e -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Performance tests
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      run: pytest tests/performance -v
```

## Test Execution Commands

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m performance

# Run with coverage
pytest --cov=src --cov-report=html

# Run with parallel execution
pytest -n auto

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/models/test_opportunity_predictor.py

# Run tests matching pattern
pytest -k "test_prediction"

# Generate test report
pytest --html=report.html --self-contained-html
```