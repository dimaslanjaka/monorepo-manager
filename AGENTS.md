## Repository rules

This repository contains multiple workspaces.

### Root workspace vs. Package workspaces

- **Root workspace**: files outside `packages/*` (e.g., `package.json`, `yarn.lock`, `README.md`, `AGENTS.md`, `.github/workflows/*`, `scripts/*`).
- **Package workspaces**: every directory inside `packages/*` is an **independent Git repository**.

### Critical scope rule

**When the user does NOT ask for a path inside `packages/*`, do NOT execute any command under `packages/*`.**
Operate on the **root workspace only**.

If the user asks about `package.json`, `yarn.lock`, or `README.md`, do not touch anything inside `packages/`.

---

## Important Git rule

When the user asks to commit, push, pull, stash, tag, check status, or inspect Git history for a path inside `packages/`, always move into the related package directory first.

Correct pattern:

```bash
cd packages/<workspace-name>
git status
git add .
git commit -m "..."
```

Wrong pattern:

```bash
git add packages/<workspace-name>
git commit -m "..."
```

The wrong pattern may commit from the root repository instead of the independent package repository.

---

## How to detect the workspace

If the user mentions a path like:

```txt
packages/ai-toolkit/src/index.ts
```

The workspace name is:

```txt
ai-toolkit
```

So Git commands must run from:

```bash
cd packages/ai-toolkit
```

---

## Commit workflow for packages

For any requested commit inside `packages/<workspace-name>`:

```bash
cd packages/<workspace-name>
git status
git add <requested-files>
git commit -m "<commit-message>"
```

If the user asks to commit all changes inside that package:

```bash
cd packages/<workspace-name>
git status
git add .
git commit -m "<commit-message>"
```

---

## Root repository workflow

Only run Git commands from the repository root when the requested files are outside `packages/*`.

Root-level examples:

```txt
package.json
yarn.lock
README.md
AGENTS.md
.github/workflows/*
scripts/*
```

For these files, use the root repository. **Do not include any `packages/*` files.**

---

## Mixed changes

If changes exist both in the root repository and inside `packages/*`, treat them as separate Git repositories.

Do not create one commit for all changes from the root.

Use separate commits:

```bash
git status
git add <root-files>
git commit -m "<root-commit-message>"
```

Then commit package changes from each package directory:

```bash
cd packages/<workspace-name>
git status
git add .
git commit -m "<package-commit-message>"
```

---

## Safety rules

Before committing, always check:

```bash
git status
```

Before staging files inside `packages/*`, always confirm the current directory is the package directory:

```bash
pwd
git rev-parse --show-toplevel
```

The Git top-level path must match:

```txt
.../packages/<workspace-name>
```

If it points to the root workspace instead, stop and change directory into the correct package first.

---

## Summary

- `packages/*` contains independent Git repositories.
- **If the user does not mention `packages/*`, do not execute anything under `packages/*`.**
- Git commands for package files must run inside `packages/<workspace-name>`.
- Do not commit package changes from the root repository.
- Root Git commands are only for root-level files.
- Mixed root and package changes require separate commits.