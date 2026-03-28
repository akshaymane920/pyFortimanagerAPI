# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.5]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.5
[0.2.4]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.4
