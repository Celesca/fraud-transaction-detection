"""Pydantic schemas for API requests and responses."""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import TransacType

class Transaction(BaseModel):
    transaction_id: Optional[str] = Field(None, description="Unique transaction identifier")
    time_ind: str = Field(..., description="Transaction timestamp or time index")
    transac_type: TransacType = Field(..., description="Transaction type / channel")
    amount: float = Field(..., gt=0, description="Transaction amount")
    src_acc: str = Field(..., description="Source account identifier")
    src_bal: Optional[float] = Field(None, description="Source account balance before transaction")
    src_new_bal: Optional[float] = Field(None, description="Source account balance after transaction")
    dst_acc: str = Field(..., description="Destination account identifier")
    dst_bal: Optional[float] = Field(None, description="Destination account balance before transaction")
    dst_new_bal: Optional[float] = Field(None, description="Destination account balance after transaction")


class PredictionResponse(BaseModel):
    transaction_id: Optional[str]
    is_fraud: bool = Field(..., description="Fraud prediction (True/False)")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Fraud probability score")
    prediction_time: str = Field(..., description="ISO timestamp of prediction")


class FraudTransaction(BaseModel):
    id: int
    transaction_id: Optional[str]
    transaction_data: Dict
    fraud_probability: float
    prediction_time: str
