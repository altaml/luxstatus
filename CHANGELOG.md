# Changelog

All notable changes to the Microphone Status Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2024-08-27

### Added
- Complete rewrite with secure, port-free architecture
- Cross-platform support (Windows and macOS)
- Smart filtering to eliminate false positives from apps with mic permission
- System tray integration with intuitive right-click menu
- Status widget for detailed information
- Timed status overrides (30min, 1hr, 2hr)
- GitHub Actions for automated builds
- Comprehensive user documentation
- Professional installers for both platforms

### Changed
- Migrated from Flask-based API to direct system integration
- Improved microphone detection accuracy
- Simplified Luxafor integration (single process)
- Enhanced UI with better status indicators
- Removed network dependencies for improved security

### Fixed
- False positive detection from Slack and other apps
- CPU usage optimization
- Memory leak in long-running sessions
- Luxafor connection stability

### Removed
- Web API interface (replaced with secure local-only operation)
- Port-based communication
- Legacy virtual environment approach for Luxafor

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Basic microphone monitoring
- Luxafor flag support
- Web-based API
- Windows support only

---

## Release Types

- **Major (X.0.0)**: Breaking changes, major features, architectural changes
- **Minor (0.X.0)**: New features, improvements, non-breaking changes
- **Patch (0.0.X)**: Bug fixes, security patches, minor improvements
