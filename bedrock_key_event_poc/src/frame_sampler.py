from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import cv2


def extract_frames(
    video_path: str,
    output_dir: str,
    sample_every_seconds: float = 2.0,
    max_frames: Optional[int] = None,
    jpeg_quality: int = 90,
) -> List[Dict]:
    """Sample frames from a video at fixed time intervals."""
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise ValueError(f"Unable to open video: {video_path}")

    fps = video.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25.0

    frame_interval = max(int(round(sample_every_seconds * fps)), 1)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results: List[Dict] = []
    frame_number = 0
    sampled_count = 0

    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)]

    while True:
        ok, frame = video.read()
        if not ok:
            break

        if frame_number % frame_interval == 0:
            timestamp_s = frame_number / fps
            frame_name = f"frame_{frame_number:06d}_t{timestamp_s:08.2f}.jpg"
            frame_path = out / frame_name

            if not cv2.imwrite(str(frame_path), frame, encode_params):
                raise RuntimeError(f"Failed writing frame: {frame_path}")

            results.append(
                {
                    "frame_path": str(frame_path),
                    "timestamp_s": timestamp_s,
                    "frame_number": frame_number,
                }
            )

            sampled_count += 1
            if max_frames is not None and sampled_count >= max_frames:
                break

        frame_number += 1

    video.release()
    return results
