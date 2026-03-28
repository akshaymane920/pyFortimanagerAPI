# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2026-03-29

### Added

- `add_firewall_address_object`: optional `fqdn` parameter for FQDN-type IPv4 address objects (mutually exclusive with `subnet`). Default API type is `"fqdn"` when `fqdn` is set.
- `make_data` / `show_params_for_object_update`: support for `fqdn` when updating address objects.

### Fixed

- `update_firewall_address_object` and `update_firewall_address_v6_object` now send valid JSON-RPC bodies using `json=payload` instead of `repr(payload)` with `data=`.
- `move_firewall_policy`: removed incorrect defaults (`int` type used as placeholder). `policyid` is required; a clear `TypeError` is raised if it is omitted.

### Changed

- `.gitignore`: ignore `.venv` for local virtual environments.

[0.2.4]: https://github.com/akshaymane920/pyFortiManagerAPI/releases/tag/v0.2.4
