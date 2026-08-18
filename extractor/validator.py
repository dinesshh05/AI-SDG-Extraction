from typing import List, Tuple, Dict
from pydantic import BaseModel, ValidationError #type:ignore


class Initiative(BaseModel):

    initiative_name: str
    description: str
    metric: str

    sdg_ids: List[int]
    sdg_names: List[str]

    evidence: str
    page_reference: str


def validate_initiatives(data) -> Tuple[List[Dict], List[Dict]]:
    """
    Validates each extracted initiative against the schema.

    Returns (validated, errors) instead of validated alone. Previously
    validation failures were only printed to the console, which is
    invisible in the Streamlit app - the user would just see fewer
    rows in their Excel output with no explanation of why. Now the
    caller (main.py / app.py) can surface how many records failed and
    why, instead of the failure being silently swallowed.

    Each entry in `errors` is:
        {
            "item": <the raw dict that failed>,
            "reason": <human-readable summary of what failed>
        }
    """

    validated = []
    errors = []

    for item in data:

        try:

            validated.append(
                Initiative(**item).model_dump()
            )

        except ValidationError as e:

            # Keep the console log for local debugging...
            print(f"\nValidation Error:\n{e}\n")

            # ...but also return a compact, non-crashing summary so
            # the UI layer can tell the user something actually went
            # wrong, instead of just quietly returning fewer rows.
            error_summary = "; ".join(
                f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )

            errors.append(
                {
                    "item": item,
                    "reason": error_summary
                }
            )

    return validated, errors