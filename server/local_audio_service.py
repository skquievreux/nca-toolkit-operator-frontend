"""
Local Audio Processing Service
Handles audio operations that the NCA Toolkit container doesn't support
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from file_handler import UPLOAD_FOLDER

def concatenate_audio_files(audio_urls, output_filename='concatenated.mp3'):
    """
    Concatenate multiple audio files using local FFmpeg
    
    Args:
        audio_urls: List of URLs to audio files (can be local file:// URLs)
        output_filename: Name for the output file
        
    Returns:
        Path to the concatenated audio file
    """
    logger.info(f"🔧 Local audio concatenation: {len(audio_urls)} files")
    
    # Download/locate input files
    input_files = []
    for i, url in enumerate(audio_urls):
        if url.startswith('http://host.docker.internal') or url.startswith('http://localhost'):
            # Local file - extract path
            filename = url.split('/')[-1]
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                input_files.append(file_path)
                logger.info(f"  ✓ File {i+1}: {filename}")
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            # Remote file - would need to download
            raise NotImplementedError("Remote file download not yet implemented")
    
    if not input_files:
        raise ValueError("No input files found")
    
    # Create concat file list for FFmpeg
    concat_file = os.path.join(UPLOAD_FOLDER, f'concat_list_{os.getpid()}.txt')
    with open(concat_file, 'w') as f:
        for file_path in input_files:
            # FFmpeg concat requires absolute paths with forward slashes
            abs_path = os.path.abspath(file_path).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
    
    # Output file
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    try:
        # Run FFmpeg concat
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',  # Overwrite output
            output_path
        ]
        
        logger.info(f"🎬 Running FFmpeg: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg stderr: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        logger.info(f"✅ Audio concatenation successful: {output_path}")
        
        # Return URL that frontend can access
        return f"http://localhost:5000/uploads/{output_filename}"
        
    finally:
        # Cleanup concat file
        if os.path.exists(concat_file):
            os.remove(concat_file)
