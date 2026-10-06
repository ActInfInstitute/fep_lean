# Capture tests roster guard

CUR-03 requires the complete approved `tests/` resource membership to equal the
test subset of the frozen input map. `roster_guard.py` provides a stdlib-only,
read-only guard suitable for embedding into separately reviewed capture
wrappers. It never derives approval from the files it discovers.

The guard opens each ancestor and subtree through POSIX directory descriptors
with `O_NOFOLLOW`, retains descendant descriptors until full scan closure,
revalidates all directory membership/identities and resources, and rejects
symlinks and special files. Optional observations bind complete directory/file
identities so wrappers can bracket their entire hashing pass, including changes
that are restored before the closing observation.
It uses the maintained planner's case-insensitive cache and bytecode exclusions.
`read_regular_nofollow` retains the complete descriptor ancestry, uses
`O_NOFOLLOW | O_NONBLOCK` for the leaf, and reads at most its opened size plus
one byte under the caller deadline. It checks full identities within the
declared owner and original inode/mode plus live pathname binding above it.
The default finite file bound is 512 MiB; callers may keep a tighter bound.

Each native and Python plan must bind the same exact input list and directory
roster. Callers supply their existing deadline callback.

Integration must record the complete tests roster in both plan and freeze and
compare complete membership and identity observations around every full source
hashing pass; check it before helper/project imports, before and after planning, immediately
before dispatch, and during closing source observations. The surrounding
wrapper retains responsibility for approved hashes, source identity, original
stage caps, native/scientific roster boundaries, and no-resume behavior. This
guard alone supplies neither execution acceptance nor byte custody.

The successor must retain the original 560 inputs and explicitly approve the
previously missing `tests/fixtures/formalism_catalogue_155_reviewed_deltas.json`
plus all new test modules/resources in the final reviewed public source map.
Unknown additions and deletions fail closed. Adding these tooling files to a
publication packet also requires explicit approval and union membership.

Run disposable controls without repository conftest or maintained owner imports:

```bash
uv run --no-sync pytest -c /dev/null -p no:cacheprovider \
  --confcutdir=specs/capture-roster-guard \
  specs/capture-roster-guard/test_roster_guard.py -q
uv run --no-sync ruff check specs/capture-roster-guard
uv run --no-sync ruff format --check specs/capture-roster-guard
```

Independent source review and actual final-source capture remain separate gates.
No private operator locations, capture source, or production receipts belong in
this public slice.
