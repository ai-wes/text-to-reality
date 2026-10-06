"""Test/build an immutable local candidate from one frozen source snapshot.

No publish, credentials, Git writes, installs to agent environments or settings.
Run with the repository development Python; uv/hatchling must already be cached.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path


def sha(content):
    return hashlib.sha256(content).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new candidate directory")
    parser.add_argument("--compact-runtime", action="store_true", help="also produce a separate wheel/skill package without full research source")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.absolute()
    if output.exists() or any(p.is_symlink() for p in (output, *output.parents)):
        raise SystemExit("Candidate output must be new and have no symlink ancestors")
    compact = output.with_name(output.name + "-runtime")
    if args.compact_runtime and (compact.exists() or any(p.is_symlink() for p in (compact, *compact.parents))):
        raise SystemExit("Compact runtime output must be new and have no symlink ancestors")
    paths = ["src", "skills", "tests", "docs", "scripts", "README.md", "LICENSE", "pyproject.toml"]
    with tempfile.TemporaryDirectory(prefix="ttr-candidate-", dir="/tmp") as temporary:
        snapshot = Path(temporary) / "source"
        snapshot.mkdir()
        for name in paths:
            source = root / name
            if source.is_dir():
                for path in source.rglob("*"):
                    if path.is_symlink():
                        raise SystemExit("Source snapshot refuses symlinks")
                shutil.copytree(source, snapshot / name, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".ruff_cache", "*.pyc"))
            else:
                if source.is_symlink():
                    raise SystemExit("Source snapshot refuses symlinks")
                shutil.copy2(source, snapshot / name)
        metadata = tomllib.loads((snapshot / "pyproject.toml").read_text())
        version = metadata["project"]["version"]
        source_files = {p.relative_to(snapshot).as_posix(): sha(p.read_bytes())
                        for p in sorted(snapshot.rglob("*")) if p.is_file()}
        environment = {**os.environ, "PYTHONPATH": str(snapshot / "src"), "UV_CACHE_DIR": "/tmp/ttr-build-cache"}
        tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=snapshot,
                               env=environment, text=True, capture_output=True, timeout=60)
        if tests.returncode:
            raise SystemExit(tests.stdout + tests.stderr)
        output.mkdir(parents=True)
        build = subprocess.run(["uv", "build", "--offline", "--no-config", "--out-dir", str(output)],
                               cwd=snapshot, env=environment, text=True, capture_output=True, timeout=60)
        if build.returncode:
            raise SystemExit(build.stdout + build.stderr)
        wheel = next(output.glob("*.whl"))
        installed = Path(temporary) / "installed"
        install = subprocess.run(["uv", "pip", "install", "--python", sys.executable, "--no-deps", "--target", str(installed), str(wheel)],
                                 env=environment, text=True, capture_output=True, timeout=60)
        if install.returncode:
            raise SystemExit(install.stdout + install.stderr)
        probe = """
import asyncio,json,hashlib
from pathlib import Path
from text_to_reality import catalog,connector_usage,__version__
from text_to_reality.server import create_server
from text_to_reality.store import Store
async def check():
 server=create_server(Store(Path('private-smoke-builds')))
 tool=await server.call_tool('connector_guidance',{})
 assert tool.structured_content['rules']==connector_usage.rules()
 rules=list(await server.read_resource('text-to-reality://connectors/usage-rules'))
 assert json.loads(rules[0].content)==connector_usage.rules()
 guide=list(await server.read_resource('text-to-reality://connectors/agent-guide'))
 assert guide[0].content==connector_usage.guide()
 plan=catalog.connectors_for([{'board':'seeed-xiao-esp32s3'}])
 assert plan['connectors'][0]['connectors']==2
 assert plan['physical_validation'] is False
 assert plan['model_choice']['approved_model_revision'] is None
 print(json.dumps({'version':__version__,'boards':len(catalog.boards()),'resources':len(await server.list_resources()),'tools':len(await server.list_tools()),'guide_sha256':hashlib.sha256(connector_usage.guide().encode()).hexdigest(),'physical_validation':False}))
asyncio.run(check())
"""
        smoke = subprocess.run([sys.executable, "-c", probe], cwd=temporary,
                               env={**environment, "PYTHONPATH": str(installed)}, text=True, capture_output=True, timeout=30)
        if smoke.returncode:
            raise SystemExit(smoke.stdout + smoke.stderr)
        shutil.copytree(snapshot / "skills", output / "skills")
        for name in ("DEPLOYMENT.md", "BATCH-IMPORT.md", "pending-batches.json"):
            shutil.copy2(snapshot / "docs/connector-library" / name, output / name)
        save_json(output / "source-snapshot.json", {"version": version, "files": source_files,
                  "snapshot_sha256": sha(json.dumps(source_files, sort_keys=True).encode())})
        save_json(output / "verification.json", {"tests": tests.stdout.strip(), "installed_wheel": json.loads(smoke.stdout),
                  "catalog_sha256": source_files["src/text_to_reality/data/boards.json"],
                  "rules_sha256": source_files["src/text_to_reality/data/connector_usage.json"],
                  "local_review_candidate": True, "public_release": False})
        verifier = '''from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'release.json').read_text())
for name,meta in manifest['files'].items():
 path=root/name
 if path.is_symlink() or not path.resolve().is_relative_to(root):raise SystemExit('Unsafe release path')
 content=path.read_bytes()
 if len(content)!=meta['bytes'] or hashlib.sha256(content).hexdigest()!=meta['sha256']:raise SystemExit('Integrity mismatch: '+name)
print('Release verified: '+str(len(manifest['files']))+' files')
'''
        (output / "verify_release.py").write_text(verifier)
        files = {p.relative_to(output).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
                 for p in sorted(output.rglob("*")) if p.is_file()}
        save_json(output / "release.json", {"version": version, "local_review_candidate": True, "files": files})
        identity = sha((output / "release.json").read_bytes())[:16]
        archive = output.parent / ("text-to-reality-connector-library-" + identity + ".zip")
        if archive.exists():
            raise SystemExit("Content-addressed archive already exists; preserve it")
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(output.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(output).as_posix())
        result = {"directory": str(output), "archive": str(archive), "archive_sha256": sha(archive.read_bytes()),
                  "version": version, "boards": json.loads(smoke.stdout)["boards"], "tests": tests.stdout.strip()}
        if args.compact_runtime:
            compact.mkdir()
            shutil.copy2(wheel, compact / wheel.name)
            shutil.copytree(output / "skills", compact / "skills")
            for name in ("DEPLOYMENT.md", "BATCH-IMPORT.md", "pending-batches.json", "source-snapshot.json", "verification.json", "verify_release.py"):
                shutil.copy2(output / name, compact / name)
            (compact / "PACKAGE-CONTENTS.md").write_text(
                "# Compact runtime and skill candidate\n\n"
                "Includes the tested wheel, skill and release guidance. The wheel and skill bytes are identical to the full package. "
                "Full research images/CAD/PDF and editable source/tests are in the separate full source/evidence package. "
                "source-snapshot.json identifies that matching source snapshot; it does not claim those source files are in this compact package. "
                "verification.json records the full-source regression and installed-wheel MCP checks. "
                "This is a local review candidate, with unresolved physical qualification and no public deployment.\n"
            )
            compact_files = {p.relative_to(compact).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
                             for p in sorted(compact.rglob("*")) if p.is_file()}
            save_json(compact / "release.json", {"version": version, "local_review_candidate": True,
                      "package_kind": "runtime_and_skill", "full_release_manifest_sha256": sha((output / "release.json").read_bytes()),
                      "full_archive_sha256": result["archive_sha256"], "files": compact_files})
            compact_identity = sha((compact / "release.json").read_bytes())[:16]
            compact_archive = compact.parent / ("text-to-reality-runtime-" + compact_identity + ".zip")
            if compact_archive.exists():
                raise SystemExit("Compact content-addressed archive already exists; preserve it")
            with zipfile.ZipFile(compact_archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
                for path in sorted(compact.rglob("*")):
                    if path.is_file():
                        bundle.write(path, path.relative_to(compact).as_posix())
            result.update({"runtime_directory": str(compact), "runtime_archive": str(compact_archive),
                           "runtime_archive_sha256": sha(compact_archive.read_bytes())})
        print(json.dumps(result))


if __name__ == "__main__":
    main()
