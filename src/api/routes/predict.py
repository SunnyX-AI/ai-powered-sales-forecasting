from io import StringIO

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from src.models.predict_units import predict_units_from_dataframe

router = APIRouter()


@router.post("/predict/units/csv")
async def predict_units_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and return units_sold predictions.
    """
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        result_df = predict_units_from_dataframe(df)

        return {
            "status": "ok",
            "rows": len(result_df),
            "items": result_df.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))