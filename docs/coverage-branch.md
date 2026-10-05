# Branch coverage

The declared coverage configuration is maintained in
[`pyproject.toml`](../pyproject.toml). The required test gate measures line
coverage and requires at least 89%; branch coverage is a separate diagnostic.
Use Python 3.14, selected by [`.python-version`](../.python-version), for
repository validation. The packaging floor does not change that requirement.

## Measuring branch coverage

An optional branch measurement can use the existing diagnostic command:

```bash
uv run pytest tests/ -q --cov=src --cov-branch --cov-report=term-missing \
  --ignore=tests/test_figure_generation.py
```

This excludes one test module, not the figure source from the coverage
denominator. Inspect the reported source set and subprocess coverage before
interpreting the result. Record the exact command, interpreter, source identity,
reported line and branch denominators, and observed result with each run.
The configured `concurrency = ["multiprocessing"]` setting alone does not
establish that every child contributed coverage data.

## Acceptance boundary

This guide claims no fresh branch-coverage measurement. Branch coverage is not
independently gated, and the 89% line-coverage requirement does not establish
branch coverage. A run with branch measurement enabled does not replace the
declared line-coverage gate or native/formal acceptance.

See [Testing](testing.md) and the [required checks](../AGENTS.md#required-checks)
for the maintained validation contract. Dated failure ledgers and prior
measurements remain historical evidence in repository history; they are not
current operating instructions.
