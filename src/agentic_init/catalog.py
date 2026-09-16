from dataclasses import dataclass
from pathlib import Path

import yaml

from agentic_init.config import ConfigError, Kind

CATALOG_DIR = Path(__file__).parent / "catalog"
METADATA = "component.yaml"


@dataclass(frozen=True)
class CatalogItem:
    kind: Kind
    name: str
    path: Path
    meta: dict

    @property
    def description(self) -> str:
        return self.meta["description"]

    def template_names(self) -> list[str]:
        return sorted(
            p.relative_to(CATALOG_DIR).as_posix()
            for p in self.path.rglob("*")
            if p.is_file() and p.name != METADATA and "__pycache__" not in p.parts
        )


def available(kind: Kind) -> list[str]:
    return sorted(p.parent.name for p in (CATALOG_DIR / kind.value).glob(f"*/{METADATA}"))


def load(kind: Kind, name: str) -> CatalogItem:
    path = CATALOG_DIR / kind.value / name
    if not (path / METADATA).exists():
        raise ConfigError(f"Unknown {kind.value[:-1]} '{name}'. Available: {', '.join(available(kind))}")
    return CatalogItem(kind, name, path, yaml.safe_load((path / METADATA).read_text()))
