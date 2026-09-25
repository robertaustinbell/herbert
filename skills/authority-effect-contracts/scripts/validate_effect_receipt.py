from __future__ import annotations

import json
import sys
from pathlib import Path

from contracts import ContractError, reject_duplicate_keys, validate_effect_receipt


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(json.dumps({"valid": False, "errors": ["usage: validate_effect_receipt.py FILE"]}))
        return 2
    try:
        value = json.loads(Path(argv[1]).read_text(), object_pairs_hook=reject_duplicate_keys)
        validate_effect_receipt(value)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "schema_version": value["schema_version"], "receipt_id": value["receipt_id"], "effect_status": value["effect_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
