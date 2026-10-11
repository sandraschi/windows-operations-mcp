"""Console output decoding for Windows native command-line tools.

Windows console programs (reg.exe, net.exe, netsh, icacls, schtasks, wmic,
expand.exe, ...) print text in the *console output code page*, which is not
UTF-8. On a Simplified-Chinese Windows install that code page is cp936 (GBK);
on a Western install it is usually cp1252.

Decoding those bytes as UTF-8 silently corrupts every non-ASCII character into
the U+FFFD replacement character. That garbles user-facing messages and, worse,
breaks any downstream logic that matches on error text (see
windows_registry._reg, which detects a missing key by matching an English
error string).

This module centralises the correct decoding so every subprocess call site can
share one implementation.
"""

from __future__ import annotations

import locale
import os
import sys

__all__ = ["console_encoding", "decode_windows_output"]

_REPLACEMENT = chr(0xFFFD)


def console_encoding() -> str:
    """Return the code page Windows console programs are currently writing in.

    Preference order:
      1. WINOPPS_OUTPUT_ENCODING - explicit operator override.
      2. The ANSI/OEM code page for this process (locale.getpreferredencoding
         with do_setlocale=False so it reflects the OS rather than Python UTF-8
         mode).
      3. mbcs - Windows ANSI code page alias.

    Returns:
        An encoding name usable with bytes.decode.
    """
    override = os.environ.get("WINOPPS_OUTPUT_ENCODING")
    if override:
        return override

    try:
        # do_setlocale=False keeps this OS-derived rather than locale-module state.
        pref = locale.getpreferredencoding(do_setlocale=False)
        if pref:
            return pref
    except Exception:  # pragma: no cover - defensive
        pass

    if sys.platform == "win32":
        return "mbcs"
    return "utf-8"


def decode_windows_output(raw: bytes | str | None) -> str:
    """Decode bytes captured from a Windows native tool or child process.

    Tries, in order: an explicit override, UTF-8 (correct when a command ran
    after chcp 65001), the OS console code page, then a few common Windows
    encodings. A candidate is only accepted when it yields no replacement
    characters, so lossy encodings such as cp1252/latin-1 cannot mask a GBK
    payload.

    Args:
        raw: Raw bytes from a subprocess pipe, an already-decoded string, or None.

    Returns:
        Decoded text with surrounding whitespace stripped; "" when there was no
        output.
    """
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if not raw:
        return ""

    candidates: list[str] = []
    override = os.environ.get("WINOPPS_OUTPUT_ENCODING")
    if override:
        candidates.append(override)
    candidates.append("utf-8")
    candidates.extend([console_encoding(), "mbcs", "gbk", "cp936", "cp1252", "latin-1"])

    seen: set[str] = set()
    for enc in candidates:
        if not enc:
            continue
        key = enc.lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            text = raw.decode(enc)
        except (UnicodeDecodeError, LookupError, ValueError):
            continue
        if _REPLACEMENT not in text:
            return text.strip()

    # Last resort: never raise, but leave the replacement chars visible.
    return raw.decode("utf-8", errors="replace").strip()
