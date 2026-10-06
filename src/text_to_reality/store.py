"""Local project storage. A project is a plain folder with a reality.json manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "text-to-reality/1"
MANIFEST = "reality.json"
HISTORY = "history.jsonl"
STAGES = ("requirements", "parts", "mechanical", "electronics", "firmware", "assembly", "testing")
STATUSES = ("todo", "done", "not_applicable")
STAGE_HINTS = {
    "requirements": "brief.md: what it does, size, power, budget, how you'll know it works",
    "parts": "bom.json: every part with quantity (see the package format reference)",
    "mechanical": "CAD source plus STL/STEP/3MF exports for printed or cut parts",
    "electronics": "wiring.json: every connection, and the JIG_ connectors used",
    "firmware": "source code, how to flash it, and what the user sees when it works",
    "assembly": "a picture-led guide: one action per step, shown in order",
    "testing": "checks to run after assembly, and what a pass looks like",
}


class ProjectError(ValueError):
    """A request the project store can't satisfy."""


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_root() -> Path:
    return Path(os.environ.get("TEXT_TO_REALITY_DIR") or Path.cwd() / "text-to-reality").resolve()


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]
    if not slug:
        raise ProjectError("project name needs at least one letter or number")
    return slug


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Store:
    def __init__(self, root: Path | None = None):
        self.root = (root or default_root()).resolve()

    def project_dir(self, project: str) -> Path:
        path = (self.root / slugify(project)).resolve()
        if path.parent != self.root:
            raise ProjectError("invalid project name")
        return path

    def load(self, project: str) -> tuple[Path, dict[str, Any]]:
        directory = self.project_dir(project)
        manifest = directory / MANIFEST
        if not manifest.is_file():
            raise ProjectError(f"no project named {project!r} in {self.root}")
        return directory, json.loads(manifest.read_text(encoding="utf-8"))

    def save(self, directory: Path, data: dict[str, Any]) -> None:
        tmp = directory / f".{MANIFEST}.tmp"
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        tmp.replace(directory / MANIFEST)

    def log(self, directory: Path, event: str, **fields: Any) -> None:
        with (directory / HISTORY).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at": now(), "event": event, **fields}) + "\n")

    def create(self, name: str, brief: str) -> dict[str, Any]:
        directory = self.project_dir(name)
        if (directory / MANIFEST).exists():
            raise ProjectError(f"project {directory.name!r} already exists")
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "brief.md").write_text(f"# {name}\n\n{brief.strip()}\n", encoding="utf-8")
        data = {
            "schema": SCHEMA,
            "id": directory.name,
            "name": name,
            "created": now(),
            "revision": 1,
            "stages": {stage: {"status": "todo", "reason": None, "files": []} for stage in STAGES},
            "files": {},
        }
        self.save(directory, data)
        self.record(directory.name, "requirements", ["brief.md"], _data=data, _directory=directory)
        self.log(directory, "created", name=name)
        return self.status(directory.name)

    def list(self) -> list[dict[str, Any]]:
        if not self.root.is_dir():
            return []
        projects = []
        for manifest in sorted(self.root.glob(f"*/{MANIFEST}")):
            data = json.loads(manifest.read_text(encoding="utf-8"))
            done = sum(1 for s in data["stages"].values() if s["status"] != "todo")
            projects.append({"id": data["id"], "name": data["name"], "revision": data["revision"], "stages_finished": f"{done}/{len(STAGES)}"})
        return projects

    def _relative(self, directory: Path, path: str) -> str:
        target = (directory / path).resolve()
        if directory not in target.parents:
            raise ProjectError(f"{path!r} is outside the project folder")
        if not target.is_file():
            raise ProjectError(f"{path!r} does not exist; write the file first")
        return target.relative_to(directory).as_posix()

    def record(self, project: str, stage: str, paths: list[str], *, _data: dict | None = None, _directory: Path | None = None) -> dict[str, Any]:
        if stage not in STAGES:
            raise ProjectError(f"stage must be one of {', '.join(STAGES)}")
        directory, data = (_directory, _data) if _data is not None else self.load(project)
        recorded = []
        for path in paths:
            relative = self._relative(directory, path)
            data["files"][relative] = {"sha256": sha256(directory / relative), "stage": stage, "revision": data["revision"], "recorded": now()}
            files = data["stages"][stage]["files"]
            if relative not in files:
                files.append(relative)
            recorded.append(relative)
        stage_entry = data["stages"][stage]
        if stage_entry["status"] == "todo":
            stage_entry["status"] = "done"
        self.save(directory, data)
        self.log(directory, "recorded", stage=stage, files=recorded)
        return {"stage": stage, "recorded": recorded}

    def set_stage(self, project: str, stage: str, status: str, reason: str | None = None) -> dict[str, Any]:
        if stage not in STAGES:
            raise ProjectError(f"stage must be one of {', '.join(STAGES)}")
        if status not in STATUSES:
            raise ProjectError(f"status must be one of {', '.join(STATUSES)}")
        if status == "not_applicable" and not (reason or "").strip():
            raise ProjectError("say why the stage doesn't apply")
        directory, data = self.load(project)
        data["stages"][stage].update(status=status, reason=reason.strip() if reason else None)
        self.save(directory, data)
        self.log(directory, "stage", stage=stage, status=status, reason=reason)
        return self.status(project)

    def new_revision(self, project: str, note: str) -> dict[str, Any]:
        directory, data = self.load(project)
        data["revision"] += 1
        self.save(directory, data)
        self.log(directory, "revision", revision=data["revision"], note=note)
        return {"revision": data["revision"], "note": note}

    def outcome(self, project: str, result: str, note: str) -> dict[str, Any]:
        if result not in {"worked", "partly_worked", "failed"}:
            raise ProjectError("result must be worked, partly_worked or failed")
        directory, data = self.load(project)
        self.log(directory, "outcome", revision=data["revision"], result=result, note=note)
        return {"recorded": True, "revision": data["revision"], "result": result}

    def history(self, project: str) -> list[dict[str, Any]]:
        directory, _ = self.load(project)
        log = directory / HISTORY
        if not log.is_file():
            return []
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def status(self, project: str) -> dict[str, Any]:
        directory, data = self.load(project)
        changed = [
            path for path, meta in data["files"].items()
            if not (directory / path).is_file() or sha256(directory / path) != meta["sha256"]
        ]
        return {
            "id": data["id"],
            "name": data["name"],
            "folder": str(directory),
            "revision": data["revision"],
            "stages": {
                stage: {**entry, "next": STAGE_HINTS[stage] if entry["status"] == "todo" else None}
                for stage, entry in data["stages"].items()
            },
            "changed_since_recorded": changed,
        }
