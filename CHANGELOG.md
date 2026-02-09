# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.5] - 2026-02-09

### Fixed

- 修复 Windows 导出失败：`/api/generate` 改为使用内存流生成 docx，避免临时文件句柄锁冲突。
- 新增回归测试，确保导出接口持续使用内存流输出。

### Added

- Electron desktop release hardening (permission and navigation controls).
- Runtime log persistence and log export IPC bridge.
- macOS notarization scaffolding and hardened runtime entitlements.
- GitHub Actions desktop release workflow for macOS, Windows, and Linux.
- Legal documents: privacy policy and EULA.

## [0.1.0] - 2026-02-09

### Added

- Initial desktop packaging support for Electron + bundled FastAPI backend.
