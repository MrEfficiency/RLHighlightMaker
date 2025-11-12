# python/video_stitcher.py

import subprocess
import os

def stitch_clips(clip_paths, output_path, cleanup=True):
    """
    Stitches multiple video clips into a single video file using FFmpeg.
    """
    if not clip_paths:
        print("No clips to stitch.")
        return

    # Create the temporary file list for ffmpeg
    list_path = os.path.join(os.path.dirname(output_path), "clips_to_stitch.txt")
    with open(list_path, 'w') as f:
        for path in clip_paths:
            # FFmpeg requires forward slashes and escaped special characters
            safe_path = path.replace('\\', '/')
            f.write(f"file '{safe_path}'\n")

    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_path,
        '-c', 'copy',
        '-y',
        output_path
    ]

    # Execute the stitching command
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up the temporary file and individual clips
    os.remove(list_path)
    if cleanup:
        for path in clip_paths:
            os.remove(path)
