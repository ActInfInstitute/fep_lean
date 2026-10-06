# Frozen test-only validator

`h2_r0_custody_99e5cdf.py.txt` contains the exact Git bytes of
`tests/_support/h2_r0_custody.py` at commit
`99e5cdf0690bebf219a49b598d9d80ff1da075d5`.
Its SHA-256 is
`5c9452c8f9120ba0ae53adf19e35f1929701281a3891d2ef0cd1b1bd9523aabb`.
The repository's `.gitattributes` disables text conversion for this resource.

`custody_fixture_knobs.py` checks that digest before loading the captured bytes
under an isolated module name. It uses the historical validator only to build
disposable synthetic pre-H3 unit inputs. Production validators and immutable
historical receipts remain unchanged. Fabricated reviews, JUnit records, and
source bindings establish no native, scientific, or publication acceptance.

When the pinned commit is available locally, verify the resource against Git
with:

```bash
git show 99e5cdf0690bebf219a49b598d9d80ff1da075d5:tests/_support/h2_r0_custody.py \
  | cmp - tests/_support/resources/h2_r0_custody_99e5cdf.py.txt
```
