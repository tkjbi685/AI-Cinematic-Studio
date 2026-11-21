# AI Cinematic Studio 🎬

A free, GitHub Actions-powered cinematic 3D video generator. Start a render from the **Actions** tab and download the resulting MP4 artifact.

> **Current engine:** procedural 3D scene rendered with Blender (Eevee), then encoded with FFmpeg. It does not call paid APIs or require secrets.
>
> **Honest quality note:** GitHub-hosted runners do not provide a guaranteed dedicated GPU. The initial renderer prioritizes a complete, reproducible 60-second cinematic sequence over claiming studio-grade photorealism. Render time and quality depend on runner limits.

## Create your first video

1. Open the repository's **Actions** tab.
2. Select **Render cinematic MP4**.
3. Click **Run workflow**.
4. Keep the default settings for the first run and confirm **Run workflow**.
5. Open the completed run and download **cinematic-video-mp4** under Artifacts.
6. Extract the ZIP to get `cinematic.mp4`.

The workflow can take a while because it renders frames on a CPU runner. The job has a time limit and may fail if the runner reaches it.

## Default film

A one-minute, widescreen science-fiction chase through a rain-soaked neon megacity. The scene is generated procedurally in Blender: animated vehicle, city skyline, road markings, atmospheric haze, animated lights, camera movement, and cinematic color treatment. No real-world weapons or dangerous instructions are depicted.

## Settings

The workflow supports:
- Duration: 60 seconds (fixed for this first release)
- Output: MP4, H.264, 16:9
- Render quality: draft / standard / high (higher settings take longer)
- Optional custom title displayed in the opening shot

## Project layout

- `.github/workflows/render.yml` — one-click cloud render and artifact upload
- `scripts/create_scene.py` — procedural Blender scene and animation
- `scripts/render.sh` — render and encode pipeline

## Limits and privacy

- GitHub Actions is not an unlimited GPU service. Public repository usage is subject to GitHub Actions policies and runner time limits.
- The project currently renders a designed 3D sequence; it does not generate arbitrary photorealistic footage from text.
- No API keys, personal data, or paid services are needed.
- Workflow artifacts are temporary and expire according to GitHub's artifact-retention policy.

## License

MIT
