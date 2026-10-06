"""Read-only, stdlib test-resource membership guard for capture wrappers.

The same function bodies can be embedded in reviewed private wrappers. There
are no project imports, approval inference, source writes or producer calls.
"""

import os
import stat
from pathlib import Path

TESTS_EXCLUDED_DIRECTORIES = frozenset(
    {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
)
TESTS_EXCLUDED_SUFFIXES = frozenset({".pyc", ".pyo"})


def _tests_identity(value):
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def _tests_relative(value):
    if (
        type(value) is not str
        or not value.startswith("tests/")
        or "\\" in value
        or "\x00" in value
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise ValueError("noncanonical tests roster member")
    return value


def tests_members(root, *, budget=lambda: None, observations=None):
    """Enumerate all test resources with descriptor-relative, no-follow reads.

    Exclusions match the maintained capture planner, case insensitively.
    A symlink, FIFO, replaced directory or nonregular resource fails closed.
    Descendant descriptors and identities are retained until full scan closure.
    """
    root = Path(root)
    if not root.is_absolute() or str(root) != os.path.normpath(str(root)):
        raise ValueError("canonical absolute tests owner required")
    budget()
    descriptors = []
    ancestors = []
    members = []
    directories = []
    resources = []
    captured = {}
    visited = 0
    try:
        descriptor = os.open(root.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(descriptor)
        for index, name in enumerate((*root.parts[1:], "tests")):
            budget()
            before = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode):
                raise ValueError("tests ancestry is not an owned directory")
            child = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            descriptors.append(child)
            if _tests_identity(before) != _tests_identity(os.fstat(child)):
                raise ValueError("tests ancestry changed while opening")
            ancestors.append(
                (descriptor, name, child, before, index == len(root.parts) - 1)
            )
            descriptor = child

        def visit(parent, relative, depth):
            nonlocal visited
            budget()
            if depth > 128:
                raise ValueError("tests resource depth exceeds guard bound")
            before = os.fstat(parent)
            names = sorted(os.listdir(parent))
            directories.append((parent, relative, before, names))
            for name in names:
                budget()
                visited += 1
                if visited > 100000:
                    raise ValueError("tests resource count exceeds guard bound")
                if (
                    name.casefold() in TESTS_EXCLUDED_DIRECTORIES
                    or Path(name).suffix.casefold() in TESTS_EXCLUDED_SUFFIXES
                ):
                    continue
                member = _tests_relative(relative + "/" + name)
                observed = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if stat.S_ISDIR(observed.st_mode):
                    child = os.open(
                        name,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                        dir_fd=parent,
                    )
                    descriptors.append(child)
                    if _tests_identity(observed) != _tests_identity(os.fstat(child)):
                        raise ValueError("tests directory changed while opening")
                    ancestors.append((parent, name, child, observed, True))
                    visit(child, member, depth + 1)
                elif stat.S_ISREG(observed.st_mode):
                    members.append(member)
                    resources.append((parent, name, observed))
                    captured[member] = _tests_identity(observed)
                else:
                    raise ValueError("tests resource is nonregular or a symlink")
            budget()
            if names != sorted(os.listdir(parent)) or _tests_identity(
                before
            ) != _tests_identity(os.fstat(parent)):
                raise ValueError("tests directory changed during enumeration")

        visit(descriptor, "tests", 0)
        # Recheck every earlier child after the last root listing. Closing a
        # child early leaves late nested additions and replacements invisible.
        for parent, relative, before, names in directories:
            budget()
            if names != sorted(os.listdir(parent)) or _tests_identity(
                before
            ) != _tests_identity(os.fstat(parent)):
                raise ValueError("tests directory changed during full scan closure")
            captured[relative] = _tests_identity(before)
        for parent, name, before in resources:
            budget()
            if _tests_identity(before) != _tests_identity(
                os.stat(name, dir_fd=parent, follow_symlinks=False)
            ):
                raise ValueError("tests resource changed during full scan closure")
        for parent, name, child, before, owned in reversed(ancestors):
            budget()
            # Ancestors above tests may acquire unrelated entries. Their inode
            # and mode must still be the originally opened directory.
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if (before.st_dev, before.st_ino, before.st_mode) != (
                current.st_dev,
                current.st_ino,
                current.st_mode,
            ) or _tests_identity(current) != _tests_identity(os.fstat(child)):
                raise ValueError("tests ancestry replaced during enumeration")
            if owned and _tests_identity(before) != _tests_identity(current):
                raise ValueError("tests directory changed during full scan closure")
        if observations is not None:
            observations.update(captured)
        return sorted(members)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def require_tests_roster(
    root, frozen_files, recorded_roster=None, *, budget=lambda: None, observations=None
):
    """Reject additions/deletions; never baseline the observed directory."""
    if type(frozen_files) is not dict:
        raise ValueError("exact frozen file map required")
    if any(type(name) is not str for name in frozen_files):
        raise ValueError("frozen file names must be strings")
    expected = sorted(
        _tests_relative(name) for name in frozen_files if name.startswith("tests/")
    )
    if not expected:
        raise ValueError("approved tests roster is empty")
    if recorded_roster is not None and (
        type(recorded_roster) is not list or recorded_roster != expected
    ):
        raise ValueError("recorded tests roster differs from frozen file map")
    actual = tests_members(root, budget=budget, observations=observations)
    if actual != expected:
        raise ValueError(
            "complete approved tests membership differs: additions="
            + repr(sorted(set(actual) - set(expected)))
            + "; deletions="
            + repr(sorted(set(expected) - set(actual)))
        )
    return expected


def require_planned_tests_roster(
    root, frozen_files, recorded_roster, stages, *, budget=lambda: None
):
    """Bind actual native/Python inputs and directory rosters before dispatch."""
    expected = require_tests_roster(root, frozen_files, recorded_roster, budget=budget)
    owner = str(Path(root) / "tests")
    wanted = sorted(str(Path(root) / name) for name in expected)
    selected = [stage for stage in stages if stage.name in ("native", "python")]
    if sorted(stage.name for stage in selected) != ["native", "python"]:
        raise ValueError("native/Python planned tests stages are absent")
    for stage in selected:
        rosters = [
            list(names)
            for directory, names in stage.input_rosters
            if directory == owner
        ]
        inputs = sorted(name for name in stage.inputs if name.startswith(owner + "/"))
        if rosters != [wanted] or inputs != wanted:
            raise ValueError(
                "maintained planned tests membership differs from approved freeze"
            )
    return expected


def read_regular_nofollow(
    path, *, owner=None, budget=lambda: None, max_bytes=512 * 1024 * 1024
):
    """Read a bounded regular file through retained, no-follow ancestry.

    Paths keep their lexical ownership; no resolve/read-by-path handoff occurs.
    O_NONBLOCK prevents a raced FIFO substitution from blocking before fstat.
    Every ancestor and the leaf must retain the same identity through closure.
    """
    path = Path(path)
    owner = path.parent if owner is None else Path(owner)
    if (
        not path.is_absolute()
        or str(path) != os.path.normpath(str(path))
        or len(path.parts) < 2
        or len(path.parts) > 128
        or type(max_bytes) is not int
        or max_bytes < 0
        or not owner.is_absolute()
        or str(owner) != os.path.normpath(str(owner))
        or not path.is_relative_to(owner)
    ):
        raise ValueError("canonical absolute bounded regular input required")
    budget()
    descriptors = []
    ancestors = []
    try:
        parent = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptors.append(parent)
        ancestry = Path(path.anchor)
        for name in path.parts[1:-1]:
            budget()
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode):
                raise ValueError("regular input ancestry is nonregular or a symlink")
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent
            )
            descriptors.append(child)
            ancestry = ancestry / name
            owned = ancestry.is_relative_to(owner)
            opened = os.fstat(child)
            if (before.st_dev, before.st_ino, before.st_mode) != (
                opened.st_dev,
                opened.st_ino,
                opened.st_mode,
            ) or (owned and _tests_identity(before) != _tests_identity(opened)):
                raise ValueError("regular input ancestry changed while opening")
            ancestors.append((parent, name, child, before, owned))
            parent = child
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or not 0 <= before.st_size <= max_bytes:
            raise ValueError("input is not a bounded regular file")
        leaf = os.open(
            path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent
        )
        descriptors.append(leaf)
        opened = os.fstat(leaf)
        if not stat.S_ISREG(opened.st_mode) or _tests_identity(
            before
        ) != _tests_identity(opened):
            raise ValueError("input changed or is nonregular before bounded read")
        parts = []
        remaining = opened.st_size + 1
        while remaining:
            budget()
            part = os.read(leaf, min(remaining, 1024 * 1024))
            budget()
            if not part:
                break
            parts.append(part)
            remaining -= len(part)
        data = b"".join(parts)
        if (
            len(data) != opened.st_size
            or _tests_identity(before) != _tests_identity(os.fstat(leaf))
            or _tests_identity(before)
            != _tests_identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False))
        ):
            raise ValueError(
                "input identity/length changed during bounded no-follow read"
            )
        for parent, name, child, before, owned in reversed(ancestors):
            budget()
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            opened = os.fstat(child)
            # Above the declared owner, unrelated directory membership may
            # change. Keep its original inode/mode and live pathname binding;
            # within the owner require the full original identity as well.
            stable = (
                (before.st_dev, before.st_ino, before.st_mode)
                == (
                    current.st_dev,
                    current.st_ino,
                    current.st_mode,
                )
                == (opened.st_dev, opened.st_ino, opened.st_mode)
            )
            if not stable or (
                owned
                and not (
                    _tests_identity(before)
                    == _tests_identity(opened)
                    == _tests_identity(current)
                )
            ):
                raise ValueError("regular input ancestry changed during read")
        return data
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
