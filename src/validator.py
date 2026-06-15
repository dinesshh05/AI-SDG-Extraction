from typing import List
from pydantic import BaseModel, ValidationError


class Initiative(BaseModel):

    initiative_name: str
    description: str
    metric: str

    sdg_ids: List[int]
    sdg_names: List[str]

    evidence: str
    page_reference: str


def validate_initiatives(data):

    validated = []

    for item in data:

        try:

            validated.append(
                Initiative(**item).model_dump()
            )

        except ValidationError as e:

            print(
                f"\nValidation Error:\n{e}\n"
            )

    return validated