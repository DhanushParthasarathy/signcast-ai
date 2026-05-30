# Avatar Research Branch Plan

This workspace is not currently a Git repository, so `feature/avatar-research` could not be created locally.

When the project is under Git, create the branch with:

```bash
git checkout -b feature/avatar-research
```

Keep all experimental work under:

```text
experiments/avatar-research/
```

Production rules:

- Do not add avatar routes to production navigation.
- Do not expose MediaPipe, VRM, or generated pose playback behind public flags.
- Keep model artifacts, datasets, and experimental notebooks out of production images.
- Merge production fixes back into the research branch, not the reverse, until avatar quality and safety are reviewed.
