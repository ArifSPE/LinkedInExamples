# Bedrock Sports Key Event Detection POC

This POC detects important moments from sports broadcast video using AWS Bedrock foundation models.

## Problem It Solves

For sports broadcasts, important events happen quickly:
- goal
- red card
- first career goal
- penalty events

This pipeline samples frames from video and sends them to a Bedrock multimodal model to identify key events.

## High-Level Flow

1. Sample video frames every `N` seconds.
2. Send each frame to Bedrock FM (vision-capable model).
3. Ask model for strict JSON with event type and confidence.
4. Keep events above threshold and deduplicate nearby duplicates.
5. Save all detections plus final key-event timeline.

## Project Structure

- `src/frame_sampler.py` - extracts periodic frames using OpenCV
- `src/bedrock_event_detector.py` - Bedrock multimodal call + structured parsing
- `src/key_event_pipeline.py` - end-to-end orchestration and output generation
- `config/events.json` - event taxonomy

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `AWS_REGION`
- `BEDROCK_INFERENCE_PROFILE_ID` (recommended)
- `BEDROCK_MODEL_ID` (optional fallback)

Also ensure AWS credentials are configured in your shell or profile:
- `aws configure`

### Inference Profile Note

Some newer Bedrock models cannot be invoked using on-demand model IDs directly.
If you see an error mentioning "inference profile", use an inference profile ID/ARN.

Useful commands:

```bash
aws bedrock list-inference-profiles --region us-east-1 --output table
aws bedrock list-foundation-models --region us-east-1 --output table
```

Then set in `.env`:

```bash
BEDROCK_INFERENCE_PROFILE_ID=<profile-id-or-arn>
```

If you use inference profile, you can leave `BEDROCK_MODEL_ID` empty.

## Run

```bash
cd bedrock_key_event_poc
python src/key_event_pipeline.py \
  --video /absolute/path/to/match.mp4 \
  --sample-every 2.0 \
  --min-confidence 0.7 \
  --match-context "Premier league match, Team A vs Team B"
```

## Outputs

- `outputs/detections.json` - model output for all sampled frames
- `outputs/key_events.json` - filtered and deduplicated key events

## Notes for Better Accuracy

- Use tighter sampling (`--sample-every 1.0`) for fast-paced moments.
- Expand `config/events.json` for sport-specific events.
- Add OCR and scoreboard tracking for stronger confidence calibration.
- For production, combine this with streaming ingestion (Kinesis + Lambda + Bedrock).
