from agentic_init.config import Config, Selection

AIDLC = Selection(skills=["evidence-gate"], hooks=["verify-completion"], docs=["evidence"])
ENRICH = Selection(skills=["agentic_init-enrich"])


def module_selections(config: Config) -> list[Selection]:
    selections = []
    if config.modules.aidlc:
        selections.append(AIDLC)
    if config.enrich:
        selections.append(ENRICH)
    return selections
