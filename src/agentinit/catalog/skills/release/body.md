# Release

## Procedure
1. Confirm the working tree is clean and on the release branch.
2. Run the full verification{% for key in ["lint", "typecheck", "test", "build"] if commands[key] %}{{ ":" if loop.first }} `{{ commands[key] }}`{% endfor %}.
3. Collect changes since the last tag: `git log $(git describe --tags --abbrev=0)..HEAD --oneline`.
4. Determine the version bump (semver): breaking → major, feature → minor, fix → patch.
5. Update the changelog and version files.
6. Commit `release: vX.Y.Z` and create an annotated tag.
7. Stop. Show the human the changelog, tag and verification output. Pushing tags and deploying requires explicit approval.
