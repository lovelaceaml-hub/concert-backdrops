"""Bind delivery evidence to exact source bytes and completed movie receipts.

These checks use only the standard library. They are independent of media
inspection, rendering and archive assembly, and are re-exported by delivery.py
for compatibility with existing callers.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


class DeliveryError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise DeliveryError(message)


def ledger_qa_arguments(path, source_commit, *, root=ROOT):
    """Expand a validation ledger without relabeling any historical inputs."""
    root, path = Path(root).resolve(), Path(path).resolve()
    require(path.is_file(), f"Missing validation ledger: {path}")
    raw = path.read_bytes()
    ledger = json.loads(raw)
    require(isinstance(ledger, dict), "The validation ledger must be a JSON object")
    require(ledger.get("picture_source", {}).get("commit") == source_commit,
            "The supplied picture commit differs from the validation ledger")
    names = ledger.get("package_evidence", {}).get("full_json_reports", [])
    records = ledger.get("artifacts", {})
    require(names and len(names) == len(set(names)), "The validation ledger needs unique full JSON report bindings")
    arguments = ["validation_ledger="+str(path)]
    snapshots = {path: hashlib.sha256(raw).hexdigest()}
    frozen = None
    bindings = []
    for name in names:
        require(re.fullmatch(r"[A-Za-z0-9_-]+", name) and name != "validation_ledger",
                f"Unsafe or reserved validation report label: {name}")
        record = records.get(name, {})
        relative = record.get("path")
        require(isinstance(relative, str) and not Path(relative).is_absolute(),
                f"Ledger report path must be repository-relative: {name}")
        report_path = (root/relative).resolve()
        require(report_path.is_relative_to(root) and report_path.is_file(),
                f"Ledger report is missing or outside the checkout: {name}")
        require(report_path.suffix.lower() == ".json", f"Ledger full report must be JSON: {name}")
        report_bytes = report_path.read_bytes()
        digest = hashlib.sha256(report_bytes).hexdigest()
        require(len(report_bytes) == record.get("bytes") and digest == record.get("sha256"),
                f"Ledger-bound QA bytes changed: {name}")
        snapshots[report_path] = digest
        arguments.append(name+"="+str(report_path))
        bindings.append({"label": name, "source_path": str(report_path),
                         "source_sha256": digest, "source_size_bytes": len(report_bytes)})
        if name == "frozen_picture_inputs":
            frozen = json.loads(report_bytes).get("source_sha256")
    require(isinstance(frozen, dict) and frozen,
            "The ledger must bind the complete frozen_picture_inputs source map")
    require(all(isinstance(name, str) and isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                for name, value in frozen.items()), "Invalid frozen picture source map")
    return {"arguments": arguments, "snapshots": snapshots, "frozen_sources": frozen,
            "record": {"source_path": str(path), "source_sha256": snapshots[path],
                       "source_size_bytes": len(raw), "source_picture_commit": source_commit,
                       "bound_report_count": len(bindings), "bindings": bindings}}


def _report_mode(label, record):
    """Use the actual record identity, with labels for plain shot receipts."""
    candidates = []
    if record.get("mode") in ("solo", "ensemble"):
        candidates.append(record["mode"])
    project = record.get("project_id")
    for mode in ("solo", "ensemble"):
        if project == "advanced-dance-"+mode or label.startswith(mode):
            candidates.append(mode)
    require(len(set(candidates)) <= 1, f"Conflicting QA performer/film identities: {label}")
    return candidates[0] if candidates else None


def verify_production_bindings(reports, movie_hashes, frozen_sources):
    """Bind the actual final pipeline schemas and proof source fingerprints."""
    identified = [(item, _report_mode(item["label"], item["content"])) for item in reports]
    verified = {}
    for mode in ("solo", "ensemble"):
        records = [(item["label"], item["content"]) for item, actual in identified if actual == mode]
        assemblies = [(label, r) for label, r in records
                      if r.get("filename") == "master.mp4" and "shot_fingerprints" in r]
        audits = [(label, r) for label, r in records
                  if r.get("filename") == "master.mp4" and "master_sha256" in r
                  and "technical_passed" in r]
        renders = [(label, r) for label, r in records
                   if r.get("shot_id") == "performance" and "provenance" in r and "frames" in r]
        require(len(assemblies) == len(audits) == len(renders) == 1,
                f"Supply exactly one {mode} final master.json, qa.json and performance/receipt.json")
        assembly_label, assembly = assemblies[0]
        audit_label, audit = audits[0]
        render_label, render = renders[0]
        project = "advanced-dance-"+mode
        for record in (assembly, audit):
            require(record.get("project_id") == project and record.get("quality") == "final",
                    f"A {mode} production record does not identify the final registered project")
            require(record.get("frames") == 1920 and record.get("fps") == 60,
                    f"A {mode} production record has the wrong frame clock")
        require(assembly.get("sha256") == audit.get("master_sha256") == movie_hashes[mode],
                f"The {mode} assembly and pipeline QA do not bind the exact supplied master")
        require(audit.get("technical_passed") is True and not audit.get("errors"),
                f"The final {mode} pipeline technical audit has not passed")
        require(render.get("complete") is True and (render.get("width"), render.get("height"), render.get("fps")) == (1920, 1080, 60),
                f"The {mode} render receipt is incomplete or not native 1080p60")
        frames = render["frames"]
        require(isinstance(frames, dict) and set(frames) == {str(i) for i in range(1920)}
                and all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) for value in frames.values()),
                f"The {mode} render receipt does not bind all 1,920 final frame hashes")
        fingerprint = render.get("fingerprint")
        require(isinstance(fingerprint, str) and re.fullmatch(r"[0-9a-f]{64}", fingerprint),
                f"Invalid {mode} render fingerprint")
        require(assembly.get("shot_fingerprints") == {"performance": fingerprint},
                f"The {mode} assembly refers to a different render receipt")
        provenance = render["provenance"]
        shot = provenance.get("shot", {})
        require(shot.get("scene") == f"tools/advanced_dance/{mode}.py"
                and shot.get("start_frame") == 0 and shot.get("end_frame_exclusive") == 1920,
                f"The {mode} frame provenance identifies a different scene or interval")
        require(all(provenance.get("inputs", {}).get(name) == digest for name, digest in frozen_sources.items()),
                f"The {mode} render source bytes differ from the frozen validation ledger")
        linked_proofs = []
        for label, record in records:
            if "source_fingerprint" in record:
                require(record["source_fingerprint"] == fingerprint,
                        f"The {mode} proof/review uses a different source fingerprint: {label}")
                linked_proofs.append(label)
        verified[mode] = {"assembly_report": assembly_label, "pipeline_qa_report": audit_label,
                          "render_report": render_label, "master_sha256": movie_hashes[mode],
                          "render_fingerprint": fingerprint, "frozen_picture_inputs_match": True,
                          "recorded_frame_hash_count": len(frames), "linked_proof_or_review_reports": linked_proofs,
                          "scope": "Existing pipeline receipts linked to the exact encoded master and frozen picture map. Frame PNG bytes are not decoded again by packaging."}
    return verified


def read_qa(arguments, movie_hashes, snapshots):
    require(arguments, "Supply the final QA JSON records with one or more --qa label=path arguments")
    reports, labels = [], set()
    for argument in arguments:
        label, separator, filename = argument.partition("=")
        require(separator and re.fullmatch(r"[A-Za-z0-9_-]+", label),
                "Use a unique safe label and a JSON path: --qa solo_motion=path.json")
        require(label not in labels, f"Duplicate QA label: {label}")
        labels.add(label)
        path = Path(filename).resolve()
        require(path.is_file(), f"Missing QA record: {path}")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if path in snapshots:
            require(digest == snapshots[path], f"Ledger-bound QA changed before embedding: {label}")
        record = json.loads(raw)
        require(isinstance(record, dict), f"QA record must contain an object: {path}")
        require(record.get("status") not in ("blocked", "failed"),
                f"QA report still has a blocking status: {label}")
        require(not record.get("error_count", 0), f"QA report contains numeric errors: {label}")
        require(not record.get("errors", []), f"QA report contains errors: {label}")
        require(record.get("technical_passed", True) is not False,
                f"Technical QA has not passed: {label}")
        require(record.get("blocking_visual_defects_found", False) is not True,
                f"Visual review records an unresolved blocking defect: {label}")
        mode = _report_mode(label, record)
        master_hash = record.get("master_sha256")
        if master_hash is not None:
            require(mode is not None and master_hash == movie_hashes[mode],
                    f"QA master hash does not match its final movie: {label}")
        if mode and record.get("filename") == "master.mp4" and "sha256" in record:
            require(record["sha256"] == movie_hashes[mode],
                    f"Assembly hash does not match its final movie: {label}")
        digest = hashlib.sha256(raw).hexdigest()
        snapshots[path] = digest
        reports.append({"label": label, "source_path": str(path), "source_sha256": digest,
                        "source_size_bytes": len(raw), "content": record})
    return reports
