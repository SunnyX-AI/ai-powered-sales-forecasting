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

        result_df = predict_units_from_dataframe(df).copy()

        # Convert datetime columns to string
        datetime_cols = result_df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns
        for col in datetime_cols:
            result_df[col] = result_df[col].astype(str)

        # Convert NaN / NaT to None so JSON is valid
        result_df = result_df.astype(object).where(pd.notnull(result_df), None)

        return {
            "status": "ok",
            "rows": int(len(result_df)),
            "items": result_df.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))