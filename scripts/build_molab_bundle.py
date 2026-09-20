"""Build the versioned browser-safe payload used by both notebook entry points."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.experience_data import build_visual_payload

OUTPUT = ROOT / "data" / "molab_bundle.json"
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Recompute scientific caches")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    payload = build_visual_payload(force=args.force)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n"
    )
    temporary.replace(args.output)
    print(
        f"wrote {args.output} ({args.output.stat().st_size / 1024 / 1024:.2f} MiB, "
        f"schema {payload['schema_version']})"
    )


if __name__ == "__main__":
    main()
