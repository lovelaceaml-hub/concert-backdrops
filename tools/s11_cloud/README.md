# Song 11: parallel cloud pictures with encrypted delivery

This isolated adapter renders the same frozen `s11_renewed` scene on GitHub's
standard Ubuntu workers. It does not change the local full-song renderer.
Only checked analysis maps are sent to the picture workers. The original MP3,
prepared WAV and artifact decryption key remain in owner-controlled storage.

## Privacy and execution boundary

The repository is public. The two tracked NPZ files contain derived time,
level, band, onset, beat and pitch estimates, not waveform samples. Public
source plus these maps makes the silent scene reproducible. Artifact encryption
protects the produced video bytes; it does not conceal the published scene code
or analysis. These checked analysis inputs and scene source are part of the public project.

Every uploaded artifact is a CMS envelope using AES-256-GCM authenticated
encryption and RSA-OAEP SHA256 key transport. Only `recipient.pem`, a public
certificate, is tracked. The private key belongs under ignored
`work/s11_cloud/private/`, with restricted file permissions. Preserve that key
privately before launching: encrypted output cannot be recovered without it.
No plaintext MP4, frame sheet, audio or private key is uploaded by this workflow.

The workflow responds only to changes to `tools/s11_cloud/request.json` on
`creative/s11-renewed-20261122`. It has read-only repository permission, one-day
artifact retention, no persistent Actions cache and no automatic publication.
Standard public-runner compute is free; artifact storage has a separate account
allowance; this workflow retains artifacts for one day.

## Stage and review a request locally

With the exact prepared recording and scene already available:

```bash
.venv/bin/python -m tools.s11_cloud.freeze --id s11-renewed-20261123-probe --mode probe
```

This verifies the original recording and prepared score hashes locally, copies
only the two analysis maps and their provenance, records all picture source,
font and model hashes, and creates a public recipient certificate plus a local
private key if neither exists. It makes no network mutation or Git commit.

Review the actual request and source changes before committing. The only
intended tracked binary inputs are `inputs/features.npz` (471,549 bytes) and
`inputs/music_fx.npz` (574,386 bytes). A request-file commit starts one native
probe job at 58, 105.7, 118.8, 186 and 205 seconds. Download its encrypted ZIP
artifact, extract the `.tar.cms`, then decrypt with:

```bash
.venv/bin/python -m tools.s11_cloud.assemble \
  --encrypted work/s11_cloud/downloaded-probe \
  --key work/s11_cloud/private/recipient-private.pem \
  --out work/s11_cloud/probe-review --probe-only
```

The images are under the reported `probe-review-verified-parts` directory.
Inspect the native pictures before freezing a `render` request. The full request
uses 40 contiguous chunks with at most 20 jobs in parallel, one render process
per 4-CPU/16-GB runner, with two Mesa threads and one thread each for BLAS,
OMP and Numba. The initial probe used one Mesa thread; its distinct runtime
fingerprint remains a separate record. Smaller jobs reduce the effect of slow scenes and keep
artifact downloads manageable. Exact duration depends on scene cost and queues.

## Full run and local assembly

After the remote probe is reviewed, freeze a new ID with `--mode render` and
commit only the deliberate new request plus any reviewed input updates. The
same local key pair is retained. Do not change picture source during a run.

Download and unzip every encrypted part artifact into a directory, then run:

```bash
.venv/bin/python -m tools.s11_cloud.assemble \
  --encrypted work/s11_cloud/downloaded-parts \
  --key work/s11_cloud/private/recipient-private.pem \
  --out work/s11_cloud/Almighty_God_Knows_the_Future_Cloud_1080p60.mp4
```

Assembly authenticates envelopes before extraction, verifies inventories and
checksums, rejects mixed request/runtime fingerprints, checks contiguous native
60-fps picture ranges, and adds the actual locally verified 275-second score.
It does not mix local fallback chunks with remote chunks. Full decode, final
audio alignment, encoded visual review and owner approval are separate checks.

The remote manifest records Python 3.12.14, every pinned Python package,
GitHub runner image, platform, Mesa, FFmpeg, OpenSSL, source/assets/font hashes,
analysis hashes, picture clock and output settings. Different host graphics or
encoder versions are explicit; cross-machine pixel equality is not assumed.

## Primary references

- [Public standard runner capacity and free compute](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
- [Actions concurrency limits](https://docs.github.com/en/actions/reference/limits)
- [Separate artifact storage allowance](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Who can download public-repository artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts)
- [Available exact Python builds](https://github.com/actions/python-versions/blob/main/versions-manifest.json)
- [OpenSSL CMS encryption and RSA-OAEP options](https://docs.openssl.org/3.5/man1/openssl-cms/)
