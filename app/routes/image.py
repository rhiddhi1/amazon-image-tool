from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import JSONResponse
from app.services.image_service import process_image_logic
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/process/")
async def process_image(request: Request, file: UploadFile = File(...)):
    try:
        # Auth is optional — returns None if no token
        user_id = get_current_user(request)
        result = await process_image_logic(file)
        return result
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)