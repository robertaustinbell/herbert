from __future__ import annotations

import json
import sys
from pathlib import Path

from contracts import ContractError, reject_duplicate_keys, validate_authority_manifest


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"valid": False, "errors": ["usage: validate_authority_manifest.py FILE"]}))
        return 2
    try:
        value = json.loads(Path(argv[1]).read_text(), object_pairs_hook=reject_duplicate_keys)
        validate_authority_manifest(value, require_active=True)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "schema_version": value["schema_version"], "manifest_id": value["manifest_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
