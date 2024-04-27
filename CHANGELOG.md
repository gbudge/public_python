<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

<!-- Example...
## [Unreleased]

### Added

- v1.1 Brazilian Portuguese translation.

### Changed

- Use frontmatter title & description in each language version template

### Removed

- Trademark sign previously shown after the project description in version 0.3.0
-->

## [1.0.1] - 2024-04-27

### Added

- [`Dockerfile`](Dockerfile) and [`docker-compose.yaml`](docker-compose.yaml).
- [`CHANGELOG.md`](CHANGELOG.md) file.

### Changed

- Moved `kubernetes_labels_emitter.py` to [`app/k8s_labels.py`](app/k8s_labels.py).
- Updated [`README.md`](README.md) with [`k8s_labels.py`](app/k8s_labels.py) docs.
- Updated [`k8s_labels.py`](app/k8s_labels.py) to use container timezone.

## [1.0.0] - 2024-04-26

### Added

- Initial release.
