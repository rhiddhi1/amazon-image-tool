from PIL import Image
import io
from fastapi.responses import Response

async def process_image_logic(file):
    from rembg import remove  # lazy import (important for Render)

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

    img_width, img_height = image.size
    offset = (
        (background.width - img_width) // 2,
        (background.height - img_height) // 2
    )

    # Paste with transparency mask
    background.paste(image, offset, mask=image)

    # Step 5: Save to BytesIO
    output = io.BytesIO()
    background.save(output, format="JPEG")
    output.seek(0)

    # Step 6: Convert to bytes (IMPORTANT FIX)
    output_bytes = output.getvalue()

    # Step 7: Return proper response (no corruption)
    return Response(
        content=output_bytes,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": "attachment; filename=processed.jpg"
        }
    )