from __future__ import annotations

import json
import sys
from pathlib import Path

from contracts import ContractError, reject_duplicate_keys, check_authority_subset


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(json.dumps({"valid": False, "errors": ["usage: check_authority_subset.py PARENT CHILD"]}))
        return 2
    try:
        parent = json.loads(Path(argv[1]).read_text(), object_pairs_hook=reject_duplicate_keys)
        child = json.loads(Path(argv[2]).read_text(), object_pairs_hook=reject_duplicate_keys)
        errors = check_authority_subset(parent, child)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        errors = [str(exc)]
    result = {"valid": not errors, "errors": errors}
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
