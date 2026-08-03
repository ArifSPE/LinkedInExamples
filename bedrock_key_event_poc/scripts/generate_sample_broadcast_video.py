from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def _draw_scoreboard(frame: np.ndarray, clock_text: str, score_text: str) -> None:
    cv2.rectangle(frame, (20, 20), (520, 95), (12, 12, 12), -1)
    cv2.rectangle(frame, (20, 20), (520, 95), (220, 220, 220), 2)
    cv2.putText(frame, "TEAM A vs TEAM B", (35, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (245, 245, 245), 2)
    cv2.putText(frame, score_text, (360, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (80, 240, 100), 2)
    cv2.putText(frame, clock_text, (35, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (245, 245, 245), 2)


def _draw_banner(frame: np.ndarray, text: str, color: tuple[int, int, int]) -> None:
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h - 110), (w, h), color, -1)
    cv2.putText(frame, text, (25, h - 42), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)


def _draw_pitch_background(frame: np.ndarray) -> None:
    h, w = frame.shape[:2]
    frame[:] = (40, 120, 40)

    stripe_h = 40
    for y in range(0, h, stripe_h * 2):
        cv2.rectangle(frame, (0, y), (w, min(y + stripe_h, h)), (35, 110, 35), -1)

    cv2.rectangle(frame, (40, 120), (w - 40, h - 140), (240, 240, 240), 2)
    cv2.line(frame, (w // 2, 120), (w // 2, h - 140), (240, 240, 240), 2)
    cv2.circle(frame, (w // 2, (h - 20) // 2), 55, (240, 240, 240), 2)


def generate_video(output_path: str, fps: int = 25, duration_s: int = 24) -> str:
    width, height = 1280, 720
    total_frames = fps * duration_s

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(out_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError("Could not create video writer. Check codec support for mp4v.")

    score_a = 0
    score_b = 0

    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        _draw_pitch_background(frame)

        seconds = i / fps
        game_min = int(seconds) // 60
        game_sec = int(seconds) % 60
        clock = f"{game_min:02d}:{game_sec:02d}"

        # Animated ball-like marker for visual variation.
        bx = int(120 + (i * 7) % (width - 240))
        by = int(180 + 80 * np.sin(i / 15.0) + (i * 3) % 240)
        by = max(150, min(height - 170, by))
        cv2.circle(frame, (bx, by), 14, (250, 250, 250), -1)
        cv2.circle(frame, (bx, by), 14, (20, 20, 20), 2)

        event_text = "LIVE"
        banner_color = (20, 80, 20)

        # 6-9s: GOAL event
        if 6 <= seconds < 9:
            score_a = 1
            event_text = "GOAL! #9 JOHN DOE SCORES"
            banner_color = (20, 120, 20)

        # 12-15s: RED CARD event
        if 12 <= seconds < 15:
            event_text = "RED CARD - TEAM B #4"
            banner_color = (30, 30, 180)
            cv2.rectangle(frame, (970, 190), (1090, 360), (0, 0, 255), -1)
            cv2.putText(frame, "RED", (984, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # 18-21s: FIRST CAREER GOAL style overlay
        if 18 <= seconds < 21:
            event_text = "MILESTONE: FIRST CAREER GOAL"
            banner_color = (160, 90, 20)

        score_text = f"{score_a} - {score_b}"
        _draw_scoreboard(frame, clock_text=clock, score_text=score_text)
        _draw_banner(frame, text=event_text, color=banner_color)

        writer.write(frame)

    writer.release()
    return str(out_path)


if __name__ == "__main__":
    generated = generate_video(
        output_path="sample_data/sports_broadcast_sample.mp4",
        fps=25,
        duration_s=24,
    )
    print(f"Generated sample video: {generated}")
