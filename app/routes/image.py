from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from app.services.image_service import process_image_logic

router = APIRouter()

@router.post("/process/")
async def process_image(file: UploadFile = File(...)):
    try:
        result = await process_image_logic(file)
        return result
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)