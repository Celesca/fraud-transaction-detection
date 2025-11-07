"""
FastAPI Fraud Detection Service
Endpoints:
  POST /predict - Accept transaction and return fraud prediction
  GET /frauds - Retrieve all transactions predicted as fraudulent
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import sqlite3
import json
import os

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="REST API for real-time fraud detection and fraud transaction retrieval",
    version="1.0.0"
)

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "frauds.db")


# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================

class Transaction(BaseModel):
    """
    Input schema for a single transaction.
    Adjust fields to match your actual dataset columns.
    """
    transaction_id: Optional[str] = Field(None, description="Unique transaction identifier")
    time_ind: str = Field(..., description="Transaction timestamp or time index")
    src_acc: str = Field(..., description="Source account identifier")
    dst_acc: str = Field(..., description="Destination account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    # Add any other features your model requires (e.g., merchant_id, device_id, etc.)
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "time_ind": "2025-11-07T10:30:00",
                "src_acc": "acc_001",
                "dst_acc": "acc_999",
                "amount": 1500.50
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for /predict endpoint"""
    transaction_id: Optional[str]
    is_fraud: bool = Field(..., description="Fraud prediction (True/False)")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Fraud probability score")
    prediction_time: str = Field(..., description="ISO timestamp of prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "is_fraud": True,
                "fraud_probability": 0.87,
                "prediction_time": "2025-11-07T10:30:15"
            }
        }


class FraudTransaction(BaseModel):
    """Schema for stored fraud transactions"""
    id: int
    transaction_id: Optional[str]
    transaction_data: dict
    fraud_probability: float
    prediction_time: str


# ============================================================================
# Database Functions
# ============================================================================

def init_db():
    """Initialize SQLite database and create frauds table if not exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frauds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            transaction_data TEXT,
            fraud_probability REAL,
            prediction_time TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_fraud_to_db(transaction: Transaction, probability: float, prediction_time: str):
    """Save a fraudulent transaction to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO frauds (transaction_id, transaction_data, fraud_probability, prediction_time)
        VALUES (?, ?, ?, ?)
    """, (
        transaction.transaction_id,
        json.dumps(transaction.dict()),
        probability,
        prediction_time
    ))
    conn.commit()
    conn.close()


def get_all_frauds() -> List[FraudTransaction]:
    """Retrieve all fraudulent transactions from the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, transaction_id, transaction_data, fraud_probability, prediction_time FROM frauds")
    rows = cursor.fetchall()
    conn.close()
    
    frauds = []
    for row in rows:
        frauds.append(FraudTransaction(
            id=row[0],
            transaction_id=row[1],
            transaction_data=json.loads(row[2]),
            fraud_probability=row[3],
            prediction_time=row[4]
        ))
    return frauds


# ============================================================================
# Model Placeholder (Replace with your trained model)
# ============================================================================

class FraudDetectionModel:
    """
    Mock fraud detection model.
    Replace this with your actual trained model (e.g., scikit-learn, XGBoost, TensorFlow).
    """
    
    def __init__(self):
        # TODO: Load your trained model here
        # Example: self.model = joblib.load('path/to/model.pkl')
        self.model = None
        print("⚠️  Mock model loaded. Replace with actual trained model.")
    
    def predict(self, transaction: Transaction) -> tuple[bool, float]:
        """
        Predict fraud for a given transaction.
        
        Args:
            transaction: Transaction object with features
            
        Returns:
            (is_fraud: bool, probability: float)
        """
        # TODO: Replace this mock logic with actual model inference
        # Example:
        # features = self._extract_features(transaction)
        # prob = self.model.predict_proba(features)[0][1]
        # is_fraud = prob >= 0.5
        # return is_fraud, prob
        
        # Mock logic: flag as fraud if amount > 5000
        mock_probability = min(transaction.amount / 10000, 0.99)
        is_fraud = mock_probability >= 0.5
        
        return is_fraud, mock_probability
    
    def _extract_features(self, transaction: Transaction):
        """
        Extract and transform features for model input.
        TODO: Implement your feature engineering pipeline here.
        """
        # Example feature extraction:
        # - Parse time_ind to datetime features (hour, day_of_week, etc.)
        # - Encode categorical variables (src_acc, dst_acc)
        # - Apply scaling/normalization
        # - Return feature vector in the format your model expects
        pass


# Initialize model (global instance)
model = FraudDetectionModel()


# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    init_db()
    print("✅ Database initialized")
    print(f"📂 Database path: {DB_PATH}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Fraud Detection API is running",
        "version": "1.0.0",
        "endpoints": [
            "POST /predict - Predict fraud for a transaction",
            "GET /frauds - Retrieve all fraudulent transactions",
            "GET /docs - Interactive API documentation"
        ]
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Transaction):
    """
    Predict whether a transaction is fraudulent.
    
    Args:
        transaction: Transaction data with required features
        
    Returns:
        PredictionResponse with fraud prediction and probability
    """
    try:
        # Get prediction from model
        is_fraud, fraud_probability = model.predict(transaction)
        
        # Current timestamp
        prediction_time = datetime.utcnow().isoformat()
        
        # If fraud detected, save to database
        if is_fraud:
            save_fraud_to_db(transaction, fraud_probability, prediction_time)
        
        return PredictionResponse(
            transaction_id=transaction.transaction_id,
            is_fraud=is_fraud,
            fraud_probability=round(fraud_probability, 4),
            prediction_time=prediction_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/frauds", response_model=List[FraudTransaction])
async def get_frauds():
    """
    Retrieve all transactions that were predicted as fraudulent.
    
    Returns:
        List of fraudulent transactions with prediction details
    """
    try:
        frauds = get_all_frauds()
        return frauds
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ============================================================================
# Run Instructions (for development only)
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
