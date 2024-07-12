<!-- Links -->
[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html

# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

Dates are formatted as: DD/MM/YYYY

<!-- Example...
## [Unreleased]

### Added

- v1.1 Brazilian Portuguese translation.

### Changed

- Use frontmatter title & description in each language version template

### Removed

- Trademark sign previously shown after the project description in version 0.3.0
-->

## 05/07/2024

v2.2.0: 

### Added

* `.gitignore` file.

### Changed

* Documentation format update in `README.md`.
* Reorganised files.

## 14/05/2024

v2.1.0: Bug fixes and support for OS syslog.

### Added

* k8s_labels: Added export `EV_LOGGER_SYSLOG` environment variable. When set to 1, will use Python syslog library when emitting events. Default is to not use syslog.

### Changed

* k8s_labels: Improved handling of sub-keys to be more reliable.
- k8s_labels: Sub-key indexes must exist with double underscore. Example: `APP_CONTOSO_MS_INVENTORY__0__NAME` instead of `APP_CONTOSO_MS_INVENTORY_0_NAME`.

## 12/05/2024

v2.0.0: Major envar_logger update to support additional configuration options and quality improvements.


### Changed

* k8s_labels: Renamed to envar_logger.
* envar_logger: Missing mandatory environment variables no longer warns only. Now error and exit.
* envar_logger: --interval is no longer supported. Use EV_LOGGER_INTERVAL instead.
* envar_logger: --indent is no longer supported. Use EV_LOGGER_INDENT instead.

### Added

* envar_logger: Added EV_LOGGER_PREFIX. Define the logging prefix. No longer uses "app.kubernetes.io" prefix.
* envar_logger: Added EV_LOGGER_INTERVAL=0 to emit only once and then exit as successful.
* envar_logger: Additional range and value checks for interval and json indentation.
* envar_logger: Add version numbering. Included in first line output.

### Removed

* envar_logger: Sample environment variables in the app code. Set via docker-compose.yaml instead.
* envar_logger: All command line parameters. Replaced by environment variables.

## 27/04/2024

v1.0.1: Minor repo reorganisation.

### Added

- [`Dockerfile`](Dockerfile) and [`docker-compose.yaml`](docker-compose.yaml).
- [`CHANGELOG.md`](CHANGELOG.md) file.

### Changed

- Moved `kubernetes_labels_emitter.py` to [`app/k8s_labels.py`](app/k8s_labels.py).
- Updated [`README.md`](README.md) with [`k8s_labels.py`](app/k8s_labels.py) docs.
- Updated [`k8s_labels.py`](app/k8s_labels.py) to use container timezone.

## 26/04/2024

v1.0.0: Initial commits.

### Added

- Initial release.
