import re
from typing import Any

_REMOVED = object()


def merge(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            merged[key] = merge(base[key], value) if key in base else value
        return merged
    if isinstance(base, list) and isinstance(overlay, list):
        return base + [item for item in overlay if item not in base]
    return overlay


def unmerge(base: Any, owned: Any) -> Any:
    if isinstance(base, dict) and isinstance(owned, dict):
        remaining = {}
        for key, value in base.items():
            if key not in owned:
                remaining[key] = value
                continue
            result = unmerge(value, owned[key])
            emptied = result in ({}, []) and value not in ({}, [])
            if result is not _REMOVED and not emptied:
                remaining[key] = result
        return remaining
    if isinstance(base, list) and isinstance(owned, list):
        return [item for item in base if item not in owned]
    return _REMOVED if base == owned else base


COMMENT_STYLES = {
    "html": ("<!-- agentinit:begin {id} -->", "<!-- agentinit:end {id} -->"),
    "hash": ("# agentinit:begin {id}", "# agentinit:end {id}"),
}


def comment_style(path: str) -> str:
    return "html" if path.endswith((".md", ".mdx", ".html")) else "hash"


def _block_pattern(block_id: str, style: str) -> re.Pattern:
    begin, end = (re.escape(m.format(id=block_id)) for m in COMMENT_STYLES[style])
    return re.compile(rf"{begin}\n.*?{end}\n?", re.S)


def _remove_block(text: str, block_id: str, style: str) -> str:
    while match := _block_pattern(block_id, style).search(text):
        before, after = text[: match.start()], text[match.end() :]
        if before.endswith("\n\n") and after.startswith("\n") or not after:
            before = before[:-1] if before.endswith("\n\n") else before
        elif not before:
            after = after.removeprefix("\n")
        text = before + after
    return text


def upsert_blocks(text: str, blocks: list[tuple[str, str]], remove: set[str], style: str) -> str:
    for block_id in remove:
        text = _remove_block(text, block_id, style)
    appended = []
    for block_id, body in blocks:
        begin, end = (m.format(id=block_id) for m in COMMENT_STYLES[style])
        rendered = f"{begin}\n{body.strip()}\n{end}\n"
        pattern = _block_pattern(block_id, style)
        if pattern.search(text):
            text = pattern.sub(lambda _, replacement=rendered: replacement, text, count=1)
        else:
            appended.append(rendered)
    if appended:
        head = text.rstrip("\n")
        text = (f"{head}\n\n" if head else "") + "\n".join(appended)
    return text
