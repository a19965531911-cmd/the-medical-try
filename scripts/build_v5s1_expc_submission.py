"""Build the Experiment C candidate without changing frozen V5S.1 decisions."""

import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.build_v5s_submission import build_source as build_frozen_source
from v5s.expc_overlay import OVERLAY_SOURCE


TARGETS = {"265", "555", "755", "805", "855"}
SHELL = ROOT / "submission/a_test_message_bundle_v5s1_candidate.json"
OUT = ROOT / "submission/a_test_message_bundle_v5s1_expc_candidate.json"


def parse_datetime(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def canonical_datetime(value):
    return parse_datetime(value).astimezone(timezone.utc).isoformat(
        timespec="seconds"
    ).replace("+00:00", "Z")


def hours_before(value, hours):
    return (parse_datetime(value) - timedelta(hours=hours)).astimezone(
        timezone.utc
    ).isoformat(timespec="seconds").replace("+00:00", "Z")


def months_before(value, months):
    dt = parse_datetime(value)
    whole = int(months)
    month_index = dt.year * 12 + dt.month - 1 - whole
    year, month = divmod(month_index, 12)
    month += 1
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    shifted = dt.replace(year=year, month=month, day=min(dt.day, days[month - 1]))
    shifted -= timedelta(days=(months - whole) * 30.4375)
    return shifted.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def build_source(cid, title, identifier):
    source = build_frozen_source(str(cid), title, identifier)
    if str(cid) in TARGETS:
        source += OVERLAY_SOURCE
    compile(source, title, "exec")
    return source


def main():
    bundle = json.loads(SHELL.read_text(encoding="utf-8"))
    count = 0
    for entry in bundle["entry"]:
        resource = entry["resource"]
        if resource.get("resourceType") != "Library":
            continue
        cid = str(resource["content"][0]["title"])
        source = build_source(cid, resource["name"], resource.get("identifier", {}))
        resource["content"][0]["data"] = base64.b64encode(source.encode("utf-8")).decode("ascii")
        count += 1
    assert count == 16
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
