import pandas as pd
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
import io

class FileParserService:
    @staticmethod
    async def parse_file(file: UploadFile) -> pd.DataFrame:
        content = await file.read()
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise HTTPException(status_code=400, detail="Invalid file format. Please upload CSV or Excel.")
            
            # Reset file cursor for future reads if necessary, though here we consumed it
            # await file.seek(0) 
            
            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

    @staticmethod
    def get_preview(df: pd.DataFrame, num_rows: int = 5) -> Dict[str, Any]:
        # Replace NaN with None for JSON serialization
        df_preview = df.head(num_rows).where(pd.notnull(df), None)
        return {
            "headers": list(df.columns),
            "preview": df_preview.to_dict(orient='records'),
            "total_rows": len(df)
        }
