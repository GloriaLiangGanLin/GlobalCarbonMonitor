from __future__ import annotations

import json
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Tuple

from .config import OUT_DIR


def _download(url: str, dest: Path) -> Tuple[bool, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Skip if already cached and non-trivial.
        if dest.exists() and dest.stat().st_size > 1000:
            return True, "cached"

        req = urllib.request.Request(url, headers={"User-Agent": "GlobalOpsVR/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        dest.write_bytes(data)
        if dest.stat().st_size < 1000:
            return False, "downloaded-but-too-small"
        return True, "downloaded"
    except Exception as e:  # noqa: BLE001
        return False, f"error: {e}"


def cache_tripo_assets(
    src_json: Path | None = None,
    out_json: Path | None = None,
    models_dir: Path | None = None,
    overwrite_output_json: bool = True,
) -> None:
    """
    Convert expiring Tripo signed URLs into locally hosted GLBs.

    Reads the existing `globalops_vr/tripo_assets.json` (legacy shape with `landmark_*` keys),
    downloads each model into `globalops_vr/models/`, then rewrites `tripo_assets.json` into
    the supported "mapping" shape:
      { "globeIcon": { cityKey: "./models/xxx.glb" }, "detailLandmark": { cityKey: "./models/xxx.glb" } }
    """

    src_json = src_json or (OUT_DIR / "tripo_assets.json")
    out_json = out_json or (OUT_DIR / "tripo_assets.json")
    models_dir = models_dir or (OUT_DIR / "models")

    if not src_json.exists():
        raise FileNotFoundError(f"Missing {src_json}")

    raw = json.loads(src_json.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Invalid tripo_assets.json (expected object)")

    # Backup the original JSON once (so you can restore remote URLs if needed).
    if overwrite_output_json and src_json.resolve() == out_json.resolve():
        backup = OUT_DIR / "tripo_assets.remote.json"
        if not backup.exists():
            shutil.copyfile(src_json, backup)

    ok = 0
    fail = 0
    globe_icon: Dict[str, str] = {}
    detail_landmark: Dict[str, str] = {}

    for k, v in raw.items():
        if not isinstance(k, str) or not k.startswith("landmark_"):
            continue
        city_key = k.replace("landmark_", "", 1)
        if not isinstance(v, dict):
            continue
        resources = v.get("resources") if isinstance(v.get("resources"), dict) else {}
        url = resources.get("pbr_model") or resources.get("model")
        if not isinstance(url, str) or not url.startswith("http"):
            continue

        dest_name = f"tripo_{city_key}.glb"
        dest_path = models_dir / dest_name
        success, reason = _download(url, dest_path)
        if success:
            ok += 1
            rel = f"./models/{dest_name}"
            globe_icon[city_key] = rel
            detail_landmark[city_key] = rel
            print(f"[tripo-cache] {city_key}: {reason} -> {rel}")
        else:
            fail += 1
            print(f"[tripo-cache] {city_key}: {reason}", file=sys.stderr)

    if ok == 0:
        # Avoid overwriting the source file with an empty mapping.
        raise SystemExit("[tripo-cache] no models cached (all downloads failed). Signed URLs may be expired.")

    out_obj: Dict[str, Any] = {"globeIcon": globe_icon, "detailLandmark": detail_landmark}
    out_json.write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[tripo-cache] done. ok={ok} fail={fail} wrote={out_json}")

