import difflib
import json
import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from agentinit.lock import Lock, digest
from agentinit.merge import comment_style, merge, unmerge, upsert_blocks
from agentinit.targets.base import FileOp, Strategy


class Action(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UNCHANGED = "unchanged"
    SKIP = "skip"


PENDING = (Action.CREATE, Action.UPDATE, Action.DELETE)


@dataclass(frozen=True)
class Change:
    path: str
    action: Action
    before: str | None
    after: str | None
    reason: str = ""
    executable: bool = False

    def diff(self) -> str:
        lines = difflib.unified_diff(
            (self.before or "").splitlines(keepends=True),
            (self.after or "").splitlines(keepends=True),
            fromfile=f"a/{self.path}",
            tofile=f"b/{self.path}",
        )
        return "".join(lines)


@dataclass(frozen=True)
class Plan:
    changes: list[Change]
    lock: Lock

    @property
    def pending(self) -> list[Change]:
        return [c for c in self.changes if c.action in PENDING]

    @property
    def skipped(self) -> list[Change]:
        return [c for c in self.changes if c.action == Action.SKIP]


def _read(root: Path, path: str) -> str | None:
    file = root / path
    return file.read_text() if file.is_file() else None


def _transition(path: str, before: str | None, after: str, executable: bool = False) -> Change:
    if before is None:
        return Change(path, Action.CREATE, None, after, executable=executable)
    action = Action.UNCHANGED if before == after else Action.UPDATE
    return Change(path, action, before, after, executable=executable)


def _owned(op: FileOp, before: str | None, entry: dict | None, force: bool) -> tuple[Change, dict | None]:
    change = _transition(op.path, before, op.content, op.executable)
    if change.action == Action.UPDATE and not force:
        if entry is None:
            return Change(op.path, Action.SKIP, before, op.content, "exists and is not managed by agentinit"), None
        if digest(before) != entry["hash"]:
            return Change(op.path, Action.SKIP, before, op.content, "modified locally"), entry
    return change, {"strategy": op.strategy, "hash": digest(op.content)}


def _blocks(op: FileOp, before: str | None, entry: dict | None) -> tuple[Change, dict]:
    desired = [(block.id, block.body) for block in op.blocks]
    stale = set(entry["blocks"] if entry else []) - {block_id for block_id, _ in desired}
    after = upsert_blocks(before or "", desired, stale, comment_style(op.path))
    return _transition(op.path, before, after), {"strategy": op.strategy, "blocks": [b for b, _ in desired]}


def _json(op: FileOp, before: str | None, entry: dict | None) -> tuple[Change, dict | None]:
    try:
        current = json.loads(before) if before else {}
    except ValueError:
        return Change(op.path, Action.SKIP, before, None, "invalid JSON, fix it and re-run"), entry
    merged = merge(unmerge(current, entry["owned"] if entry else {}), op.data)
    new_entry = {"strategy": op.strategy, "owned": op.data}
    if before is not None and merged == current:
        return Change(op.path, Action.UNCHANGED, before, before), new_entry
    return _transition(op.path, before, json.dumps(merged, indent=2) + "\n"), new_entry


def _retire(path: str, before: str | None, entry: dict, force: bool) -> Change | None:
    if before is None:
        return None
    match entry["strategy"]:
        case Strategy.OWNED if force or digest(before) == entry["hash"]:
            return Change(path, Action.DELETE, before, None)
        case Strategy.OWNED:
            return Change(path, Action.SKIP, before, before, "no longer generated but modified locally; left in place")
        case Strategy.BLOCKS:
            after = upsert_blocks(before, [], set(entry["blocks"]), comment_style(path))
        case Strategy.JSON:
            try:
                current = json.loads(before)
            except ValueError:
                return Change(path, Action.SKIP, before, before, "invalid JSON, fix it and re-run")
            remaining = unmerge(current, entry["owned"])
            after = json.dumps(remaining, indent=2) + "\n" if set(remaining) - {"$schema"} else ""
        case _:
            return None
    if not after.strip():
        return Change(path, Action.DELETE, before, None)
    return _transition(path, before, after)


def plan(root: Path, ops: list[FileOp], lock: Lock, force: bool = False) -> Plan:
    changes, files = [], {}
    for op in ops:
        before, entry = _read(root, op.path), lock.files.get(op.path)
        match op.strategy:
            case Strategy.OWNED:
                change, new_entry = _owned(op, before, entry, force)
            case Strategy.BLOCKS:
                change, new_entry = _blocks(op, before, entry)
            case Strategy.JSON:
                change, new_entry = _json(op, before, entry)
            case Strategy.SEED:
                change, new_entry = _transition(op.path, before, before or op.content), None
        changes.append(change)
        if new_entry:
            files[op.path] = new_entry

    generated = {op.path for op in ops}
    for path, entry in lock.files.items():
        if path not in generated and (change := _retire(path, _read(root, path), entry, force)):
            changes.append(change)
            if change.action == Action.SKIP and entry["strategy"] == Strategy.JSON:
                files[path] = entry
    return Plan(changes, Lock(files=files))


def apply(root: Path, plan: Plan) -> None:
    for change in plan.pending:
        file = root / change.path
        if change.action == Action.DELETE:
            file.unlink()
            continue
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(change.after)
        if change.executable:
            file.chmod(file.stat().st_mode | 0o111)
    for directory in {(root / c.path).parent for c in plan.pending if c.action == Action.DELETE}:
        while directory != root and directory.is_dir() and not any(directory.iterdir()):
            os.rmdir(directory)
            directory = directory.parent
    plan.lock.save(root)
