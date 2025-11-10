from PIL import Image
from PIL.ExifTags import TAGS
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import sys


def resize_image(image_file, max_width=1200, max_height=1200):
    """
    Resize image to maximum the provided dimensions

    Args:
        image_file: Django UploadedFile object
        max_width: Maximum width in pixels (default 1200)
        max_height: Maximum height in pixels (default 1200)

    Returns:
        InMemoryUploadedFile: Optimized image ready to save to ImageField
    """
    # Open the image
    img = Image.open(image_file)

    # Fix EXIF orientation
    try:
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                if TAGS.get(tag) == "Orientation":
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
                    break
    except (AttributeError, KeyError, IndexError):
        pass

    # Get original dimensions
    original_width, original_height = img.size

    # Calculate new dimensions maintaining aspect ratio
    if original_width > max_width or original_height > max_height:
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_factor = min(width_ratio, height_ratio)

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Save to BytesIO as JPEG
    output = BytesIO()
    img.save(output, format="JPEG", quality=90, optimize=True)
    output.seek(0)

    # Get original filename and change extension
    original_name = image_file.name
    name_without_ext = original_name.rsplit(".", 1)[0]
    new_filename = f"{name_without_ext}.jpeg"

    # Create InMemoryUploadedFile
    optimized_image = InMemoryUploadedFile(
        output, "ImageField", new_filename, "image/jpeg",
        sys.getsizeof(output), None
    )

    return optimized_image
