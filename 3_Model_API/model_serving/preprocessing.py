from datetime import datetime
from typing import Dict, Any, Optional
import os

import pandas as pd
import joblib
from .schemas import TRANSAC_TYPE, ALLOWED_TRANSAC_TYPES
from enum import Enum as _Enum

def parse_time_features(time_ind: str) -> Dict[str, Any]:
    try:
        dt = datetime.fromisoformat(time_ind)
    except Exception:
        try:
            dt = datetime.strptime(time_ind, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return {"hour": None, "day_of_week": None, "parsed": False}

    return {"hour": dt.hour, "day_of_week": dt.weekday(), "parsed": True}

def load_preprocessing_artifacts(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    # Resolve path relative to this file's directory if not provided
    if path is None:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(parent_dir, "models", "preprocessing_artifacts.joblib")
    
    try:
        artifacts = joblib.load(path)
        return artifacts
    except Exception:
        return None
    
# Convert incoming JSON transaction to a 1-row DataFrame ready for model inference.
def transform_transaction(transaction: Dict[str, Any], artifacts: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    
    relevant_features = [
        "transac_type",
        "amount",
        "src_bal",
        "src_new_bal",
        "dst_bal",
        "dst_new_bal",
    ]

    # Build initial df from transaction dict
    # Normalize transac_type to uppercase and validate
    tt = transaction.get("transac_type")
    if tt is not None:
        # If the incoming value is an Enum member (from Pydantic), extract its value.
        if isinstance(tt, _Enum):
            tt_val = tt.value
        else:
            tt_val = tt

        tt_norm = str(tt_val).strip().upper()
        if tt_norm not in TRANSAC_TYPE.__members__:
            raise ValueError(f"Invalid transac_type '{tt}'; allowed: {list(TRANSAC_TYPE)}")
        # store the normalized string value so later code can treat it as a category
        transaction["transac_type"] = tt_norm

    row = {k: transaction.get(k, None) for k in relevant_features}
    df = pd.DataFrame([row])

    # Ensure transac_type uses the canonical categories so dummies are consistent
    if "transac_type" in df.columns:
        # ensure category order matches training
        df["transac_type"] = pd.Categorical(df["transac_type"], categories=ALLOWED_TRANSAC_TYPES)

    # One-hot encode transac_type (drop_first=True matches training notebook)
    df = pd.get_dummies(df, columns=["transac_type"], drop_first=True)

    # Align columns to training columns 
    if artifacts and "train_cols" in artifacts and artifacts["train_cols"]:
        train_cols = list(artifacts["train_cols"])  # expected order
        for c in train_cols:
            if c not in df.columns:
                df[c] = 0
        # If there are extra cols in df not in train_cols, drop them
        extra = set(df.columns) - set(train_cols)
        if extra:
            df = df.drop(columns=list(extra))
        # Reorder to train cols
        df = df[train_cols]

    # Scale numerical columns
    scaler = artifacts.get("scaler") if artifacts else None
    if scaler is not None:
        num_cols = artifacts.get("numerical_cols") if artifacts and artifacts.get("numerical_cols") else df.select_dtypes(include=["number"]).columns.tolist()
        num_cols = [c for c in num_cols if c in df.columns]
        if num_cols:
            try:
                df[num_cols] = scaler.transform(df[num_cols])
            except Exception:
                df[num_cols] = df[num_cols].astype(float)
    else:
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def transaction_to_features(transaction: Dict[str, Any]) -> Dict[str, Any]:
    features: Dict[str, Any] = {}
    features["amount"] = transaction.get("amount")

    time_ind = transaction.get("time_ind")
    if time_ind is not None:
        time_feats = parse_time_features(str(time_ind))
        features.update(time_feats)
    else:
        features.update({"hour": None, "day_of_week": None, "parsed": False})

    features["src_acc"] = transaction.get("src_acc")
    features["dst_acc"] = transaction.get("dst_acc")

    return features
