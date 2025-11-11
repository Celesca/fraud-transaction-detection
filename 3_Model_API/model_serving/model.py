from typing import Tuple, Dict, Any, Optional
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FraudDetectionModel:
    """Thin model wrapper. Replace or extend as needed.

    By default the constructor will attempt to load `models/xgb_model.joblib`.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        # Resolve model path relative to this file's directory
        if model_path is None:
            # Default: look for xgb_model.joblib in ../models/ (parent of model_serving/)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(parent_dir, "models", "xgb_model.joblib")
        
        self.model_path = model_path
        self.model = None
        self._has_proba = False
        self._is_xgb_booster = False

        # Auto-load if path exists
        if model_path and os.path.exists(model_path):
            try:
                self.load(model_path)
            except Exception:
                # keep fallback behavior
                self.model = None

    def load(self, path: str) -> None:

        obj = joblib.load(path)
        self.model = obj
        # detect capabilities
        self._has_proba = hasattr(self.model, "predict_proba")

        try:
            import xgboost as xgb

            if isinstance(self.model, xgb.Booster):
                self._is_xgb_booster = True
        except Exception:
            # xgboost not installed or not a booster; ignore
            self._is_xgb_booster = False

        self.model_path = path

    def _to_dataframe(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Normalize input features to a single-row DataFrame."""
        if isinstance(features, pd.DataFrame):
            return features.reset_index(drop=True)
        # assume mapping-like
        return pd.DataFrame([features])

    def predict(self, features: Dict[str, Any]) -> Tuple[bool, float]:
        """Return (is_fraud, probability).

        Tries the loaded model (if any). Falls back to a simple heuristic if no
        model is available or an error occurs.
        """
        # Require a loaded model — do not fall back to a heuristic anymore.
        if self.model is None:
            raise RuntimeError("No model loaded")

        # Log that model-based prediction will run (only when a model is present)
        logger.debug("Running model-based prediction")
        try:
            df = self._to_dataframe(features)

            if self._has_proba:
                probs = self.model.predict_proba(df)
                if probs.ndim == 2 and probs.shape[1] >= 2:
                    prob = float(probs[0, 1])
                else:
                    prob = float(probs.ravel()[0])
                is_fraud = prob >= 0.5
                return bool(is_fraud), float(prob)

            if self._is_xgb_booster:
                import xgboost as xgb 

                dmat = xgb.DMatrix(df.values, feature_names=list(df.columns))
                preds = self.model.predict(dmat)
                prob = float(preds[0])
                is_fraud = prob >= 0.5
                return bool(is_fraud), float(prob)

            # generic predict: could return probability or class
            preds = self.model.predict(df)
            # numpy array-like
            if isinstance(preds, (np.ndarray, list, tuple)):
                val = preds[0]
                try:
                    prob = float(val)
                except Exception:
                    prob = 1.0 if int(val) == 1 else 0.0
                is_fraud = prob >= 0.5
                return bool(is_fraud), float(prob)

            return self._heuristic_predict(features)

        except Exception:
            # Log the exception and re-raise so the API surface returns an error.
            logging.getLogger(__name__).exception("Model prediction failed")
            raise

    # Heuristic fallback removed by design. If no model is loaded or prediction
    # fails an exception will be raised so the calling service can handle it.

    def predict_from_transaction(self, transaction: BaseModel) -> Tuple[bool, float]:
        """Helper to accept a pydantic transaction model or raw dict."""
        if hasattr(transaction, "dict"):
            data = transaction.dict()
        else:
            data = dict(transaction)
        return self.predict(data)
