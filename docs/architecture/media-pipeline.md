# Free-first media pipeline

Media work starts from a versioned `ContentDraft` and a structured media specification: target format, dimensions/duration, text, visual style, voice/subtitle needs, template ID, and asset rights/provenance requirements. The initial path favors local, template-driven assembly instead of paid video generation.

## Planned stages

1. Select a licensed or project-owned template and validate source images/assets. Generate simple images with local tools or an optional image provider; do not scrape and repost copyrighted media.
2. Render text/graphics with Pillow or equivalent local tooling. A TTS adapter may produce voice; a silent/text-only variant remains possible. Record voice model/provider and permitted-use metadata.
3. Produce subtitle timing from the script or voice timing, render legible captions and text animation, and compose short video with FFmpeg. Version the template and composition settings.
4. Validate output format, dimensions, duration, codecs, audio levels, text clipping, subtitle readability, missing frames, file integrity, and platform constraints known at implementation time. A failed artifact is never promoted to publication-ready.
5. Store generated assets behind a media-storage interface. Local storage is the first adapter; an S3-compatible adapter may replace it later without changing content logic.

`ContentAsset` metadata links the source draft, account, template, tool/provider and version, input asset IDs, license/usage basis, generation time, checksum, storage URI, validation result, and derived assets. Keep temporary work separate from durable artifacts; clean it after a successful or terminal run. Avoid storing binary media in PostgreSQL or committing it to Git.

An optional future video-generation provider accepts the same media specification and returns candidate assets. It must pass the same provenance, cost/usage, validation, and approval gates. Provider output is not automatically publishable. See [integrations](integrations.md), [domain model](domain-model.md), and [security controls](security-and-controls.md).
