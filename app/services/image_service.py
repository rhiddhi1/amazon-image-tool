from PIL import Image
import io
from fastapi.responses import StreamingResponse

async def process_image_logic(file):
    from rembg import remove

    contents = await file.read()

    # Remove background
    removed_bg = remove(contents)

    # Open image with transparency
    image = Image.open(io.BytesIO(removed_bg)).convert("RGBA")

    # Maintain aspect ratio
    max_size = (1000, 1000)
    image.thumbnail(max_size)

    # White background
    background = Image.new("RGB", (1000, 1000), (255, 255, 255))
    img_width, img_height = image.size
    offset = ((background.width - img_width) // 2, (background.height - img_height) // 2)
    background.paste(image, offset, mask=image)  # important: mask=image for transparency

    # Save to BytesIO properly
    output = io.BytesIO()
    background.save(output, format="JPEG")
    output.seek(0)  # important to reset pointer

    # Return StreamingResponse
    return StreamingResponse(
        output,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f"attachment; filename=processed_{file.filename}.jpg"
        }
    )