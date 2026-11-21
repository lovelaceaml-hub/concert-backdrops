"""Compose existing preparation, checkpoints, finishing and review in one command."""
from __future__ import annotations

from .media import assemble, qa, storyboard
from .project import PipelineError, Project, safe_path
from .render import guard_render, render


def plan(project: Project, quality: str, *, selected=None, shot_ids=None, editor="ffmpeg") -> dict:
    settings = project.settings(quality)
    if selected is not None and any(frame < 0 or frame >= project.frames for frame in selected):
        raise PipelineError("Selected frames are outside this project's timeline.")
    if shot_ids and set(shot_ids) - {shot["id"] for shot in project.shots}:
        raise PipelineError("A selected shot does not exist in this project.")
    backends = sorted({shot["renderer"] for shot in project.shots})
    partial = selected is not None or shot_ids is not None
    audio = project.data.get("audio", {})
    supplied = audio.get("source")
    return {"project_id": project.id, "quality": quality, "settings": settings,
            "renderers": backends, "editor": editor, "frames": project.frames,
            "selected_frames": selected, "selected_shots": shot_ids,
            "duration_seconds": project.seconds, "source_audio": supplied,
            "audio_present": bool(supplied and safe_path(project.root, supplied, exists=False).is_file()),
            "source_audio_sha256_expected": audio.get("source_sha256"),
            "audio_offset_seconds": audio.get("offset_seconds", 0),
            "picture_delay_seconds": 0.1 if "p3d-approved" in backends else 0.0,
            "stages": ["prepare", "render", "gallery"] if partial else ["prepare", "render", "assemble", "qa", "gallery"],
            "output": str(project.output(quality)), "workers": 1,
            "checkpoint": "Checksummed atomic PNGs; matching frames are reused after interruption.",
            "plan_only": True, "cloud_gpu_provider": None,
            "creative_approval": "No automatic user approval is recorded."}


def prepare(project: Project) -> dict:
    renderers = {shot["renderer"] for shot in project.shots}
    if renderers == {"p3d-approved"}:
        from .approved import prepare as prepare_reference
        return prepare_reference(project)
    if renderers == {"p3d-kit"}:
        from .kit import prepare as prepare_kit
        return prepare_kit(project)
    return {"preparation": "Scene dependencies are declared in the manifest; no extra preparation adapter is required."}


def produce(project: Project, quality: str, *, selected=None, shot_ids=None, force=False,
            allow_local=False, editor="ffmpeg", profile=None) -> dict:
    proposal = plan(project, quality, selected=selected, shot_ids=shot_ids, editor=editor)
    guard_render(project, allow_local)
    if (project.output(quality) / "STOP").exists():
        raise PipelineError("This production round has a STOP marker. Remove it only when intentionally resuming.")
    prepared = prepare(project)
    render(project, quality, selected=selected, shot_ids=shot_ids, force=force, allow_local=allow_local)
    result = {"project_id": project.id, "quality": quality, "preparation": prepared,
              "plan_only": False, "complete": selected is None and shot_ids is None}
    if result["complete"]:
        if (project.output(quality) / "STOP").exists():
            raise PipelineError("Production stopped before assembly. Rendered frames remain reusable.")
        result["master"] = str(assemble(project, quality, editor=editor, allow_local=allow_local, profile=profile))
        result["qa"] = qa(project, quality)
    result["gallery"] = str(storyboard(project, quality))
    result["stages"] = proposal["stages"]
    return result
