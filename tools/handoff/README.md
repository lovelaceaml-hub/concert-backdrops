# Restore exact large Drive files

The November 22, 2026 Claude handoff preserves large originals as numbered byte
parts because the connected Drive upload route rejects files larger than
104,857,600 bytes. Parts are at most 90,000,000 bytes. Splitting changes neither
the original contents nor the video encoding; it is only a transfer format.

## Use

Download the entire relevant Drive folder. If Drive creates one or more ZIPs
for the download, extract all of them so the files are together. The folder
must contain its `TRANSFER-MANIFEST.json`, `restore_handoff.py` and every
numbered part named by the manifest. Run:

```sh
python3 restore_handoff.py
```

To restore just the full-HD Song 11 delivery:

```sh
python3 restore_handoff.py --only "Almighty_God_Knows_the_Future_Renewed_1080p60_delivery.mp4"
```

Use `--manifest /path/to/TRANSFER-MANIFEST.json` when running the script from
another directory. Use `--output-dir /path/to/restored` for a different output
folder. Python 3.8 or later and the standard library are sufficient; no network,
renderer, video tools or private key are required. Allow disk space for both
the downloaded parts and restored originals.

The script validates safe basenames, expected sizes, each part's SHA-256 and
the complete restored original's SHA-256. It leaves matching existing outputs
intact and refuses to overwrite a different existing file. It writes to a
temporary file and installs the verified output without replacing another file.
Keep the numbered parts until you have confirmed the restored outputs.

## Exact native Song 11 master

The native master was originally retained in two independently saved ZIPs.
First restore those two original ZIPs using the command above. Extract
`restore_master.py` from either restored ZIP into the same folder, then run:

```sh
python3 restore_master.py --archive-dir .
```

The resulting native MP4 is 911,865,528 bytes, SHA-256
`c553b2a51f3917d389adc51ee6dc97c96e6b6e9e306a9bfd2bfbe38a89b34c55`.
The archive's own manifest and restore helper verify its exact chunks and
complete movie. Both restoration stages were exercised on the actual files;
the handoff evidence records their hashes. This is the finished 1080p60 review
production, not an approved final 4K60 show render.

## Authority and limits

Use `project-docs/production-system/evidence/claude-drive-completion.json` for
the observed Drive IDs, transfer manifests and readback receipts. Use
`project-docs/production-system/catalogs/handoff-media.json` for original media identities and recovery gaps.
All per-folder transfer manifests retain the original names, lengths and hashes.
The source tar.gz archive is a current tracked-source snapshot, not a full Git-history
bundle; GitHub remains the history authority. Private recovery keys stay in
the separate private recovery folder and are excluded from source packages.
