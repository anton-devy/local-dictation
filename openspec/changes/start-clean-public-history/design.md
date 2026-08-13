## Context

See proposal.md. The current repository is a clean, audited public-preview snapshot, but its
reachable and unreachable Git objects remain private development history. No remote, tags, or public
release currently exist. The vault archive remains available after the transition.

## Goals / Non-Goals

**Goals:**

- Publish only an auditable current tree with a single public root commit.
- Verify the actual bytes, Git object graph, package checks, and GitHub settings before replacing the
  normal checkout.
- Keep the former private checkout until all public publication gates have passed.

**Non-Goals:**

- Preserve private commit history in the public repository.
- Reimplement application behavior, publish packages to PyPI, or distribute an app bundle.
- Retain a second private Git mirror after the verified transition.

## Decisions

- Build a separate staging repository rather than reinitializing the private checkout in place. This
  avoids destructive operations while preparing and reviewing the public root; the alternative would
  leave a window where the only working copy had been replaced.
- Copy the current tracked snapshot only, preserving modes and symlinks, then initialize a new Git
  object database. This prevents historic objects, reflogs, remotes, tags, notes, ignored files, and
  dangling blobs from entering the public repository.
- Use `Anton Lang <289793190+anton-devy@users.noreply.github.com>` for the one root commit. The
  prior personal email never appears in the public history.
- Treat the root commit as a `chore:` baseline. Python Semantic Release must not create a release for
  it; later Conventional Commit feature/fix changes may release through the protected-main workflow.
- After remote verification, replace the normal checkout with a fresh clone and delete the former
  private checkout. The vault archive is the approved retained history.

## Risks / Trade-offs

- [The staging tree could accidentally contain private content] → Generate it from `git ls-files`,
  inspect its complete tracked list, and run content/path scans before commit and push.
- [The public initial push could trigger an unwanted release] → Use a `chore:` root commit and verify
  workflow behavior in GitHub Actions before deleting the private checkout.
- [Release documentation can drift from automation] → Align README and semantic-release config with
  the checked-in release workflow before the public root commit.
- [A remote or GitHub settings action requires user authority] → Stop at that gate until the empty
  repository URL and needed authorization are available.
