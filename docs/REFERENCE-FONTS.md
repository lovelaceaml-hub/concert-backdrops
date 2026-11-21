# Exact fonts for the registered concert studies

In a fresh isolated checkout, after installing the documented host tools, run:

```bash
python3 scripts/bootstrap.py --p3d-only --reference-fonts
```

This uses the locked Python environment and pinned npm packages, reconstructs
the exact 74 historical TTF files required by the registered studies, and runs
the p3d dependency check. It does not start a render or configure a GPU provider.
Restore the selected private recording separately before producing a video.

## Why the explicit mode exists

The original study fonts were converted from the pinned Fontsource WOFF2 files
with historical `head.created` and `head.modified` values. Normal deterministic
conversion preserves the timestamps embedded in the WOFF2 source. Its visible
font data can match while its complete file checksum differs from the historical
reference. The frozen study renderer correctly rejects different input bytes.

[study-fonts.json](../project-docs/production-system/catalogs/study-fonts.json)
records each original WOFF2 checksum, historical head timestamps and expected
TTF checksum. All 74 historical files were reconstructed exactly from the pinned
Cormorant Garamond, Jost and Outfit 5.3.0 packages. All tables were independently
compared; only the head table differed between normal conversion and those
historical files. No binary font archive is needed for this reconstruction.

The tested converter runtime is fontTools 4.68.0 in the locked Python environment.
The source and output checksums remain the acceptance rule on another host.
Different converter versions are not assumed to reproduce the same bytes.

## Conversion and validation

To reconstruct into a separate directory without running the whole bootstrap:

```bash
uv run --frozen --extra legacy python tools/setup_fonts.py \
  node_modules/@fontsource work/reference-font-check --reference-fonts
```

The converter checks the complete source file set and every source checksum.
It builds all fonts in a temporary directory with `recalcTimestamp=False`, sets
only the recorded head timestamps, then checks every reconstructed TTF before
publishing any file. Invalid source bytes, timestamp metadata or expected output
hashes fail before existing destination files change. Unexpected TTF files in
the destination are reported and preserved. Files already matching the expected
reference are left untouched, including their modification times.

Use an isolated checkout for setup while a production round is active. The
reference mode was proved in new ignored directories; the active render's font
hashes, sizes and modification times were checked unchanged.

Without `--reference-fonts`, the converter retains its normal deterministic
behavior and preserves WOFF2 timestamps:

```bash
uv run --frozen --extra legacy python tools/setup_fonts.py \
  node_modules/@fontsource work/source-timestamp-fonts
```

If reference reconstruction fails, keep the failed-run evidence and check the
pinned package versions, source hashes and converter environment. Do not replace
the expected catalog hashes simply to make a changed font pass.

The focused regression tests use a real, original synthetic WOFF2 fixture and
exercise exact reconstruction, altered source/metadata rejection, preservation
of existing outputs, deterministic default conversion and bootstrap forwarding:

```bash
uv run --frozen --extra legacy python -m unittest discover \
  -s tests/pipeline -p test_reference_fonts.py -v
```
