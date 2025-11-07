from datetime import datetime
from typing import Dict, Any, Optional

import pandas as pd
import joblib

def parse_time_features(time_ind: str) -> Dict[str, Any]:
    try:
        dt = datetime.fromisoformat(time_ind)
    except Exception:
        try:
            dt = datetime.strptime(time_ind, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return {"hour": None, "day_of_week": None, "parsed": False}

    return {"hour": dt.hour, "day_of_week": dt.weekday(), "parsed": True}

def load_preprocessing_artifacts(path: str = "models/preprocessing_artifacts.joblib") -> Optional[Dict[str, Any]]:
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
    row = {k: transaction.get(k, None) for k in relevant_features}
    df = pd.DataFrame([row])

    # One-hot encode transac_type
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
