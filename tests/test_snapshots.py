import os
from pathlib import Path

import pytest
from conftest import configure

from agentic_init.config import Mode, Modules
from agentic_init.engine import build

SNAPSHOTS = Path(__file__).parent / "snapshots"
CASES = {
    "l0-greenfield": dict(level=0, mode=Mode.GREENFIELD),
    "l1-greenfield": dict(level=1, mode=Mode.GREENFIELD),
    "l2-brownfield-aidlc": dict(level=2, mode=Mode.BROWNFIELD, modules=Modules(aidlc=True)),
    "l3-greenfield-bmad": dict(level=3, mode=Mode.GREENFIELD, modules=Modules(bmad=True), enrich=True),
    "l4-brownfield": dict(level=4, mode=Mode.BROWNFIELD),
}


def render(root: Path) -> str:
    changes = sorted(build(root).plan.pending, key=lambda c: c.path)
    return "".join(f"=== {c.path}{' (executable)' if c.executable else ''}\n{c.after}\n" for c in changes)


@pytest.mark.parametrize("case", CASES)
def test_generated_output_matches_snapshot(python_project, case):
    configure(python_project, **CASES[case])
    snapshot = SNAPSHOTS / f"{case}.txt"

    output = render(python_project)

    if os.environ.get("UPDATE_SNAPSHOTS") or not snapshot.exists():
        SNAPSHOTS.mkdir(exist_ok=True)
        snapshot.write_text(output)
    assert output == snapshot.read_text()
