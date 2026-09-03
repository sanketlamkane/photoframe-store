import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config

def init_storage(app):
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'originals'), exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'previews'), exist_ok=True)
    os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'thumbnails'), exist_ok=True)

    if Config.USE_CLOUDINARY:
        import cloudinary
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET
        )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage, folder_sub='originals'):
    """
    Saves the user's high-res photo.
    If Cloudinary is configured, uploads directly to Cloudinary (Free 25GB).
    Otherwise saves to local /uploads/ directory.
    Returns the web-accessible URL / relative path.
    """
    if not file_storage or file_storage.filename == '':
        return None
        
    ext = file_storage.filename.rsplit('.', 1)[1].lower() if '.' in file_storage.filename else 'jpg'
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    if Config.USE_CLOUDINARY:
        import cloudinary.uploader
        try:
            upload_res = cloudinary.uploader.upload(
                file_storage,
                folder=f"photoframe/{folder_sub}",
                public_id=uuid.uuid4().hex,
                resource_type="image"
            )
            return upload_res.get('secure_url')
        except Exception as e:
            print(f"Cloudinary upload error, falling back to local: {e}")

    # Local storage fallback
    dest_dir = os.path.join(Config.UPLOAD_FOLDER, folder_sub)
    os.makedirs(dest_dir, exist_ok=True)
    local_path = os.path.join(dest_dir, unique_name)
    
    file_storage.save(local_path)
    
    # Return path relative to upload route
    return f"/uploads/{folder_sub}/{unique_name}"

def save_base64_preview(base64_data_uri, folder_sub='previews'):
    """
    Saves the preview mockup canvas generated in the browser.
    Uploads directly to Cloudinary if configured, or saves locally.
    """
    import base64
    import re
    if not base64_data_uri or not base64_data_uri.startswith('data:image'):
        return None
        
    if Config.USE_CLOUDINARY:
        import cloudinary.uploader
        try:
            upload_res = cloudinary.uploader.upload(
                base64_data_uri,
                folder=f"photoframe/{folder_sub}",
                public_id=f"preview_{uuid.uuid4().hex[:10]}",
                resource_type="image"
            )
            return upload_res.get('secure_url')
        except Exception as e:
            print(f"Cloudinary preview upload error, falling back to local: {e}")

    # Local storage fallback
    img_format, img_str = base64_data_uri.split(';base64,')
    ext = re.search(r'image/(\w+)', img_format).group(1)
    if ext == 'jpeg': ext = 'jpg'
    
    unique_name = f"preview_{uuid.uuid4().hex[:10]}.{ext}"
    dest_dir = os.path.join(Config.UPLOAD_FOLDER, folder_sub)
    os.makedirs(dest_dir, exist_ok=True)
    local_path = os.path.join(dest_dir, unique_name)
    
    with open(local_path, 'wb') as f:
        f.write(base64.b64decode(img_str))
        
    return f"/uploads/{folder_sub}/{unique_name}"
