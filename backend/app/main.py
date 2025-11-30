from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid
import aiofiles

from app.routers import closet, outfits, colors

app = FastAPI(
    title="Best-Fit API",
    description="A smart wardrobe management system with color-based outfit suggestions",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(closet.router, prefix="/api/closet", tags=["Closet"])
app.include_router(outfits.router, prefix="/api/outfits", tags=["Outfits"])
app.include_router(colors.router, prefix="/api/colors", tags=["Colors"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Best-Fit API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Image upload endpoint (replaces Firebase Storage)
@app.post("/api/upload")
async def upload_image(
    image: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    Upload an image file to the server.
    Returns the URL to access the uploaded image.
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create user-specific directory
    user_upload_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(image.filename or "image.jpg")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(user_upload_dir, unique_filename)
    
    # Save uploaded file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await image.read()
        await f.write(content)
    
    # Return the URL to access the image
    image_url = f"/uploads/{user_id}/{unique_filename}"
    return {"image_url": image_url}


class DeleteImageRequest(BaseModel):
    image_url: str


@app.delete("/api/upload")
async def delete_image(request: DeleteImageRequest):
    """
    Delete an uploaded image from the server.
    """
    # Extract file path from URL
    image_path = request.image_url.lstrip('/')
    full_path = os.path.join(os.path.dirname(UPLOAD_DIR), image_path)
    
    if os.path.exists(full_path):
        os.remove(full_path)
        return {"message": "Image deleted successfully"}
    
    return {"message": "Image not found"}
