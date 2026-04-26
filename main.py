"""
Lanchuang Global Monitor VR
---------------------------

Entrypoint only. Implementation lives in `globalops_vr_app/`.

Run:
  PORT=5173 python3 main.py

Scaffold only (no HTTP server):
  python3 main.py --no-serve

Cache Tripo models locally (recommended for Vercel/VR stability):
  python3 main.py --cache-tripo-assets

Open:
  http://localhost:5173/globalops_vr/
"""

from __future__ import annotations

import sys

from globalops_vr_app.scaffold import scaffold
from globalops_vr_app.server import serve
from globalops_vr_app.tripo_cache import cache_tripo_assets


def main() -> None:
    if "--cache-tripo-assets" in sys.argv:
        cache_tripo_assets()
        return
    scaffold()
    if "--no-serve" in sys.argv:
        return
    serve()


if __name__ == "__main__":
    main()
