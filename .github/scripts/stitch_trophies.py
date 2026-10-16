"""Combine single-trophy SVGs into one horizontal strip.

Usage: python3 stitch_trophies.py OUTPUT.svg GAP_PX INPUT1.svg [INPUT2.svg ...]

Each input is a one-trophy SVG from the github-profile-trophy server
(column=1, one title). Only the inputs passed in are placed, so trophies you
have not earned never leave an empty slot in the final image.
"""

import re
import sys

ROOT_SVG = re.compile(r"<svg\b([^>]*)>(.*)</svg>\s*$", re.S)
ATTR = r'{}\s*=\s*"([\d.]+)'


def read_trophy(path):
    text = open(path, encoding="utf-8").read().strip()
    match = ROOT_SVG.search(text)
    if not match:
        raise SystemExit(f"{path}: no root <svg> element found")
    attrs, body = match.groups()
    width = re.search(ATTR.format("width"), attrs)
    height = re.search(ATTR.format("height"), attrs)
    if not width or not height:
        raise SystemExit(f"{path}: root <svg> has no numeric width/height")
    return float(width.group(1)), float(height.group(1)), body


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    output, gap, inputs = sys.argv[1], float(sys.argv[2]), sys.argv[3:]

    trophies = [read_trophy(p) for p in inputs]
    total_width = sum(w for w, _, _ in trophies) + gap * (len(trophies) - 1)
    total_height = max(h for _, h, _ in trophies)

    parts = []
    x = 0.0
    for width, height, body in trophies:
        # Each trophy keeps its own coordinate system inside a nested <svg>.
        parts.append(
            f'<svg x="{x:g}" y="0" width="{width:g}" height="{height:g}" '
            f'viewBox="0 0 {width:g} {height:g}">{body}</svg>'
        )
        x += width + gap

    with open(output, "w", encoding="utf-8") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width:g}" '
            f'height="{total_height:g}" viewBox="0 0 {total_width:g} {total_height:g}" '
            f'fill="none">\n' + "\n".join(parts) + "\n</svg>\n"
        )
    print(f"{output}: {len(trophies)} trophies, {total_width:g}x{total_height:g}")


if __name__ == "__main__":
    main()
