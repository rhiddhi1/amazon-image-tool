from PIL import Image
import io
from fastapi.responses import StreamingResponse
from rembg import remove

async def process_image_logic(file):
    contents = await file.read()

    # Step 1: Remove background
    removed_bg = remove(contents)

    # Step 2: Open image with transparency
    image = Image.open(io.BytesIO(removed_bg)).convert("RGBA")

    # Step 3: Maintain aspect ratio
    max_size = (1000, 1000)
    image.thumbnail(max_size)

    # Step 4: Create white background
    background = Image.new("RGB", (1000, 1000), (255, 255, 255))

    # Step 5: Center image
    img_width, img_height = image.size
    bg_width, bg_height = background.size

    offset = (
        (bg_width - img_width) // 2,
        (bg_height - img_height) // 2
    )

    # Paste using mask (important for transparency)
    background.paste(image, offset, image)

    # Step 6: Save output
    output = io.BytesIO()
    background.save(output, format="JPEG")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": f"attachment; filename=processed_{file.filename}"
        }
    )

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def process_image_logic(file):
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise Exception("File too large (max 5MB)")