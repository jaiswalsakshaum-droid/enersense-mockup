from pydantic import BaseModel
from typing import List

class SchemeItem(BaseModel):
    id: str
    title: str
    organization: str
    category: str
    eligible_industries: List[str]
    incentive: str
    max_benefit_inr: str
    eligibility_summary: str
    deadline: str
    status: str
    action_url: str
