import os
from PIL import Image as PILImage
from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

def validate_image_file(uploaded_file, max_size_mb=5):
    """
    Validates uploaded image files for extension, MIME type, size limit, and image header integrity.
    """
    if not uploaded_file:
        return False, "No file uploaded."

    # 1. File size check
    max_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_bytes:
        return False, f"File size exceeds limit of {max_size_mb}MB. (Uploaded: {round(uploaded_file.size / (1024*1024), 2)}MB)"

    # 2. Extension check
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Invalid file extension '{ext}'. Only JPG, PNG, and WEBP images are allowed."

    # 3. Content Type check
    content_type = getattr(uploaded_file, 'content_type', '')
    if content_type and not content_type.startswith('image/'):
        return False, f"Invalid MIME content type '{content_type}'. Must be an image file."

    # 4. Pillow Image Integrity inspection
    try:
        img = PILImage.open(uploaded_file)
        img.verify()
        # Reset file pointer after verify
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
    except Exception as e:
        return False, "Uploaded file appears to be a corrupted or invalid image."

    return True, "Valid"
