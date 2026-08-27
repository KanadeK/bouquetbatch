# Development and release notes

## Local gate

```console
uv sync --locked --dev
uv run python scripts/check.py
```

The gate is one entry point shared by developers and CI.

## Source-backed tooling choices

Packaging follows the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/). CI follows the [official uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/) and [GitHub's Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python). Release creation follows the [GitHub CLI release manual](https://cli.github.com/manual/gh_release_create).

Action tags and commit SHAs were checked on 2026-08-27:

- actions/checkout v7.0.1: 3d3c42e5aac5ba805825da76410c181273ba90b1
- actions/setup-python v7.0.0: 5fda3b95a4ea91299a34e894583c3862153e4b97
- astral-sh/setup-uv v9.0.0: c771a70e6277c0a99b617c7a806ffedaca235ff9

Future updates should verify tag-to-commit mapping before changing a pin.

## Release checklist

1. Update version and changelog.
2. Run the locked quality gate.
3. Create an annotated version tag containing release notes.
4. Push the commit and tag.
5. Wait for CI and Release workflows.
6. Verify wheel, source archive, and examples ZIP publicly.
7. Install the downloaded wheel in a clean environment and run the complete example.

The tag workflow reruns the complete gate before publishing assets.
