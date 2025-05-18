from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from app.utils import extract_text_from_pdf
import os

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/extract")
async def extract(pdf: UploadFile = File(...)):
    temp_path = f"/tmp/{pdf.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await pdf.read()
            f.write(content)

        text = extract_text_from_pdf(temp_path)
        os.remove(temp_path)
        return {"text": text.strip(), "method": "fitz"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
