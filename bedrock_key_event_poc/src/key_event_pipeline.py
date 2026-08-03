from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
import os

from bedrock_event_detector import BedrockKeyEventDetector, DetectorConfig
from frame_sampler import extract_frames


def load_event_types(config_path: str) -> List[str]:
    data = json.loads(Path(config_path).read_text())
    event_types = data.get("event_types", [])
    if "none" not in event_types:
        event_types.append("none")
    return event_types


def deduplicate_events(events: List[Dict], min_gap_seconds: float = 12.0) -> List[Dict]:
    deduped: List[Dict] = []

    for event in sorted(events, key=lambda x: x["timestamp_s"]):
        if not deduped:
            deduped.append(event)
            continue

        last = deduped[-1]
        same_type = event["event_type"] == last["event_type"]
        close_in_time = (event["timestamp_s"] - last["timestamp_s"]) < min_gap_seconds

        if same_type and close_in_time:
            if event["confidence"] > last["confidence"]:
                deduped[-1] = event
            continue

        deduped.append(event)

    return deduped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bedrock sports key-event detection POC")
    parser.add_argument("--video", required=True, help="Path to sports broadcast video")
    parser.add_argument("--frames-dir", default="./outputs/frames", help="Frame output directory")
    parser.add_argument("--sample-every", type=float, default=2.0, help="Seconds between sampled frames")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional max frame count")
    parser.add_argument("--events-config", default="./config/events.json", help="Event config JSON")
    parser.add_argument("--output-json", default="./outputs/detections.json", help="All detections output JSON")
    parser.add_argument("--output-key-events", default="./outputs/key_events.json", help="Final key event list")
    parser.add_argument("--min-confidence", type=float, default=0.65, help="Key-event confidence threshold")
    parser.add_argument("--match-context", default="", help="Optional context string")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    # Some Bedrock models require invocation via inference profile instead of on-demand model ID.
    model_id = os.getenv("BEDROCK_INFERENCE_PROFILE_ID") or os.getenv("BEDROCK_MODEL_ID")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not model_id:
        raise ValueError(
            "Set either BEDROCK_INFERENCE_PROFILE_ID or BEDROCK_MODEL_ID in your environment/.env."
        )

    event_types = load_event_types(args.events_config)

    sampled_frames = extract_frames(
        video_path=args.video,
        output_dir=args.frames_dir,
        sample_every_seconds=args.sample_every,
        max_frames=args.max_frames,
    )

    detector = BedrockKeyEventDetector(
        DetectorConfig(
            model_id=model_id,
            region_name=region,
            event_types=event_types,
            min_confidence=args.min_confidence,
        )
    )

    detections: List[Dict] = []
    key_events: List[Dict] = []

    for frame in sampled_frames:
        result = detector.detect_event(
            image_path=frame["frame_path"],
            timestamp_s=frame["timestamp_s"],
            match_context=args.match_context,
        )
        detections.append(result)

        if result["is_key_event"]:
            key_events.append(result)

    key_events = deduplicate_events(key_events)

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(detections, indent=2))
    Path(args.output_key_events).write_text(json.dumps(key_events, indent=2))

    print(f"Sampled frames: {len(sampled_frames)}")
    print(f"Total detections: {len(detections)}")
    print(f"Key events (deduped): {len(key_events)}")
    for idx, event in enumerate(key_events, 1):
        print(
            f"{idx:02d}. t={event['timestamp_s']:.2f}s "
            f"event={event['event_type']} conf={event['confidence']:.2f}"
        )


if __name__ == "__main__":
    main()
