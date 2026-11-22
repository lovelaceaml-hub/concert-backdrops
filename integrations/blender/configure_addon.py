"""Run through Blender to enable the add-on in this project's own profile."""

from __future__ import annotations

import json
import os
from pathlib import Path

import addon_utils
import bpy


root = Path(__file__).resolve().parents[2]
profile = root / ".tools/blender-profile"
expected_config = (profile / "config").resolve()
actual_config = Path(os.environ.get("BLENDER_USER_CONFIG", "/missing")).resolve()
if actual_config != expected_config:
    raise RuntimeError("Refusing to alter a Blender profile outside this checkout.")
expected_config.mkdir(parents=True, exist_ok=True)
addon_utils.enable("blender_mcp", default_set=True, persistent=True)
addon = bpy.context.preferences.addons.get("blender_mcp")
if addon is None:
    raise RuntimeError("Blender did not enable blender_mcp; inspect its import error above.")
addon.preferences.telemetry_consent = False
addon.preferences.bind_address = "localhost"
addon.preferences.allow_remote_connections = False
bpy.context.preferences.filepaths.use_scripts_auto_execute = False
if hasattr(bpy.context.preferences.system, "use_online_access"):
    bpy.context.preferences.system.use_online_access = False
disabled = []
for scene in bpy.data.scenes:
    scene.blendermcp_port = 9876
    scene.blendermcp_auto_start_server = True
    for prop in scene.bl_rna.properties:
        if prop.identifier.startswith("blendermcp_use_") and prop.type == "BOOLEAN":
            setattr(scene, prop.identifier, False)
            if prop.identifier not in disabled:
                disabled.append(prop.identifier)
bpy.ops.wm.save_userpref()
# This writes only the isolated profile, never the user's normal startup scene.
bpy.ops.wm.save_homefile()
report = {
    "blender_version": bpy.app.version_string,
    "addon_enabled": True,
    "addon_module": "blender_mcp",
    "telemetry": False,
    "bind_address": "localhost",
    "port": 9876,
    "remote_connections": False,
    "external_asset_and_generation_integrations": "disabled",
    "disabled_scene_properties": sorted(disabled),
    "live_connection_tested": False,
}
(profile / "installed.json").write_text(json.dumps(report, indent=2) + "\n")
print("PIPELINE_ADDON_CONFIG=" + json.dumps(report))
