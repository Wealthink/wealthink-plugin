#!/usr/bin/env python3
"""Gzip+Base64 encode/decode a Wealthink `custom_layout` component.

Wealthink stores a report's layout as a **gzip-compressed, then base64-encoded**
TypeScript/React component string in the template's `custom_layout` field
(compressed + encoded to keep the API payload small). Once base64-decoded the
stored value begins with the gzip magic `H4sI…`. Use this helper so the agent
never has to re-implement the encoding:

  - Before saving: encode the .tsx you wrote, then pass the output to
    `update_template(custom_layout=<gzip+b64>)`.
  - When learning a reference template's branding: decode its `custom_layout`
    back to readable TSX.

Usage
-----
  python3 b64.py encode Component.tsx     # encode a file  -> prints gzip+base64
  python3 b64.py encode < Component.tsx   # encode stdin   -> prints gzip+base64
  python3 b64.py decode layout.b64        # decode a file  -> prints TSX
  python3 b64.py decode < layout.b64      # decode stdin   -> prints TSX

Notes
-----
  - Encode: gzip (mtime=0 for deterministic output) then single-line ASCII base64.
  - Decode: base64-decode, then gunzip. For backward compatibility it also
    accepts a legacy plain-base64 (non-gzip) payload and returns it as-is.
  - Decoding tolerates whitespace/newlines in the input.
"""
import base64
import gzip
import io
import sys


def encode(raw: bytes) -> str:
    buf = io.BytesIO()
    # mtime=0 keeps the output byte-stable across runs (no embedded timestamp).
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        gz.write(raw)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def decode(raw: bytes) -> str:
    cleaned = b"".join(raw.split())  # strip any whitespace/newlines
    data = base64.b64decode(cleaned)
    if data[:2] == b"\x1f\x8b":  # gzip magic — current format
        data = gzip.decompress(data)
    # else: legacy plain-base64 payload, already the raw TSX bytes
    return data.decode("utf-8")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in ("encode", "decode"):
        sys.exit("usage: b64.py encode|decode [file]   (reads stdin if no file)")

    mode = args[0]
    if len(args) > 1:
        with open(args[1], "rb") as fh:
            raw = fh.read()
    else:
        raw = sys.stdin.buffer.read()

    sys.stdout.write(encode(raw) if mode == "encode" else decode(raw))


if __name__ == "__main__":
    main()
