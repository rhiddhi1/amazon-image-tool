from PIL import Image
import io
from fastapi.responses import Response

async def process_image_logic(file):
    contents = await file.read()

    # Open original image
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Maintain aspect ratio
    max_size = (1000, 1000)
    image.thumbnail(max_size)

    # Create white background (Amazon style)
    background = Image.new("RGB", (1000, 1000), (255, 255, 255))

    img_width, img_height = image.size
    offset = (
        (background.width - img_width) // 2,
        (background.height - img_height) // 2
    )

    # Paste image on white background
    background.paste(image, offset)

    # Save to BytesIO
    output = io.BytesIO()
    background.save(output, format="JPEG")
    output.seek(0)

    # Convert to bytes
    output_bytes = output.getvalue()

    # Return response
    return Response(
        content=output_bytes,
        media_type="image/jpeg",
        headers={
            "Content-Disposition": "attachment; filename=processed.jpg"
        }
    )