from fastapi import FastAPI, Response, UploadFile, HTTPException
from pydantic import BaseModel
from io import BytesIO

import sentimental_utils
import pandas as pd
import json


app = FastAPI()


@app.get("/")
async def root():
    return {
        "Response": "This is the API for sentimental Analysis"
    }


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, response: Response):
    # Read the file contents
    contents = await file.read()
    
    # check the file extension
    is_csv = file.filename.endswith(".csv")
    is_xlsx = file.filename.endswith(".xlsx")

    # Check if the file is valid csv/xlsx and read it into a pandas dataframe.
    if is_csv:
        df = pd.read_csv(BytesIO(contents))
    elif is_xlsx:
        df = pd.read_excel(BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or XLSX file.")
    
    # Check if column named "Review" Present int the file
    if "Review" not in df.columns:
        raise HTTPException(status_code=400, detail="This file doesn't have a 'Review' column.")

    # Extract the reviews from the Review column and split them into batches each of size 10
    reviews = list(df['Review'])
    batches = []

    for i in range(0, len(reviews), 10):
        batches.append("\n".join(reviews[i:i+10]))

    # Get sentimental scores for all the extracted reviews using Groq API
    # along with Error Handling for Groq API response
    try:
        sentiment_scores = []
        for batch in batches:
            sentiment_scores = sentiment_scores + sentimental_utils.score(batch)["scores"]
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Error parsing response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Groq API: {str(e)}")
    
    # Return the Response
    return {
        "filename": file.filename,
        "sentiment_scores": sentiment_scores
    }
