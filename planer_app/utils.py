from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def optimize_image(image_file, max_width=1200, max_height=1200, quality=85):
    """
    Optimize an uploaded image by:
    1. Converting to WebP format
    2. Resizing if larger than max dimensions (maintaining aspect ratio)
    3. Compressing with specified quality

    Args:
        image_file: Django UploadedFile object
        max_width: Maximum width in pixels (default 1200)
        max_height: Maximum height in pixels (default 1200)
        quality: WebP quality 0-100 (default 85)

    Returns:
        InMemoryUploadedFile: Optimized image ready to save to ImageField
    """
    # Open the image
    img = Image.open(image_file)

    # Convert RGBA to RGB if necessary (WebP supports RGBA but for compatibility)
    if img.mode in ("RGBA", "LA", "P"):
        # Create a white background
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Get original dimensions
    original_width, original_height = img.size

    # Calculate new dimensions maintaining aspect ratio
    if original_width > max_width or original_height > max_height:
        # Calculate scaling factor
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_factor = min(width_ratio, height_ratio)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Resize image with high-quality resampling
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Save to BytesIO as WebP
    output = BytesIO()
    img.save(output, format="WebP", quality=quality, optimize=True)
    output.seek(0)

    # Get original filename and change extension to .webp
    original_name = image_file.name
    name_without_ext = original_name.rsplit(".", 1)[0]
    new_filename = f"{name_without_ext}.webp"

    # Create InMemoryUploadedFile
    optimized_image = InMemoryUploadedFile(
        output, "ImageField", new_filename, "image/webp", sys.getsizeof(output), None
    )

    return optimized_image


def optimize_avatar(image_file, size=200, quality=85):
    """
    Optimize avatar/profile picture by:
    1. Converting to WebP format
    2. Resizing to square dimensions
    3. Center cropping to maintain aspect
    4. Compressing with specified quality

    Args:
        image_file: Django UploadedFile object
        size: Square dimensions in pixels (default 200x200)
        quality: WebP quality 0-100 (default 85)

    Returns:
        InMemoryUploadedFile: Optimized avatar ready to save to ImageField
    """
    # Open the image
    img = Image.open(image_file)

    # Convert to RGB if necessary
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Get original dimensions
    original_width, original_height = img.size

    # Calculate dimensions for center crop to square
    if original_width > original_height:
        # Landscape - crop width
        left = (original_width - original_height) // 2
        top = 0
        right = left + original_height
        bottom = original_height
    else:
        # Portrait or square - crop height
        left = 0
        top = (original_height - original_width) // 2
        right = original_width
        bottom = top + original_width

    # Crop to square
    img = img.crop((left, top, right, bottom))

    # Resize to target size
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Save to BytesIO as WebP
    output = BytesIO()
    img.save(output, format="WebP", quality=quality, optimize=True)
    output.seek(0)

    # Get original filename and change extension to .webp
    original_name = image_file.name
    name_without_ext = original_name.rsplit(".", 1)[0]
    new_filename = f"{name_without_ext}.webp"

    # Create InMemoryUploadedFile
    optimized_image = InMemoryUploadedFile(
        output, "ImageField", new_filename, "image/webp", sys.getsizeof(output), None
    )

    return optimized_image
