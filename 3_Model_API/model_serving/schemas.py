from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum

class TRANSAC_TYPE(str, Enum):
    CASH_OUT = "CASH_OUT"
    PAYMENT = "PAYMENT"
    CASH_IN = "CASH_IN"
    TRANSFER = "TRANSFER"
    DEBIT = "DEBIT"


# Public list of allowed transaction type strings (used by preprocessing/pandas categories)
ALLOWED_TRANSAC_TYPES = list(TRANSAC_TYPE.__members__.keys())


class Transaction(BaseModel):
    # make time_ind optional for clients that don't provide timestamps
    time_ind: Optional[int] = Field(None, description="Transaction timestamp or time index")
    transac_type: TRANSAC_TYPE = Field(..., description="Transaction type / channel")
    amount: float = Field(..., gt=0, description="Transaction amount")
    # source / destination accounts are optional for some synthetic/test payloads
    src_acc: Optional[str] = Field(None, description="Source account identifier")
    src_bal: Optional[float] = Field(None, description="Source account balance before transaction")
    src_new_bal: Optional[float] = Field(None, description="Source account balance after transaction")
    dst_acc: Optional[str] = Field(None, description="Destination account identifier")
    dst_bal: Optional[float] = Field(None, description="Destination account balance before transaction")
    dst_new_bal: Optional[float] = Field(None, description="Destination account balance after transaction")

    class Config:
        schema_extra = {
            "example": {
                "transac_type": "CASH_OUT",
                "amount": 181.00,
                "src_bal": 181.0,
                "src_new_bal": 0,
                "dst_bal": 21182.0,
                "dst_new_bal": 0
            }
        }


class PredictionResponse(BaseModel):
    is_fraud: bool = Field(..., description="Fraud prediction (True/False)")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Fraud probability score")
    prediction_time: str = Field(..., description="ISO timestamp of prediction")


class FraudTransaction(BaseModel):
    id: int
    transaction_data: Dict
    fraud_probability: float
    prediction_time: str
