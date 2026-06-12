# monorepo-manager

Private workspace utility for managing my monorepo setup.

This repository is used to control package configuration between workspace and monorepo projects, especially projects that use Yarn workspaces.

It is not a public package.
It is not intended as a general CLI tool.
It is mainly used for my own workspace automation.

## Purpose

`monorepo-manager` helps maintain consistency between packages inside my workspace.

The main focus is Yarn workspaces, dependency control, package resolutions, and shared package configuration.

## Main focus

This project is used for:

* Managing Yarn workspace package data
* Reading workspace package configuration
* Controlling dependency versions
* Managing root `resolutions`
* Comparing dependency versions between packages
* Checking internal workspace package links
* Keeping package configuration consistent
* Reducing repeated manual edits across many `package.json` files

## Target structure

This tool is intended for workspace structures like this:

```txt
workspace/
├── package.json
├── yarn.lock
├── packages/
│   ├── package-a/
│   │   └── package.json
│   ├── package-b/
│   │   └── package.json
│   └── package-c/
│       └── package.json
└── apps/
    └── app-a/
        └── package.json
```

Example root `package.json`:

```json
{
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "resolutions": {
    "typescript": "^5.0.0"
  }
}
```

## What it controls

### Workspaces

The project can be used to inspect and control workspace packages from the root workspace configuration.

Workspace data may include:

* Package name
* Package path
* Package version
* Dependencies
* Dev dependencies
* Peer dependencies
* Scripts
* Internal workspace references

### Dependencies

This project helps compare and control dependency versions across workspace packages.

Common use cases:

* Find duplicated dependency versions
* Find mismatched dependency ranges
* Keep shared dependencies aligned
* Move selected dependencies to the root package
* Detect missing dependencies in workspace packages

### Resolutions

This project is also used to manage Yarn `resolutions`.

Common use cases:

* Keep forced dependency versions in one place
* Review existing root resolutions
* Add or update package resolutions
* Avoid repeated dependency overrides across packages

Example:

```json
{
  "resolutions": {
    "typescript": "^5.0.0",
    "eslint": "^9.0.0"
  }
}
```

## Internal usage

This repository is used through internal scripts and local workspace logic.

It does not expose a fixed public command name.

The usage depends on the scripts defined in this repository or in the workspace that imports it.

Example script style:

```json
{
  "scripts": {
    "check:workspace": "node ./scripts/check-workspace.js",
    "sync:workspace": "node ./scripts/sync-workspace.js",
    "fix:resolutions": "node ./scripts/fix-resolutions.js"
  }
}
```

Run scripts with Yarn:

```bash
yarn check:workspace
yarn sync:workspace
yarn fix:resolutions
```
