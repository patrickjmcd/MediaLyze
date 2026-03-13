# Changelog

All notable changes to this project will be documented in this file.

## vUnreleased

### ✨ New

- Continue documenting changes here until the next tagged release is prepared.

### 🐛 Bug fixes

## v0.1.1

>2026-03-13

### ✨ New

- Added official GitHub release support with tag-driven publishing and curated release notes.
- Added a release metadata validation script to keep Docker, backend, and frontend versions aligned.
- Added release PR validation in GitHub Actions so version and changelog mismatches fail before merge.

### 🐛 Bug fixes

- Switched official Docker publishing for `main` from branch-triggered builds to SemVer tag releases.
- Updated the dev image workflow to derive its base version from Git tags instead of GHCR package APIs.
- Normalized the repository version metadata to `0.1.1` ahead of the first official public release.

## v0.1.0

>2026-03-13

### ✨ New

### 🐛 Bug fixes
