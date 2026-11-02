"""Sanity-check style-tokens.yaml and TEMPLATE_RESUME.md.

Fails (non-zero exit) if a required key or heading is missing, or if a text
color has less than 4.5:1 contrast against white.
"""
import re
import sys
import yaml

REQUIRED_TOP = ["palette", "fonts", "sizes_pt", "layout"]
REQUIRED_COLORS = ["primary", "secondary_text", "body", "tint", "on_primary"]
REQUIRED_HEADINGS = ["Profile", "Technical Skills", "Experience", "Education"]


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    errors = []
    with open("style-tokens.yaml") as fh:
        tokens = yaml.safe_load(fh)

    for key in REQUIRED_TOP:
        if key not in tokens:
            errors.append(f"style-tokens.yaml: missing top-level key '{key}'")

    palette = tokens.get("palette", {})
    for key in REQUIRED_COLORS:
        if key not in palette:
            errors.append(f"palette: missing '{key}'")

    for key in ("primary", "secondary_text", "body"):
        if key in palette:
            ratio = contrast(palette[key], "#FFFFFF")
            status = "ok" if ratio >= 4.5 else "FAIL"
            print(f"{key:15} {palette[key]}  {ratio:4.2f}:1 on white  {status}")
            if ratio < 4.5:
                errors.append(f"palette.{key} contrast {ratio:.2f}:1 is below 4.5:1")

    with open("TEMPLATE_RESUME.md") as fh:
        template = fh.read()
    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"^##\s+{re.escape(heading)}\b", template, re.M):
            errors.append(f"TEMPLATE_RESUME.md: missing '## {heading}' heading")

    if errors:
        print("\nValidation failed:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
