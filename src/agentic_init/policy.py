from agentic_init.blueprint import Policy
from agentic_init.config import Commands

READ_ONLY_GIT = ("git status", "git diff", "git log", "git show", "git branch", "git rev-parse")
DELIVERY_GIT = (
    "git add",
    "git commit",
    "git switch -c",
    "git checkout -b",
    "gh pr create",
    "gh pr view",
    "gh pr checks",
)
ALWAYS_DENIED = ("rm -rf", "sudo", "git push --force", "git push -f")
ENTERPRISE_DENIED = ("curl", "wget", "ssh", "scp")
PROTECTED_PATHS = (
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "secrets/**",
    "**/*.pem",
    "**/*.key",
    "**/credentials.json",
)


def build_policy(autonomy: int, level: int, commands: Commands) -> Policy:
    project = [c for c in (commands.test, commands.lint, commands.typecheck, commands.format, commands.build) if c]
    allowed = [*READ_ONLY_GIT, *project]
    ask = ["git reset --hard", "git clean", "git rebase"]
    denied = list(ALWAYS_DENIED)

    if autonomy >= 3:
        allowed += DELIVERY_GIT
    if autonomy >= 4:
        allowed += ["git push", "gh pr merge"]
    else:
        ask += ["git push", "gh pr merge"]
    if level >= 4:
        denied += ENTERPRISE_DENIED

    return Policy(
        edits="propose" if autonomy == 0 else "ask" if autonomy == 1 else "auto",
        allowed_commands=tuple(dict.fromkeys(allowed)),
        ask_commands=tuple(dict.fromkeys(ask)),
        denied_commands=tuple(denied),
        protected_paths=PROTECTED_PATHS,
        enterprise=level >= 4,
        sandbox="strict" if level >= 4 else "soft" if level >= 2 else "off",
    )
