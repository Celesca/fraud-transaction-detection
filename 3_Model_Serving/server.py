from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import os
import logging

from schemas import Transaction, PredictionResponse, FraudTransaction
import db
from model import FraudDetectionModel
import preprocessing


app = FastAPI(
    title="Fraud Detection API",
    description="REST API for real-time fraud detection and fraud transaction retrieval",
    version="1.0.0",
)

# Configure a module logger
logger = logging.getLogger("fraud_api")
if not logger.handlers:
    # simple console handler if not configured by uvicorn
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


DB_PATH = os.path.join(os.path.dirname(__file__), "frauds.db")

@app.on_event("startup")
async def startup_event():
    """Initialize database, load preprocessing artifacts and the model on startup."""
    # Initialize DB
    try:
        db.init_db()
        logger.info("Database initialized at %s", DB_PATH)
    except Exception:
        logger.exception("Failed to initialize database")

    # Load preprocessing artifacts (may be None if not present)
    try:
        artifacts = preprocessing.load_preprocessing_artifacts()
        logger.info("Preprocessing artifacts loaded: %s", "yes" if artifacts else "no")
    except Exception:
        artifacts = None
        logger.exception("Failed to load preprocessing artifacts")

    # Instantiate model (constructor may auto-load default path)
    model = FraudDetectionModel()
    # If model not loaded, try explicit load to capture errors in logs
    if model.model is None and model.model_path:
        try:
            model.load(model.model_path)
            logger.info("Model loaded from %s", model.model_path)
        except Exception:
            logger.exception("Failed to load model from %s", model.model_path)
    else:
        logger.info("Model loaded: %s", "yes" if model.model is not None else "no")

    # Attach to app.state for handlers to access
    app.state.artifacts = artifacts
    app.state.model = model


@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API is running",
        "version": "1.0.0",
        "endpoints": ["POST /predict", "GET /frauds", "DELETE /frauds", "GET /docs"],
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Transaction):
    try:
        artifacts = getattr(app.state, "artifacts", None)
        model: FraudDetectionModel = getattr(app.state, "model")

        logger.info("Received transaction for prediction: transaction_id=%s dst_acc=%s amount=%s",
                    transaction.transaction_id, transaction.dst_acc, transaction.amount)

        # Transform incoming transaction to model-ready features (DataFrame)
        features_df = preprocessing.transform_transaction(transaction.dict(), artifacts)

        # Model inference: model.predict accepts DataFrame or dict
        is_fraud, fraud_probability = model.predict(features_df)

        prediction_time = datetime.utcnow().isoformat()

        # Persist if fraud
        if is_fraud:
            db.save_fraud_to_db(transaction.dict(), fraud_probability, prediction_time)
            logger.info("Persisted fraud: transaction_id=%s prob=%.4f",
                        transaction.transaction_id, fraud_probability)

        logger.info("Prediction result: transaction_id=%s is_fraud=%s prob=%.4f",
                    transaction.transaction_id, is_fraud, fraud_probability)

        return PredictionResponse(
            transaction_id=transaction.transaction_id,
            is_fraud=is_fraud,
            fraud_probability=round(fraud_probability, 4),
            prediction_time=prediction_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")


@app.get("/frauds", response_model=List[FraudTransaction])
async def get_frauds():
    try:
        records = db.get_all_frauds()
        return [FraudTransaction(**r) for r in records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.delete("/frauds")
async def clear_frauds():
    try:
        deleted = db.clear_frauds()
        return {"message": f"Deleted {deleted} fraud records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
