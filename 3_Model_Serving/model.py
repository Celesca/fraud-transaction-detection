"""Model wrapper for fraud prediction.
Loads a joblib-serialized model (XGBoost/sklearn) by default from
`models/xgb_model.joblib` and exposes a unified predict interface.

The wrapper is defensive: if loading fails it falls back to the
existing simple amount-based heuristic so the API remains usable.
"""
from typing import Tuple, Dict, Any, Optional
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import numpy as np


class FraudDetectionModel:
    """Thin model wrapper. Replace or extend as needed.

    By default the constructor will attempt to load `models/xgb_model.joblib`.
    """

    def __init__(self, model_path: Optional[str] = "models/xgb_model.joblib") -> None:
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
        # If no model loaded: fallback heuristic
        if self.model is None:
            return self._heuristic_predict(features)

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

            # xgboost native Booster
            if self._is_xgb_booster:
                import xgboost as xgb  # type: ignore

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

            # last-resort fallback
            return self._heuristic_predict(features)

        except Exception:
            # Do not crash the API on model errors; fall back to heuristic
            return self._heuristic_predict(features)

    def _heuristic_predict(self, features: Dict[str, Any]) -> Tuple[bool, float]:
        """Original amount-based heuristic used as a safe fallback."""
        amount = features.get("amount")
        try:
            amount = float(amount)
        except Exception:
            amount = 0.0

        prob = min(amount / 10000.0, 0.99) if amount and amount > 0 else 0.01
        is_fraud = prob >= 0.5
        return bool(is_fraud), float(prob)

    def predict_from_transaction(self, transaction: BaseModel) -> Tuple[bool, float]:
        """Helper to accept a pydantic transaction model or raw dict."""
        if hasattr(transaction, "dict"):
            data = transaction.dict()
        else:
            data = dict(transaction)
        return self.predict(data)
