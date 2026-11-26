#!/usr/bin/env python3
"""Cache official Dacia model images locally with conditional HTTP refresh."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

SOURCE_PATH = Path("project/sources/dacia-pl-model-media-20260724.json")
CACHE_DIRECTORY = Path("assets/model-media")
MANIFEST_PATH = CACHE_DIRECTORY / "manifest.json"
USER_AGENT = "Dacia-Knowledge-Base/1.0"
OFFICIAL_PREFIXES = (
    "https://www.dacia.pl/",
    "https://cdn.group.renault.com/",
)


class MediaCacheError(RuntimeError):
    pass


def _read_json(path: Path, *, optional: bool = False) -> dict[str, Any]:
    if optional and not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaCacheError(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MediaCacheError(f"expected JSON object in {path}")
    return payload


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _extension(content_type: str, url: str) -> str:
    normalized = content_type.split(";", 1)[0].strip().lower()
    known = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
    }.get(normalized)
    if known:
        return known
    guessed = mimetypes.guess_extension(normalized) if normalized else None
    if guessed:
        return guessed
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".svg"} else ".img"


def _safe_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _placeholder_svg(model_code: str, model_name: str) -> bytes:
    name = _safe_xml(model_name)
    code = _safe_xml(model_code)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img">
<title>{name}</title><desc>Lokalna sylwetka zastępcza modelu {code}</desc>
<rect width="800" height="450" rx="32" fill="#eef2ed"/>
<path d="M150 292h500l-46-103c-12-27-39-45-69-45H317c-31 0-59 19-70 48l-35 91-62 9z" fill="#cbd5cb"/>
<path d="M281 168h249c21 0 40 12 49 31l28 63H230l29-75c4-11 13-19 22-19z" fill="#83958a"/>
<circle cx="262" cy="301" r="56" fill="#34433a"/><circle cx="262" cy="301" r="25" fill="#d9dfd9"/>
<circle cx="562" cy="301" r="56" fill="#34433a"/><circle cx="562" cy="301" r="25" fill="#d9dfd9"/>
<text x="400" y="401" text-anchor="middle" font-family="system-ui,sans-serif" font-size="30" fill="#34433a">{name}</text>
</svg>""".encode("utf-8")


def _load_sources(repository: Path) -> tuple[str, dict[str, dict[str, str]]]:
    payload = _read_json(repository / SOURCE_PATH)
    models = payload.get("models")
    if not isinstance(models, dict):
        raise MediaCacheError("media source has no models object")
    result: dict[str, dict[str, str]] = {}
    for model_code, item in models.items():
        if not isinstance(model_code, str) or not isinstance(item, dict):
            continue
        image_url = str(item.get("image_url", ""))
        page_url = str(item.get("source_page_url", ""))
        if not image_url.startswith(OFFICIAL_PREFIXES):
            raise MediaCacheError(f"non-official image URL for {model_code}")
        if not page_url.startswith("https://www.dacia.pl/"):
            raise MediaCacheError(f"non-official page URL for {model_code}")
        result[model_code] = {
            "model_name": str(item.get("model_name", model_code)),
            "image_url": image_url,
            "source_page_url": page_url,
            "source_name": str(item.get("source_name", "Dacia Polska")),
            "captured_on": str(
                item.get("captured_on", payload.get("captured_on", ""))
            ),
        }
    if not result:
        raise MediaCacheError("media source contains no usable models")
    return str(payload.get("captured_on", "")), result


def _cached_path(repository: Path, entry: Mapping[str, Any]) -> Path | None:
    relative = entry.get("path")
    if not isinstance(relative, str) or not relative:
        return None
    path = repository / relative
    return path if path.is_file() else None


def _download(
    url: str,
    *,
    etag: str,
    last_modified: str,
    force: bool,
    timeout: float,
) -> tuple[bytes, str, str, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/png,image/jpeg,image/svg+xml,image/*",
    }
    if etag and not force:
        headers["If-None-Match"] = etag
    if last_modified and not force:
        headers["If-Modified-Since"] = last_modified
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
        if not data:
            raise MediaCacheError("empty image response")
        content_type = (
            str(response.headers.get_content_type())
            if hasattr(response.headers, "get_content_type")
            else str(response.headers.get("Content-Type", ""))
        )
        return (
            data,
            content_type,
            str(response.headers.get("ETag", "")),
            str(response.headers.get("Last-Modified", "")),
        )


def refresh(
    repository: Path,
    *,
    offline: bool = False,
    force: bool = False,
    timeout: float = 20.0,
) -> dict[str, Any]:
    repository = repository.resolve()
    cache_directory = repository / CACHE_DIRECTORY
    cache_directory.mkdir(parents=True, exist_ok=True)
    manifest_path = repository / MANIFEST_PATH
    old_manifest = _read_json(manifest_path, optional=True)
    old_models = old_manifest.get("models", {})
    if not isinstance(old_models, dict):
        old_models = {}

    captured_on, sources = _load_sources(repository)
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    models: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}

    for model_code, source in sorted(sources.items()):
        old = old_models.get(model_code, {})
        if not isinstance(old, dict):
            old = {}
        old_path = _cached_path(repository, old)
        old_hash = str(old.get("sha256", ""))
        if old_path is not None and old_hash and _sha256(old_path.read_bytes()) != old_hash:
            raise MediaCacheError(f"cached file hash mismatch for {model_code}")

        data: bytes | None = None
        content_type = str(old.get("content_type", ""))
        etag = str(old.get("etag", ""))
        last_modified = str(old.get("last_modified", ""))
        status = ""

        if offline:
            if old_path is not None:
                status = "cached_offline"
            else:
                data = _placeholder_svg(model_code, source["model_name"])
                content_type = "image/svg+xml"
                status = "placeholder_offline"
        else:
            try:
                data, content_type, etag, last_modified = _download(
                    source["image_url"],
                    etag=etag,
                    last_modified=last_modified,
                    force=force,
                    timeout=timeout,
                )
                status = "downloaded"
            except urllib.error.HTTPError as exc:
                if exc.code == 304 and old_path is not None:
                    status = "not_modified"
                elif old_path is not None:
                    status = "cached_after_http_error"
                else:
                    data = _placeholder_svg(model_code, source["model_name"])
                    content_type = "image/svg+xml"
                    status = "placeholder_after_http_error"
            except (urllib.error.URLError, TimeoutError, OSError, MediaCacheError):
                if old_path is not None:
                    status = "cached_after_network_error"
                else:
                    data = _placeholder_svg(model_code, source["model_name"])
                    content_type = "image/svg+xml"
                    status = "placeholder_after_network_error"

        path = old_path
        digest = old_hash
        if data is not None:
            digest = _sha256(data)
            if old_path is not None and digest == old_hash:
                path = old_path
                status = "unchanged_content"
            else:
                path = cache_directory / (
                    f"{model_code}-{digest[:16]}"
                    f"{_extension(content_type, source['image_url'])}"
                )
                path.write_bytes(data)
                if old_path is not None and old_path != path:
                    old_path.unlink()
        if path is None:
            raise MediaCacheError(f"no local image available for {model_code}")

        relative = path.relative_to(repository).as_posix()
        models[model_code] = {
            **source,
            "captured_on": str(source.get("captured_on", captured_on)),
            "path": relative,
            "content_type": (
                content_type
                or mimetypes.guess_type(relative)[0]
                or "application/octet-stream"
            ),
            "sha256": digest or _sha256(path.read_bytes()),
            "etag": etag,
            "last_modified": last_modified,
            "checked_at": checked_at,
            "status": status,
        }
        statuses[model_code] = status

    referenced = {entry["path"] for entry in models.values()}
    for path in cache_directory.iterdir():
        relative = path.relative_to(repository).as_posix()
        if path.is_file() and path.name != "manifest.json" and relative not in referenced:
            path.unlink()

    manifest = {
        "version": 1,
        "source_path": SOURCE_PATH.as_posix(),
        "captured_on": captured_on,
        "checked_at": checked_at,
        "models": models,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"models": len(models), "statuses": statuses}


def verify(repository: Path) -> dict[str, Any]:
    repository = repository.resolve()
    captured_on, sources = _load_sources(repository)
    manifest = _read_json(repository / MANIFEST_PATH)
    models = manifest.get("models")
    if not isinstance(models, dict) or set(models) != set(sources):
        raise MediaCacheError("cache manifest model set differs from source")
    for model_code, source in sources.items():
        entry = models[model_code]
        if not isinstance(entry, dict):
            raise MediaCacheError(f"invalid manifest entry for {model_code}")
        if entry.get("image_url") != source["image_url"]:
            raise MediaCacheError(f"image URL differs for {model_code}")
        path = _cached_path(repository, entry)
        if path is None:
            raise MediaCacheError(f"missing cached image for {model_code}")
        if _sha256(path.read_bytes()) != entry.get("sha256"):
            raise MediaCacheError(f"cached image hash differs for {model_code}")
        if not str(entry.get("content_type", "")).startswith("image/"):
            raise MediaCacheError(f"invalid content type for {model_code}")
    return {"verified": True, "models": len(models), "captured_on": captured_on}


def data_uri(repository: Path, model_code: str) -> str:
    repository = repository.resolve()
    manifest = _read_json(repository / MANIFEST_PATH, optional=True)
    models = manifest.get("models", {})
    if not isinstance(models, dict):
        return ""
    entry = models.get(model_code)
    if not isinstance(entry, dict):
        return ""
    path = _cached_path(repository, entry)
    if path is None:
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{entry.get('content_type', 'application/octet-stream')};base64,{encoded}"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--refresh", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = (
            refresh(
                args.repository,
                offline=args.offline,
                force=args.force,
                timeout=args.timeout,
            )
            if args.refresh
            else verify(args.repository)
        )
    except (MediaCacheError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
