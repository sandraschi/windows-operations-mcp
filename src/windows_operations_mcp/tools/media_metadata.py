"""
Media Metadata Tools

This module provides functionality for reading and writing metadata from media files,
including EXIF data from images and ID3 tags from MP3 files.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime

from ..decorators import tool

class MediaMetadataError(Exception):
    """Base exception for media metadata operations."""
    pass

# Try to import optional dependencies
try:
    from PIL import Image, ExifTags
    # TAGS is available in ExifTags module in newer Pillow versions
    if hasattr(ExifTags, 'TAGS'):
        TAGS = ExifTags.TAGS
    else:
        # Fallback for older versions
        from PIL.Exif import TAGS
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    TAGS = None

try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK, TPE2, TCOM, TYER, TORY, TENC, TCOP, TSRC, TKEY, TBPM, COMM, USLT, SYLT, APIC, TXXX
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

def _ensure_dependencies():
    """Ensure required dependencies are installed."""
    if not HAS_PILLOW:
        raise MediaMetadataError("Pillow is required for image metadata operations. Install with: pip install Pillow")
    if not HAS_MUTAGEN:
        raise MediaMetadataError("Mutagen is required for audio metadata operations. Install with: pip install mutagen")

# EXIF (Image) Metadata Functions
@tool(
    name="get_image_metadata",
    description="Get EXIF metadata from an image file",
    parameters={
        "image_path": {
            "type": "string",
            "description": "Path to the image file"
        }
    }
)
def get_image_metadata(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get EXIF metadata from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing the image metadata
        
    Raises:
        MediaMetadataError: If the file is not an image or if there's an error reading metadata
    """
    _ensure_dependencies()
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise MediaMetadataError(f"File not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif() is not None:
                for tag, value in img._getexif().items():
                    if tag in TAGS:
                        exif_data[TAGS[tag]] = value
            
            return {
                "success": True,
                "metadata": exif_data,
                "file_info": {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size
                }
            }
    except Exception as e:
        raise MediaMetadataError(f"Error reading image metadata: {e}")

def update_image_metadata(
    image_path: Union[str, Path], 
    metadata: Dict[str, Any],
    save_copy: bool = False,
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Update EXIF metadata for an image file.
    
    Args:
        image_path: Path to the image file
        metadata: Dictionary of metadata to update
        save_copy: If True, save to a new file instead of modifying the original
        output_path: Path to save the modified file (required if save_copy is True)
        
    Returns:
        Dictionary containing the updated metadata
        
    Raises:
        MediaMetadataError: If there's an error updating the metadata
    """
    _ensure_dependencies()
    image_path = Path(image_path)
    
    if save_copy and not output_path:
        raise MediaMetadataError("output_path is required when save_copy is True")
    
    if not image_path.exists():
        raise MediaMetadataError(f"File not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            exif = img.info.get('exif', b'')
            
            # Create a copy of the image to modify
            if img.mode in ('P', 'PA'):
                img = img.convert('RGBA' if 'A' in img.mode else 'RGB')
            
            # Save the image with updated metadata
            output = output_path if save_copy else image_path
            img.save(output, exif=exif, **metadata)
            
            return get_image_metadata(output)
    except Exception as e:
        raise MediaMetadataError(f"Error updating image metadata: {e}")

# MP3 (Audio) Metadata Functions
def get_mp3_metadata(mp3_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get ID3 metadata from an MP3 file.
    
    Args:
        mp3_path: Path to the MP3 file
        
    Returns:
        Dictionary containing the MP3 metadata
        
    Raises:
        MediaMetadataError: If the file is not an MP3 or if there's an error reading metadata
    """
    _ensure_dependencies()
    mp3_path = Path(mp3_path)
    
    if not mp3_path.exists():
        raise MediaMetadataError(f"File not found: {mp3_path}")
    
    try:
        audio = MP3(mp3_path, ID3=ID3)
        metadata = {}
        
        # Standard ID3 tags
        if audio.tags is not None:
            for frame_id, frame in audio.tags.items():
                # Skip album art and other binary data
                if frame_id.startswith('APIC'):
                    continue
                metadata[frame_id] = str(frame)
        
        # Audio info
        metadata.update({
            'bitrate': audio.info.bitrate // 1000,  # kbps
            'length': int(audio.info.length),  # seconds
            'channels': audio.info.channels,
            'sample_rate': audio.info.sample_rate,
        })
        
        return metadata
    except Exception as e:
        raise MediaMetadataError(f"Error reading MP3 metadata: {e}")

def update_mp3_metadata(
    mp3_path: Union[str, Path], 
    metadata: Dict[str, Any],
    save_copy: bool = False,
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Update ID3 metadata for an MP3 file.
    
    Args:
        mp3_path: Path to the MP3 file
        metadata: Dictionary of metadata to update
        save_copy: If True, save to a new file instead of modifying the original
        output_path: Path to save the modified file (required if save_copy is True)
        
    Returns:
        Dictionary containing the updated metadata
        
    Raises:
        MediaMetadataError: If there's an error updating the metadata
    """
    _ensure_dependencies()
    mp3_path = Path(mp3_path)
    
    if save_copy and not output_path:
        raise MediaMetadataError("output_path is required when save_copy is True")
    
    if not mp3_path.exists():
        raise MediaMetadataError(f"File not found: {mp3_path}")
    
    try:
        # Create a copy if needed
        if save_copy:
            import shutil
            shutil.copy2(mp3_path, output_path)
            mp3_path = Path(output_path)
        
        # Update the metadata
        audio = MP3(mp3_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        
        # Map common tag names to ID3 frame classes
        tag_map = {
            'title': TIT2,
            'artist': TPE1,
            'album': TALB,
            'date': TDRC,
            'year': TYER,
            'genre': TCON,
            'tracknumber': TRCK,
            'album_artist': TPE2,
            'composer': TCOM,
            'original_year': TORY,
            'encoded_by': TENC,
            'copyright': TCOP,
            'isrc': TSRC,
            'initial_key': TKEY,
            'bpm': TBPM,
        }
        
        # Update the tags
        for tag, value in metadata.items():
            tag_class = tag_map.get(tag.lower())
            if tag_class:
                audio.tags.add(tag_class(encoding=3, text=str(value)))
            else:
                # Add as a custom tag
                audio.tags.add(TXXX(encoding=3, desc=tag, text=str(value)))
        
        # Save the changes
        audio.save()
        
        return get_mp3_metadata(mp3_path)
    except Exception as e:
        raise MediaMetadataError(f"Error updating MP3 metadata: {e}")

# Generic File Metadata Functions
def get_media_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get metadata from a media file (supports images and MP3s).
    
    Args:
        file_path: Path to the media file
        
    Returns:
        Dictionary containing the file metadata
        
    Raises:
        MediaMetadataError: If the file type is not supported
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    if ext in ('.jpg', '.jpeg', '.tiff', '.png', '.webp'):
        return get_image_metadata(file_path)
    elif ext == '.mp3':
        return get_mp3_metadata(file_path)
    else:
        raise MediaMetadataError(f"Unsupported file type: {ext}")

def update_media_metadata(
    file_path: Union[str, Path],
    metadata: Dict[str, Any],
    save_copy: bool = False,
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Update metadata for a media file (supports images and MP3s).
    
    Args:
        file_path: Path to the media file
        metadata: Dictionary of metadata to update
        save_copy: If True, save to a new file instead of modifying the original
        output_path: Path to save the modified file (required if save_copy is True)
        
    Returns:
        Dictionary containing the updated metadata
        
    Raises:
        MediaMetadataError: If the file type is not supported or there's an error
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    if ext in ('.jpg', '.jpeg', '.tiff', '.png', '.webp'):
        return update_image_metadata(file_path, metadata, save_copy, output_path)
    elif ext == '.mp3':
        return update_mp3_metadata(file_path, metadata, save_copy, output_path)
    else:
        raise MediaMetadataError(f"Unsupported file type: {ext}")
