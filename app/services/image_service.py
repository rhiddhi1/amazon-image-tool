# app/services/image_service.py
from fastapi.responses import StreamingResponse
from PIL import Image
import io

async def process_image_logic(file):
    """
    Handles image upload, resizes it, maintains aspect ratio, and outputs a
    safe PNG/JPEG file that works in Preview/browser.
    """

    contents = await file.read()
    input_stream = io.BytesIO(contents)

    try:
        # Open input image (Pillow handles JPEG, PNG, GIF, WebP, etc.)
        image = Image.open(input_stream)
        image_format = image.format  # Keep original format if needed

        # Convert to RGBA to handle transparency
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Resize while maintaining aspect ratio
        max_size = (1000, 1000)
        image.thumbnail(max_size)

        # White background for flattening transparent images
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image)  # mask=image keeps transparency

        # Save to BytesIO
        output = io.BytesIO()
        # Always save as PNG to avoid corruption
        output_format = "PNG"
        background.save(output, format=output_format)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type=f"image/{output_format.lower()}",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}.{output_format.lower()}"
            }
        )

    except Exception as e:
        # Optional: log error
        print("Image processing error:", e)
        return {"error": "Failed to process image. Make sure it is a valid image file."}