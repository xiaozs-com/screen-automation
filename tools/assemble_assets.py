from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATOMIC = ROOT / "skills" / "screen-automation"
HYBRID = ROOT / "skills" / "screen-automation-engineer"
EXPERT = ROOT / "plugins" / "screen-automation-engineer"
EMBEDDED_ATOMIC = EXPERT / "skills" / "screen-automation"
DIST = ROOT / "dist"
GENERATED_HYBRID = DIST / "screen-automation-engineer"
IGNORED_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)


def fail(message: str) -> None:
    raise ValueError(message)


def frontmatter(path: Path, required_keys: tuple[str, ...] = ("name", "description", "version")) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
    header = text.split("\n---\n", 1)[0][4:]
    values: dict[str, str] = {}
    for key in required_keys:
        if key == "version":
            continue
        match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", header)
        if not match:
            fail(f"missing {key}: {path.relative_to(ROOT)}")
        values[key] = match.group(1).strip("'\"")
    metadata_version = re.search(r"(?m)^\s{2}version:\s*([^\s#]+)", header)
    top_version = re.search(r"(?m)^version:\s*([^\s#]+)", header)
    if "version" in required_keys and not metadata_version:
        fail(f"missing metadata.version: {path.relative_to(ROOT)}")
    if metadata_version:
        values["version"] = metadata_version.group(1).strip("'\"")
    if top_version and metadata_version and top_version.group(1).strip("'\"") != values["version"]:
        fail(f"version and metadata.version differ: {path.relative_to(ROOT)}")
    return values


def files_under(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and not any(part in IGNORED_NAMES for part in path.parts)
    )


def tree_digest(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in files_under(directory):
        relative = path.relative_to(directory).as_posix().encode("utf-8")
        digest.update(relative + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def safe_replace_tree(source: Path, destination: Path, allowed: tuple[Path, ...]) -> None:
    resolved_root = ROOT.resolve()
    resolved_destination = destination.resolve()
    if resolved_root not in resolved_destination.parents or destination not in allowed:
        fail(f"refusing unsafe sync target: {destination}")
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


WORKBUDDY_COMPAT_FIELDS = (
    "version",
    "display_name",
    "display_name_en",
    "description_zh",
    "description_en",
)


def add_workbuddy_frontmatter(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    version = re.search(r"(?m)^\s{2}version:\s*([^\s#]+)", text)
    description = re.search(r"(?m)^description:\s*(.+?)\s*$", text)
    description_en = re.search(r"(?m)^description_en:\s*(.+?)\s*$", text)
    if not version or not description or not description_en:
        fail(f"cannot derive WorkBuddy compatibility frontmatter: {skill_path.relative_to(ROOT)}")
    text = re.sub(
        r"(?m)^(?:version|display_name|display_name_en|description_zh|description_en):.*\n",
        "",
        text,
    )
    compatibility = (
        f"version: {version.group(1)}\n"
        "display_name: 屏幕自动化\n"
        "display_name_en: Screen Automation\n"
        f"description_zh: {description.group(1)}\n"
        f"description_en: {description_en.group(1)}\n"
    )
    text = re.sub(r"(?m)^(name:.*\n)", rf"\1{compatibility}", text, count=1)
    skill_path.write_text(text, encoding="utf-8", newline="\n")


def validate_workbuddy_atomic(expected_version: str) -> None:
    canonical_files = {path.relative_to(ATOMIC) for path in files_under(ATOMIC)}
    embedded_files = {path.relative_to(EMBEDDED_ATOMIC) for path in files_under(EMBEDDED_ATOMIC)}
    if canonical_files != embedded_files:
        fail("embedded WorkBuddy atomic skill file set has drifted")
    for relative in canonical_files - {Path("SKILL.md")}:
        if (ATOMIC / relative).read_bytes() != (EMBEDDED_ATOMIC / relative).read_bytes():
            fail(f"embedded WorkBuddy atomic skill has drifted: {relative.as_posix()}")
    canonical = (ATOMIC / "SKILL.md").read_text(encoding="utf-8")
    embedded = (EMBEDDED_ATOMIC / "SKILL.md").read_text(encoding="utf-8")
    for field in WORKBUDDY_COMPAT_FIELDS:
        if not re.search(rf"(?m)^{re.escape(field)}:\s*.+$", embedded):
            fail(f"WorkBuddy atomic Skill missing {field}")
    if not re.search(rf"(?m)^version:\s*{re.escape(expected_version)}$", embedded):
        fail("WorkBuddy atomic Skill version mismatch")
    if all(re.search(rf"(?m)^{re.escape(field)}:\s*.+$", canonical) for field in WORKBUDDY_COMPAT_FIELDS):
        for field in WORKBUDDY_COMPAT_FIELDS:
            source_value = re.search(rf"(?m)^{re.escape(field)}:\s*(.+)$", canonical)
            embedded_value = re.search(rf"(?m)^{re.escape(field)}:\s*(.+)$", embedded)
            if not source_value or not embedded_value or source_value.group(1) != embedded_value.group(1):
                fail(f"embedded WorkBuddy atomic Skill field differs: {field}")
        canonical_without_compatibility = re.sub(
            r"(?m)^(?:version|display_name|display_name_en|description_zh|description_en):.*\n",
            "",
            canonical,
        )
        embedded_without_compatibility = re.sub(
            r"(?m)^(?:version|display_name|display_name_en|description_zh|description_en):.*\n",
            "",
            embedded,
        )
        if embedded_without_compatibility != canonical_without_compatibility:
            fail("embedded WorkBuddy atomic Skill differs from its canonical source")
        return
    normalized = re.sub(
        r"(?m)^(?:version|display_name|display_name_en|description_zh|description_en):.*\n",
        "",
        embedded,
    )
    if normalized != canonical:
        fail("WorkBuddy atomic Skill differs from its canonical source")


def read_frontmatter_and_body(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
    header, body = text[4:].split("\n---\n", 1)
    return header, body.strip()


def load_assembly() -> dict[str, object]:
    path = HYBRID / "assembly.json"
    unexpected = [item.relative_to(HYBRID).as_posix() for item in files_under(HYBRID) if item != path]
    if unexpected:
        fail(f"hybrid source must contain only assembly.json: {', '.join(unexpected)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"schemaVersion", "name", "version", "owner", "slug", "displayName", "displayNameEn", "description", "descriptionEn", "agentSource", "skillSource"}
    missing = sorted(required - data.keys())
    if missing:
        fail(f"assembly definition missing: {', '.join(missing)}")
    if data["schemaVersion"] != 1 or data["name"] != "screen-automation-engineer":
        fail("unsupported hybrid assembly definition")
    if data["owner"] != "xiaozs-com" or data["slug"] != "screen-automation-engineer":
        fail("ClawHub owner/slug must remain fixed")
    for key in ("agentSource", "skillSource"):
        source = (HYBRID / str(data[key])).resolve()
        if ROOT.resolve() not in source.parents:
            fail(f"assembly source escapes repository: {key}")
    return data


def assemble_hybrid(definition: dict[str, object]) -> None:
    agent_path = (HYBRID / str(definition["agentSource"])).resolve()
    skill_dir = (HYBRID / str(definition["skillSource"])).resolve()
    _, agent_body = read_frontmatter_and_body(agent_path)
    _, skill_body = read_frontmatter_and_body(skill_dir / "SKILL.md")
    if GENERATED_HYBRID.exists():
        safe_replace_tree(skill_dir, GENERATED_HYBRID, (GENERATED_HYBRID,))
    else:
        GENERATED_HYBRID.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_dir, GENERATED_HYBRID)
    header = f'''---
name: {definition["name"]}
version: {definition["version"]}
display_name: {definition["displayName"]}
display_name_en: {definition["displayNameEn"]}
description: {definition["description"]}
description_zh: {definition["description"]}
description_en: {definition["descriptionEn"]}
metadata:
  owner: {definition["owner"]}
  slug: {definition["slug"]}
  version: {definition["version"]}
  displayName: {definition["displayName"]}
  homepage: https://www.xiaozs.com/sah/
---'''
    content = f"{header}\n\n{agent_body}\n\n---\n\n# 屏幕自动化能力与工程标准\n\n{skill_body}\n"
    (GENERATED_HYBRID / "SKILL.md").write_text(content, encoding="utf-8", newline="\n")
    openai = '''interface:
  display_name: "屏幕自动化工程师"
  short_description: "安全完成当前屏幕任务并创建可维护流程"
  default_prompt: "使用 $screen-automation-engineer，确认目标窗口和真实能力，再完成任务或创建经过监督验收的流程。"
'''
    (GENERATED_HYBRID / "agents" / "openai.yaml").write_text(openai, encoding="utf-8", newline="\n")


def validate_links(skill_dir: Path) -> None:
    link_pattern = re.compile(r"\[[^]]+\]\((?!https?://|#)([^)]+)\)")
    for path in files_under(skill_dir):
        if path.suffix.lower() != ".md":
            continue
        for target in link_pattern.findall(path.read_text(encoding="utf-8")):
            clean_target = target.split("#", 1)[0]
            if clean_target and not (path.parent / clean_target).resolve().exists():
                fail(f"broken local link {target!r} in {path.relative_to(ROOT)}")


def validate_skill(directory: Path, expected_name: str) -> str:
    required = directory / "SKILL.md"
    if not required.is_file():
        fail(f"missing SKILL.md: {directory.relative_to(ROOT)}")
    data = frontmatter(required)
    if data["name"] != expected_name:
        fail(f"expected skill name {expected_name}, got {data['name']}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"]):
        fail(f"invalid skill name: {data['name']}")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", data["version"]):
        fail(f"invalid SemVer: {data['version']}")
    validate_links(directory)
    return data["version"]


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"avatar is not PNG: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def validate_expert(expected_version: str) -> None:
    manifest_path = EXPERT / ".codebuddy-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = {
        "name", "version", "description", "author", "agents", "expertType",
        "agentName", "displayName", "profession", "displayDescription", "avatar",
        "categoryId", "defaultInitPrompt", "plugin", "tags", "quickPrompts",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        fail(f"WorkBuddy manifest missing: {', '.join(missing)}")
    if manifest["name"] != "screen-automation-engineer" or manifest["plugin"] != manifest["name"]:
        fail("WorkBuddy name/plugin mismatch")
    if manifest["expertType"] != "agent" or manifest["version"] != expected_version:
        fail("WorkBuddy type/version mismatch")
    if len(manifest["tags"]) != 3 or len(manifest["quickPrompts"]) != 3:
        fail("WorkBuddy tags and quickPrompts must each contain exactly 3 items")
    if manifest["defaultInitPrompt"] != manifest["quickPrompts"][0]:
        fail("WorkBuddy defaultInitPrompt must equal the first quickPrompt")
    agent_path = EXPERT / manifest["agents"][0]
    agent = frontmatter(agent_path, ("name", "description"))
    if agent["name"] != manifest["agentName"]:
        fail("WorkBuddy agentName does not match agent definition")
    avatar_path = EXPERT / manifest["avatar"]
    if png_dimensions(avatar_path) != (512, 512) or avatar_path.stat().st_size > 500_000:
        fail("WorkBuddy avatar must be a 512x512 PNG no larger than 500KB")
    if not EMBEDDED_ATOMIC.is_dir():
        fail("embedded WorkBuddy atomic skill is missing; run with --sync")
    validate_workbuddy_atomic(expected_version)


def deterministic_zip(source: Path, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files_under(source):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix in {".sh", ".ps1"} else 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize, validate, and build Agent assets.")
    parser.add_argument("--sync", action="store_true", help="refresh derived embedded assets")
    parser.add_argument("--check", action="store_true", help="validate all source assets")
    parser.add_argument("--build", action="store_true", help="create deterministic ZIP packages")
    args = parser.parse_args()
    if not (args.sync or args.check or args.build):
        parser.error("choose at least one of --sync, --check, or --build")

    atomic_version = validate_skill(ATOMIC, "screen-automation")
    assembly = load_assembly()
    hybrid_version = str(assembly["version"])
    if atomic_version != hybrid_version:
        fail("atomic and hybrid skill versions must match for one asset release")
    if args.sync:
        safe_replace_tree(ATOMIC, EMBEDDED_ATOMIC, (EMBEDDED_ATOMIC,))
        add_workbuddy_frontmatter(EMBEDDED_ATOMIC / "SKILL.md")
    assemble_hybrid(assembly)
    validate_skill(GENERATED_HYBRID, "screen-automation-engineer")
    validate_expert(hybrid_version)

    result: dict[str, object] = {
        "ok": True,
        "version": hybrid_version,
        "atomicDigest": tree_digest(ATOMIC),
    }
    if args.build:
        packages = {
            f"screen-automation-{atomic_version}.zip": ATOMIC,
            f"screen-automation-engineer-clawhub-{hybrid_version}.zip": GENERATED_HYBRID,
            f"screen-automation-engineer-workbuddy-{hybrid_version}.zip": EXPERT,
        }
        result["packages"] = {
            name: deterministic_zip(source, DIST / name) for name, source in packages.items()
        }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
