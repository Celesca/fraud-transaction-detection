from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import os
import logging

from model_serving.schemas import Transaction, PredictionResponse, FraudTransaction
import model_serving.db as db
from model_serving.model import FraudDetectionModel
import model_serving.preprocessing as preprocessing

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

        logger.info(
            "Received transaction for prediction: dst_acc=%s amount=%s",
            transaction.dst_acc,
            transaction.amount,
        )

        # Transform incoming transaction to model-ready features (DataFrame)
        features_df = preprocessing.transform_transaction(transaction.dict(), artifacts)

        # Short-circuit: if the transaction type is not one of the two
        # high-risk channels we care about (CASH_OUT, TRANSFER), skip the model
        # and immediately mark as non-fraudulent.
        try:
            tt = getattr(transaction, "transac_type", None)
            if tt is None:
                tt_val = None
            else:
                # handle Enum members
                tt_val = getattr(tt, "value", None) or str(tt)
            if isinstance(tt_val, str):
                tt_val = tt_val.strip().upper()
        except Exception:
            tt_val = None

        if tt_val not in ("CASH_OUT", "TRANSFER"):
            logger.info("Transaction transac_type=%s not high-risk; skipping model (marking not fraud)", tt_val)
            is_fraud = False
            fraud_probability = 0.0
        else:
            # Model inference: model.predict accepts DataFrame or dict
            is_fraud, fraud_probability = model.predict(features_df)

        prediction_time = datetime.utcnow().isoformat()

        # Persist if fraud
        if is_fraud:
            db.save_fraud_to_db(transaction.dict(), fraud_probability, prediction_time)
            logger.info("Persisted fraud record with prob=%.4f", fraud_probability)

        logger.info("Prediction result: is_fraud=%s prob=%.4f", is_fraud, fraud_probability)

        return PredictionResponse(
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
