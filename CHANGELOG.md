# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Test suite (`tests/`, pytest) covering request shape for every API method, using a mocked HTTP session.
- CI workflow running the tests on Python 3.9–3.13 for pushes and pull requests; PyPI upload now runs tests first.
- `FortiManagerLoginError`, raised when login fails instead of failing later with `AttributeError`.
- `vdom` parameter on `add_dynamic_object` / `update_dynamic_object` (default `root`).

### Fixed

- `logout` reuses the logged-in session (proxies/cookies) and clears session state, so a later `login()` works.
- `get_services` returned only a hard-coded `Custom_Service_1`; it now returns all custom services.
- Header/footer policy getters built `.../policy5` instead of `.../policy/5` when `policyid` was given.
- `get_policies_assigned_to_device` crashed if called before login and ignored the configured adom.
- `add_dynamic_object` / `update_dynamic_object` ignored the configured adom and sent `comment` as the string `"None"`.
- `update_dynamic_object` / `update_address_group` / `update_address_v6_group` raise `ValueError` on an invalid `do` instead of sending a malformed or no-op request.
- `update_firewall_address_v6_object(subnet=...)` sent `subnet` instead of the IPv6 field `ip6`.
- `add_device` sent the description `"False"` when none was given.
- `run_script_on_single_device` sends `scope` as a list, as the API expects.
- `set_adom()` with no argument silently set the adom to `None`; the argument is now required.

### Removed

- `/tests` from `.gitignore`, which had been preventing tests from being committed.

## [0.2.7] - 2026-03-29

### Fixed

- PyPI upload failures (HTTP 400) when GitHub Actions used the latest `3.x` Python (e.g. 3.14): publish workflow now builds on **Python 3.12** with pinned `setuptools`, strict `twine check`, and clearer `twine`/publish logging.
- Declare `license='MIT'` in `setup.py` for consistent package metadata.

## [0.2.6] - 2026-03-29

### Added

- Module-level `__version__` string for runtime introspection.

### Changed

- `custom_api`: build a copy of the caller's payload before adding `session`, so the original dict is not mutated.
- MIT `LICENSE.txt`: copyright notice updated to 2022–2026.

### Fixed

- CI: PyPI upload runs on `push` of `v*` tags (in addition to `release: published`) so uploads are not skipped when the GitHub Release is created with the default `GITHUB_TOKEN`.

## [0.2.5] - 2026-03-29

### Fixed

- Use `self.verify` for all API `requests` calls (replacing hard-coded `verify=False`).
- Avoid mutable default arguments: `FortiManager(..., proxies=None)`, `add_address_group` / `add_address_v6_group` use `members=None` with a fresh list when omitted.
- `add_dynamic_object`: `subnet` is a required parameter (the old default was accidentally the built-in `list` type).

### Changed

- `make_data`: map kwargs with explicit lookups; unknown keys raise `KeyError` with a hint. Invalid `_for` raises `ValueError`.
- Policy field mapping includes `source_address6` / `destination_address6` for updates aligned with dual-stack policies.

### Removed

- Unused `functools.wraps` import.

## [0.2.4] - 2026-03-29

### Added

- `add_firewall_address_object`: optional `fqdn` parameter for FQDN-type IPv4 address objects (mutually exclusive with `subnet`). Default API type is `"fqdn"` when `fqdn` is set.
- `make_data` / `show_params_for_object_update`: support for `fqdn` when updating address objects.

### Fixed

- `update_firewall_address_object` and `update_firewall_address_v6_object` now send valid JSON-RPC bodies using `json=payload` instead of `repr(payload)` with `data=`.
- `move_firewall_policy`: removed incorrect defaults (`int` type used as placeholder). `policyid` is required; a clear `TypeError` is raised if it is omitted.

### Changed

- `.gitignore`: ignore `.venv` for local virtual environments.

[0.2.7]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.7
[0.2.6]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.6
[0.2.5]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.5
[0.2.4]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.4
