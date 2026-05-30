# AI Sign Language Avatar Roadmap

## Goal

Extend SignCast AI from dictionary-based sign clip playback to an AI-assisted avatar pipeline:

```text
News -> Summary -> ASL Gloss -> Pose Generation -> 3D Avatar Animation
```

This must be treated as an assistive research feature, not a replacement for qualified human interpreters. Every production release should include Deaf reviewer evaluation before user-facing rollout.

## Research Baseline

### Datasets

WLASL:

- Best fit: isolated sign vocabulary and lexical sign lookup.
- Useful for training or validating gloss-token-to-sign classifiers.
- Limitation: word-level signs do not solve continuous ASL grammar, transitions, facial grammar, or discourse context.

How2Sign:

- Best fit: continuous ASL generation and sentence-level alignment.
- Provides multimodal ASL video, transcripts, gloss annotations, depth/multiview assets, and 3D-oriented subsets.
- Use as the main dataset for continuous pose-generation experiments.

### Pose Extraction

MediaPipe Holistic:

- Extracts pose, face, and hands landmarks.
- Good MVP representation for sign motion because ASL depends on hands, body, and non-manual markers.
- Start with landmarks as the model target before attempting mesh/rig animation.

### Models

Sign Language Transformers:

- Best fit: English/simple-English-to-gloss and gloss-to-pose sequence conditioning.
- Use gloss as an intermediate representation because it improves controllability and reviewability.

Motion Diffusion:

- Best fit: generating smooth motion sequences conditioned on gloss tokens and prior poses.
- Needs strict constraints because generic text-to-motion models are not precise enough for sign language.

## Product Architecture

```text
frontend/
  AvatarPlayer.tsx
  PosePreview.tsx
  GenerationStatus.tsx

backend/
  services/avatar/
    pose_extractor.py
    gloss_aligner.py
    pose_generator.py
    rig_mapper.py
    avatar_renderer.py
  jobs/
    avatar_generation_worker.py

database/
  avatar_generation_jobs
  pose_sequences
  avatar_assets
  reviewer_feedback
```

## Production Pipeline

### Stage 1: Reviewed Dictionary Avatar MVP

Purpose: ship avatar playback safely without generative motion.

Flow:

1. Use existing ASL gloss tokens.
2. Map each gloss token to reviewed prerecorded clip.
3. Extract pose landmarks from each clip.
4. Retarget landmarks to a 3D avatar rig.
5. Blend transitions between signs.
6. Render in browser with Three.js.

Output:

- Avatar sequence is deterministic.
- Missing glosses route to admin review.
- No AI-generated signs are shown as authoritative.

Acceptance:

- >= 95 percent dictionary coverage for top news vocabulary.
- Deaf reviewer approval for all shipped token motions.
- Clear UI label: generated avatar is an accessibility aid.

### Stage 2: Pose Dataset Creation

Purpose: build a model-ready dataset.

Inputs:

- WLASL clips for isolated vocabulary.
- How2Sign continuous signing clips.
- Internal reviewed clips from SignCast dictionary.

Processing:

1. Normalize video metadata.
2. Extract MediaPipe Holistic landmarks per frame.
3. Store 543-landmark frames: pose, left hand, right hand, face.
4. Smooth landmarks with temporal filters.
5. Normalize coordinate systems around torso/shoulders.
6. Align gloss tokens to time ranges.
7. Reject low-confidence frames and occluded hands.
8. Export train/validation/test splits by signer, not random clip, to test generalization.

Stored sample:

```json
{
  "sample_id": "how2sign_0001",
  "gloss_tokens": ["NASA", "LAUNCH", "SATELLITE"],
  "frames": [
    {
      "timestamp_ms": 0,
      "pose": [[0.1, 0.2, -0.1]],
      "left_hand": [[0.4, 0.5, 0.0]],
      "right_hand": [[0.6, 0.5, 0.0]],
      "face": [[0.5, 0.2, 0.0]]
    }
  ],
  "quality": {
    "hand_visibility": 0.97,
    "face_visibility": 0.92,
    "reviewed": true
  }
}
```

### Stage 3: Gloss-to-Pose Baseline

Purpose: train a non-diffusion baseline first.

Model:

- Encoder: gloss token Transformer.
- Decoder: temporal Transformer or TCN.
- Output: normalized landmark frames.
- Losses:
  - position loss
  - velocity loss
  - acceleration smoothness loss
  - hand-shape loss
  - face/non-manual marker loss
  - bone-length consistency loss

Why first:

- Easier to debug than diffusion.
- Provides measurable baseline.
- Produces deterministic outputs for review.

Metrics:

- MPJPE for body/hand landmarks.
- Dynamic Time Warping distance.
- hand-shape similarity.
- lexical intelligibility judged by ASL reviewers.
- transition smoothness.

### Stage 4: Constrained Motion Diffusion

Purpose: improve naturalness while preserving sign precision.

Model:

- Conditional diffusion model over landmark sequences.
- Conditioning:
  - gloss token embeddings
  - target duration
  - previous/next sign context
  - signer/avatar style embedding
  - optional emotion/non-manual marker tags

Constraints:

- Freeze or heavily weight hand landmarks.
- Penalize hand orientation drift.
- Penalize face/eyebrow loss for questions, negation, intensity.
- Use classifier-free guidance carefully; high guidance can distort motion.

Output:

- Landmark sequence, not final pixels.
- Render through deterministic avatar rig.

### Stage 5: 3D Avatar Retargeting

Purpose: make generated landmarks usable in the product.

Steps:

1. Map MediaPipe landmarks to avatar skeleton controls.
2. Solve inverse kinematics for arms, wrists, and fingers.
3. Retarget face landmarks to blendshapes.
4. Add temporal smoothing.
5. Detect physically impossible poses.
6. Export:
   - browser runtime pose JSON
   - GLB animation clip
   - MP4 preview for audit

Recommended runtime:

- Three.js avatar viewer.
- VRM or GLB rig.
- Pose JSON streamed from backend or cached in Supabase Storage.

## Training Pipeline

```text
1. Ingest datasets
2. Extract landmarks
3. Normalize skeleton
4. Align glosses
5. Build train/val/test splits
6. Train baseline gloss-to-pose Transformer
7. Evaluate with metrics and Deaf review
8. Train constrained diffusion model
9. Retarget to avatar rig
10. Human review and release gate
```

### Data Ingestion

Jobs:

- `ingest_wlasl.py`
- `ingest_how2sign.py`
- `ingest_signcast_dictionary.py`

Outputs:

- canonical metadata table
- raw video references
- license/provenance records
- signer split assignments

### Landmark Extraction

Tooling:

- MediaPipe Holistic for pose, hands, face.
- FFmpeg for frame sampling.
- Store frame rate at 25 or 30 fps consistently.

Quality filters:

- reject samples with missing hands for more than 20 percent of frames.
- reject samples where face landmarks are missing during non-manual marker segments.
- flag excessive motion blur.

### Gloss Alignment

Alignment sources:

- dataset-provided gloss annotations.
- forced alignment where available.
- manual correction for high-value news vocabulary.

Rules:

- keep ASL gloss tokens uppercase.
- maintain token start/end timestamps.
- preserve facial grammar labels separately from manual signs.

Example:

```json
{
  "tokens": [
    { "gloss": "NASA", "start_ms": 0, "end_ms": 640 },
    { "gloss": "LAUNCH", "start_ms": 620, "end_ms": 1180 },
    { "gloss": "SATELLITE", "start_ms": 1160, "end_ms": 1900 }
  ],
  "non_manual": [
    { "label": "topic", "start_ms": 0, "end_ms": 640 }
  ]
}
```

### Model Training

Baseline config:

```yaml
model:
  type: gloss_to_pose_transformer
  gloss_vocab_size: 5000
  hidden_size: 512
  layers: 8
  heads: 8
  dropout: 0.1
target:
  fps: 30
  landmarks: holistic_543
loss:
  position: 1.0
  velocity: 0.5
  acceleration: 0.2
  bone_length: 0.5
  hand_shape: 1.5
  face: 0.8
training:
  batch_size: 16
  max_frames: 240
  optimizer: adamw
  lr: 0.0001
  epochs: 100
```

Diffusion config:

```yaml
model:
  type: conditional_motion_diffusion
  denoiser: transformer
  timesteps: 1000
conditioning:
  gloss_tokens: true
  duration: true
  previous_context: true
  non_manual_markers: true
loss:
  diffusion: 1.0
  hand_precision: 2.0
  face_precision: 1.0
  velocity: 0.4
  bone_length: 0.5
sampling:
  guidance_scale: 2.0
  steps: 50
```

## Evaluation

Automated:

- landmark reconstruction error.
- hand landmark error weighted higher than body.
- velocity/acceleration smoothness.
- bone length consistency.
- sequence duration accuracy.
- missing/invalid pose count.

Human:

- ASL intelligibility.
- semantic correctness.
- facial grammar correctness.
- comfort/naturalness.
- risk of misleading sign.

Release gates:

- No high-risk semantic errors in reviewer sample.
- No generated signs for unreviewed critical news vocabulary.
- Confidence displayed in UI.
- Fallback to dictionary video clips when model confidence is low.

## Product Rollout

Phase 0:

- Keep current prerecorded clip sequencing.
- Add pose extraction experiments offline.

Phase 1:

- Add avatar playback for reviewed dictionary clips only.
- No generative model in production.

Phase 2:

- Add model-generated transitions between known signs.
- Human review required before caching generated transition.

Phase 3:

- Add gloss-to-pose generation for low-risk educational content.
- Do not use for emergency, health, legal, or financial news without review.

Phase 4:

- Add continuous ASL avatar mode for selected reviewed categories.

## System Design

Backend services:

- `PoseExtractionService`
- `GlossAlignmentService`
- `PoseGenerationService`
- `AvatarRetargetingService`
- `AvatarRenderJobService`

Database:

- `pose_sequences`
- `avatar_generation_jobs`
- `avatar_assets`
- `reviewer_feedback`

Storage:

- raw clips
- landmark JSON
- generated pose JSON
- GLB animation clips
- MP4 previews

Frontend:

- Three.js avatar renderer.
- timeline scrubber.
- confidence indicators.
- fallback to prerecorded clips.
- reviewer annotation view.

## Immediate Engineering Tasks

1. Add `pose_sequences` and `avatar_generation_jobs` tables.
2. Build offline MediaPipe extraction script.
3. Extract landmarks from existing `sign_dictionary` clips.
4. Build a Three.js/VRM avatar proof of concept.
5. Retarget one reviewed sign clip to avatar rig.
6. Add reviewer UI for pose quality.
7. Train baseline gloss-to-pose Transformer.
8. Add diffusion model only after baseline evaluation.

## Safety And Governance

- Do not claim generated avatar output is certified interpretation.
- Always expose original text, simple English, and gloss alongside animation.
- Keep human-reviewed dictionary clips as fallback.
- Log model version, prompt version, data version, and confidence for every generated avatar.
- Maintain dataset license records and remove data on request.
- Require Deaf signer/reviewer feedback before public production release.
