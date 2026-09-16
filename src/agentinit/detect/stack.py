import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

LANGUAGE_MARKERS = {
    "package.json": "javascript",
    "tsconfig.json": "typescript",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "setup.py": "python",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "Gemfile": "ruby",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "kotlin",
    "composer.json": "php",
    "mix.exs": "elixir",
    "pubspec.yaml": "dart",
}

LOCKFILES = {
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "bun.lock": "bun",
    "bun.lockb": "bun",
    "package-lock.json": "npm",
    "uv.lock": "uv",
    "poetry.lock": "poetry",
    "Pipfile.lock": "pipenv",
}

FRAMEWORKS = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "svelte": "Svelte",
    "@angular/core": "Angular",
    "express": "Express",
    "fastify": "Fastify",
    "@nestjs/core": "NestJS",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "axum": "Axum",
    "actix-web": "Actix",
    "gin-gonic/gin": "Gin",
}

MANIFESTS = ("pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "Gemfile")

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".rs",
    ".go",
    ".rb",
    ".java",
    ".kt",
    ".php",
    ".ex",
    ".exs",
    ".dart",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".cs",
    ".swift",
    ".scala",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".claude",
    ".next",
    ".turbo",
    "vendor",
    "coverage",
}

SOURCE_FILE_CAP = 1000


@dataclass(frozen=True)
class Stack:
    languages: tuple[str, ...] = ()
    package_managers: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()

    def uses(self, language: str) -> bool:
        return language in self.languages

    def manager(self, *candidates: str) -> str | None:
        return next((m for m in self.package_managers if m in candidates), None)


def read_package_json(root: Path) -> dict:
    try:
        return json.loads((root / "package.json").read_text())
    except (OSError, ValueError):
        return {}


def _package_managers(root: Path, languages: list[str]) -> list[str]:
    managers = [manager for lock, manager in LOCKFILES.items() if (root / lock).exists()]
    if "javascript" in languages and not {"pnpm", "yarn", "bun", "npm"} & set(managers):
        managers.append("npm")
    pyproject = root / "pyproject.toml"
    if pyproject.exists() and "[tool.uv]" in pyproject.read_text() and "uv" not in managers:
        managers.append("uv")
    if "python" in languages and not {"uv", "poetry", "pipenv"} & set(managers):
        managers.append("pip")
    if "rust" in languages:
        managers.append("cargo")
    if "go" in languages:
        managers.append("go")
    return list(dict.fromkeys(managers))


def _frameworks(root: Path) -> list[str]:
    package = read_package_json(root)
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    manifests = "\n".join((root / m).read_text() for m in MANIFESTS if (root / m).exists())
    found = []
    for hint, framework in FRAMEWORKS.items():
        in_manifest = re.search(rf"(?<![\w-]){re.escape(hint)}(?![\w-])", manifests, re.I)
        if hint in dependencies or in_manifest:
            found.append(framework)
    return found


def detect_stack(root: Path) -> Stack:
    languages = list(
        dict.fromkeys(language for marker, language in LANGUAGE_MARKERS.items() if (root / marker).exists())
    )
    return Stack(
        languages=tuple(languages),
        package_managers=tuple(_package_managers(root, languages)),
        frameworks=tuple(_frameworks(root)),
    )


def count_source_files(root: Path) -> int:
    count = 0
    for _, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        count += sum(Path(name).suffix in SOURCE_EXTENSIONS for name in files)
        if count >= SOURCE_FILE_CAP:
            return SOURCE_FILE_CAP
    return count
