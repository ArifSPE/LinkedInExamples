from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


@dataclass
class DetectorConfig:
    model_id: str
    region_name: str
    event_types: List[str]
    min_confidence: float = 0.6


class BedrockKeyEventDetector:
    def __init__(self, config: DetectorConfig) -> None:
        self.config = config
        self.client = boto3.client("bedrock-runtime", region_name=config.region_name)

    def detect_event(
        self,
        image_path: str,
        timestamp_s: float,
        match_context: Optional[str] = None,
    ) -> Dict:
        prompt = self._build_prompt(timestamp_s=timestamp_s, match_context=match_context)
        image_bytes = Path(image_path).read_bytes()

        try:
            response = self.client.converse(
                modelId=self.config.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt},
                            {
                                "image": {
                                    "format": "jpeg",
                                    "source": {"bytes": image_bytes},
                                }
                            },
                        ],
                    }
                ],
                inferenceConfig={
                    "temperature": 0.0,
                    "maxTokens": 600,
                },
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            message = exc.response.get("Error", {}).get("Message", "")
            if code == "ResourceNotFoundException":
                raise RuntimeError(
                    "Bedrock model not available. Update BEDROCK_MODEL_ID to an active model "
                    f"in region '{self.config.region_name}'. Current value: '{self.config.model_id}'. "
                    "Use: aws bedrock list-foundation-models --region <region> --output table"
                ) from exc
            if code == "ValidationException" and "inference profile" in message.lower():
                raise RuntimeError(
                    "Bedrock model requires an inference profile for invocation. "
                    "Set BEDROCK_INFERENCE_PROFILE_ID (or ARN) in .env and retry. "
                    f"Current BEDROCK_MODEL_ID value: '{self.config.model_id}'. "
                    "You can keep BEDROCK_MODEL_ID empty when using BEDROCK_INFERENCE_PROFILE_ID."
                ) from exc
            raise RuntimeError(f"Bedrock Converse failed ({code}): {message}") from exc

        text = self._extract_text(response)
        parsed = self._extract_json(text)

        event_type = parsed.get("event_type", "none")
        confidence = float(parsed.get("confidence", 0.0))

        return {
            "image_path": image_path,
            "timestamp_s": timestamp_s,
            "event_type": event_type,
            "confidence": confidence,
            "reason": parsed.get("reason", ""),
            "entities": parsed.get("entities", []),
            "scoreboard": parsed.get("scoreboard", {}),
            "is_key_event": (
                event_type in self.config.event_types
                and event_type != "none"
                and confidence >= self.config.min_confidence
            ),
            "raw_model_response": text,
        }

    def _build_prompt(self, timestamp_s: float, match_context: Optional[str]) -> str:
        event_list = ", ".join(self.config.event_types)
        context_text = match_context if match_context else "No extra match context supplied."

        return f"""
You are a sports broadcast event analyst.

Task:
Analyze the attached sports broadcast frame and determine if it represents a key match event.

Valid event_type values:
[{event_list}]

Frame timestamp (seconds): {timestamp_s:.2f}
Match context: {context_text}

Rules:
1) Return only one event_type.
2) If uncertain, use event_type='none'.
3) Confidence must be between 0.0 and 1.0.
4) Be concise and evidence-based from visible frame cues only.
5) If the frame suggests a milestone (e.g., first career goal) from text overlays, capture it.

Return STRICT JSON only with this schema:
{{
  "event_type": "<one from valid list>",
  "confidence": <float 0..1>,
  "reason": "short explanation",
  "entities": ["player/team/referee names if visible"],
  "scoreboard": {{"home": "", "away": "", "clock": ""}}
}}
""".strip()

    @staticmethod
    def _extract_text(response: Dict) -> str:
        content = response.get("output", {}).get("message", {}).get("content", [])
        chunks = [entry.get("text", "") for entry in content if isinstance(entry, dict)]
        return "\n".join([c for c in chunks if c]).strip()

    @staticmethod
    def _extract_json(text: str) -> Dict:
        if not text:
            return {}

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass

        generic = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if generic:
            try:
                return json.loads(generic.group(1))
            except json.JSONDecodeError:
                return {}

        return {}
