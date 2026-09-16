from agentic_init.merge import merge, unmerge, upsert_blocks


def test_merge_preserves_user_entries_and_deduplicates_lists():
    user = {"permissions": {"allow": ["Bash(make)"], "defaultMode": "default"}, "env": {"A": "1"}}
    ours = {"permissions": {"allow": ["Bash(make)", "Bash(git status)"]}}

    assert merge(user, ours) == {
        "permissions": {"allow": ["Bash(make)", "Bash(git status)"], "defaultMode": "default"},
        "env": {"A": "1"},
    }


def test_unmerge_removes_only_owned_values():
    owned = {"permissions": {"allow": ["Bash(git status)"], "defaultMode": "acceptEdits"}}
    current = merge({"permissions": {"allow": ["Bash(make)"]}, "env": {"A": "1"}}, owned)

    assert unmerge(current, owned) == {"permissions": {"allow": ["Bash(make)"]}, "env": {"A": "1"}}


def test_unmerge_keeps_values_the_user_changed():
    owned = {"permissions": {"defaultMode": "acceptEdits"}}

    assert unmerge({"permissions": {"defaultMode": "plan"}}, owned) == {"permissions": {"defaultMode": "plan"}}


def test_blocks_are_inserted_replaced_and_removed_without_touching_user_text():
    text = "My notes\n"
    text = upsert_blocks(text, [("a", "one"), ("b", "two")], set(), "html")
    assert text == (
        "My notes\n\n"
        "<!-- agentic_init:begin a -->\none\n<!-- agentic_init:end a -->\n\n"
        "<!-- agentic_init:begin b -->\ntwo\n<!-- agentic_init:end b -->\n"
    )

    text = upsert_blocks(text + "\nMore notes\n", [("a", "uno")], {"b"}, "html")
    assert text == "My notes\n\n<!-- agentic_init:begin a -->\nuno\n<!-- agentic_init:end a -->\n\nMore notes\n"


def test_removing_a_block_keeps_blank_lines_in_user_text():
    text = "Intro\n\n\n\nSpaced out\n\n<!-- agentic_init:begin a -->\none\n<!-- agentic_init:end a -->\n"

    assert upsert_blocks(text, [], {"a"}, "html") == "Intro\n\n\n\nSpaced out\n"
