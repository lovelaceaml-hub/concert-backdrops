"""Explicit SDR delivery profiles and validation of the actual encoded media."""
from __future__ import annotations

import math
import struct
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

from .project import PipelineError, Project


@dataclass(frozen=True)
class DeliveryProfile:
    name: str
    encoder: str
    codec: str
    codec_profile: str
    pixel_format: str
    extension: str
    master_filename: str
    source_bits_required: int
    codec_args: tuple[str, ...]
    audio_codec: str


PROFILES = {
    "h264": DeliveryProfile(
        "h264", "libx264", "h264", "High", "yuv420p", "mp4", "master.mp4", 8,
        ("-preset", "medium", "-crf", "16", "-profile:v", "high"), "aac",
    ),
    "hevc10": DeliveryProfile(
        "hevc10", "libx265", "hevc", "Main 10", "yuv420p10le", "mp4", "master-10bit.mp4", 16,
        ("-preset", "medium", "-crf", "18", "-profile:v", "main10", "-tag:v", "hvc1",
         "-x265-params", "pools=4:frame-threads=2:log-level=error"), "aac",
    ),
    "prores422hq": DeliveryProfile(
        "prores422hq", "prores_ks", "prores", "HQ", "yuv422p10le", "mov", "master-prores422hq.mov", 16,
        ("-profile:v", "3"), "pcm_s24le",
    ),
}


def get_profile(name: str) -> DeliveryProfile:
    if not isinstance(name, str) or name not in PROFILES:
        raise PipelineError(f"Unknown delivery profile {name!r}; choose from {', '.join(PROFILES)}.")
    return PROFILES[name]


def resolve_profile(project: Project, quality: str, override: str | None = None) -> DeliveryProfile:
    """Draft/review stay compatible unless a quality or invocation overrides them."""
    project.settings(quality)
    delivery = project.data.get("delivery", {})
    transfer = delivery.get("source_transfer", "srgb")
    if transfer not in ("srgb", "legacy_display_gamma") or delivery.get("color_space", "rec709") != "rec709":
        raise PipelineError("Select sRGB or the explicit legacy display convention for Rec.709 SDR delivery.")
    default = delivery.get("profile", "h264") if quality == "final" else "h264"
    selected = override or delivery.get("profiles_by_quality", {}).get(quality, default)
    profile = get_profile(selected)
    if transfer == "legacy_display_gamma" and profile.name != "h264":
        raise PipelineError("The legacy display convention is an RGB8 to H.264 SDR path.")
    return profile


@lru_cache(maxsize=1)
def encoder_capabilities() -> dict:
    """Probe the installed CPU encoders and color conversion filter, not GPU availability."""
    results = {}
    for label, flag in (("encoders", "-encoders"), ("filters", "-filters")):
        try:
            process = subprocess.run(["ffmpeg", "-hide_banner", flag], capture_output=True, text=True, check=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as exc:
            raise PipelineError(f"Cannot inspect FFmpeg {label}: {exc}") from exc
        results[label] = {parts[1] for line in process.stdout.splitlines() if len(parts := line.split()) > 1}
    return {
        "encoders": sorted(results["encoders"] & {profile.encoder for profile in PROFILES.values()}),
        "zscale": "zscale" in results["filters"],
    }


def require_encoder(profile: DeliveryProfile, *, source_transfer: str = "srgb") -> dict:
    capabilities = encoder_capabilities()
    if profile.encoder not in capabilities["encoders"]:
        raise PipelineError(f"The installed FFmpeg lacks {profile.encoder}, required by {profile.name}. Install a build with that CPU encoder.")
    if source_transfer == "srgb" and not capabilities["zscale"]:
        raise PipelineError("The installed FFmpeg lacks zscale. This pipeline requires it for the explicit sRGB to Rec.709 conversion.")
    return capabilities


def video_encoding_args(fps: int, profile: DeliveryProfile, *, source_transfer: str = "srgb") -> list[str]:
    # PNGs are display-referred sRGB, including Blender's AgX display output.
    # zimg's display-referred BT.709 uses the BT.1886 gamma-2.4 display EOTF.
    # A real transfer conversion is required; changing metadata alone is wrong.
    conversion = (
        "format=gbrp16le,zscale=matrixin=gbr:transferin=iec61966-2-1:"
        "primariesin=bt709:rangein=full:matrix=bt709:transfer=bt709:"
        "primaries=bt709:range=limited:dither=error_diffusion,format=" + profile.pixel_format
    )
    codec_metadata = []
    if source_transfer == "legacy_display_gamma":
        if profile.name != "h264":
            raise PipelineError("Legacy display pixels require the H.264 SDR profile.")
        # Preserve the production's filmic/gamma treatment. Do not apply the
        # sRGB transfer conversion used for Blender and browser PNGs.
        conversion = (
            "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
            "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709"
        )
        # PNG frame metadata can override output color flags in FFmpeg 7.1.
        # Set filtered-frame metadata and H.264 VUI without changing samples.
        codec_metadata = ["-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off"]
    elif source_transfer != "srgb":
        raise PipelineError("Unsupported source transfer convention.")
    return [
        "-vf", conversion, "-c:v", profile.encoder, *profile.codec_args, *codec_metadata,
        "-threads", "4", "-pix_fmt", profile.pixel_format, "-r", str(fps), "-fps_mode", "cfr",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-movflags", "+faststart+write_colr",
    ]


def audio_encoding_args(profile: DeliveryProfile) -> list[str]:
    args = ["-c:a", profile.audio_codec, "-ar", "48000"]
    if profile.audio_codec == "aac":
        args += ["-b:a", "256k"]
    return args


def png_header(path: Path) -> dict:
    """Read the PNG IHDR directly; Pillow converts RGB16 PNGs to RGB8 on load."""
    try:
        with path.open("rb") as stream:
            header = stream.read(33)
    except OSError as exc:
        raise PipelineError(f"Cannot read source frame {path}: {exc}") from exc
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[8:16] != b"\x00\x00\x00\x0dIHDR":
        raise PipelineError(f"Invalid PNG source frame: {path}")
    width, height, depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", header[16:29])
    if depth not in (8, 16) or color_type not in (0, 2, 4, 6) or compression or filtering or interlace not in (0, 1):
        raise PipelineError(f"Expected an 8-bit or 16-bit RGB/grayscale PNG frame: {path}")
    return {"width": width, "height": height, "bit_depth": depth, "color_type": color_type}


def validate_source_frames(project: Project, quality: str, profile: DeliveryProfile) -> dict:
    settings = project.settings(quality)
    depths: set[int] = set()
    colors: set[int] = set()
    count = 0
    for shot in project.shots:
        folder = project.output(quality) / "shots" / shot["id"] / "frames"
        for number in range(shot["start_frame"], shot["end_frame_exclusive"]):
            path = folder / f"frame_{number:06d}.png"
            header = png_header(path)
            if (header["width"], header["height"]) != (settings["width"], settings["height"]):
                raise PipelineError(f"Source frame dimensions do not match {quality}: {path}")
            if header["bit_depth"] < profile.source_bits_required:
                raise PipelineError(
                    f"{profile.name} requires actual 16-bit PNG inputs; frame {number} in {shot['id']} is "
                    f"{header['bit_depth']}-bit. Set quality.{quality}.image_bit_depth to 16 and render again. "
                    "Converting an existing 8-bit movie cannot restore missing precision."
                )
            depths.add(header["bit_depth"])
            colors.add(header["color_type"])
            count += 1
    return {"frame_count": count, "png_bit_depths": sorted(depths), "png_color_types": sorted(colors),
            "source_transfer": project.data.get("delivery", {}).get("source_transfer", "srgb")}


def stream_validation_errors(metadata: dict, profile: DeliveryProfile, *, width: int, height: int, fps: int, frames: int, wanted_audio: bool) -> list[str]:
    """Reject mislabeled outputs, wrong clock/duration, or missing/truncated audio."""
    errors = []
    streams = metadata.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    if len(videos) != 1:
        errors.append(f"Expected one video stream, found {len(videos)}.")
    video = videos[0] if videos else {}
    for label, expected in (("width", width), ("height", height), ("nb_read_frames", frames)):
        try:
            actual = int(video.get(label, -1))
        except (ValueError, TypeError):
            actual = -1
        if actual != expected:
            errors.append(f"{label}: expected {expected}, found {actual}.")
    for label in ("avg_frame_rate", "r_frame_rate"):
        try:
            actual_rate = Fraction(video.get(label, "0/1"))
        except (ValueError, TypeError, ZeroDivisionError):
            actual_rate = Fraction(0)
        if actual_rate != fps:
            errors.append(f"{label}: expected {fps}, found {video.get(label, 'missing')}.")
    expectations = {
        "codec_name": profile.codec, "profile": profile.codec_profile, "pix_fmt": profile.pixel_format,
        "color_primaries": "bt709", "color_transfer": "bt709", "color_space": "bt709",
    }
    if profile.name == "hevc10":
        expectations["codec_tag_string"] = "hvc1"
    for label, expected in expectations.items():
        if video.get(label) != expected:
            errors.append(f"{label}: expected {expected}, found {video.get(label, 'missing')}.")
    # ProRes MOV commonly exposes no range flag through ffprobe. Its encoded YUV
    # uses limited range by convention; our zscale conversion enforces that range.
    allowed_ranges = (None, "unknown", "tv") if profile.name == "prores422hq" else ("tv",)
    if video.get("color_range") not in allowed_ranges:
        errors.append(f"color_range: expected limited range, found {video.get('color_range', 'missing')}.")
    seconds = frames / fps
    tolerance = 1 / fps + 0.002
    try:
        duration = float(video.get("duration", metadata.get("format", {}).get("duration", 0)))
    except (ValueError, TypeError):
        duration = 0
    if not math.isfinite(duration) or abs(duration - seconds) > tolerance:
        errors.append(f"Video duration: expected {seconds:.6f}s, found {duration:.6f}s.")
    try:
        start = float(video.get("start_time", 0))
    except (ValueError, TypeError):
        start = -1
    if not math.isfinite(start) or abs(start) > 0.002:
        errors.append(f"Video starts at {start:.6f}s instead of zero.")
    if len(audios) != int(wanted_audio):
        errors.append(f"Expected {int(wanted_audio)} audio stream(s), found {len(audios)}.")
    for audio in audios:
        if audio.get("codec_name") != profile.audio_codec:
            errors.append(f"Audio codec: expected {profile.audio_codec}, found {audio.get('codec_name', 'missing')}.")
        if str(audio.get("sample_rate")) != "48000":
            errors.append(f"Audio sample rate: expected 48000, found {audio.get('sample_rate', 'missing')}.")
        try:
            audio_seconds = float(audio.get("duration", 0))
            audio_start = float(audio.get("start_time", 0))
        except (ValueError, TypeError):
            audio_seconds, audio_start = 0, -1
        # AAC packets cover 1024 samples; allow at most one packet or video frame.
        audio_tolerance = max(tolerance, 1024 / 48000 + 0.002)
        if not math.isfinite(audio_seconds) or abs(audio_seconds - seconds) > audio_tolerance:
            errors.append(f"Audio duration: expected {seconds:.6f}s, found {audio_seconds:.6f}s.")
        if not math.isfinite(audio_start) or abs(audio_start) > audio_tolerance:
            errors.append(f"Audio starts at {audio_start:.6f}s instead of zero.")
    return errors
