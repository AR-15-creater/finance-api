from pydantic import BaseModel
from typing import Optional

class expense(BaseModel):
    id: Optional[int] = None
    amount:float
    category:str

class Budget(BaseModel):
    id: Optional[int] = None
    category: str
    monthly_limit: float