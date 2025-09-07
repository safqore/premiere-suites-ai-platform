"""Generate responsive hero image variants from a single large source image.

Usage:
    python -m scripts.generate_responsive_hero_images \
        --source src/demo/premieresuites-website-new.jpeg \
        --outdir src/demo/images \
        --widths 640 960 1280 1440 1600 1920 2560 2880 3200
"""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ModuleNotFoundError as e:
    raise SystemExit(
        "Pillow is not installed.\n"
        "Install with: pip install Pillow\n"
        "Then re-run."
    ) from e

# Extended default widths (matches your srcset)
DEFAULT_WIDTHS = [640, 960, 1280, 1440, 1600, 1920, 2560, 2880, 3200]

def generate_variants(
    source: Path,
    outdir: Path,
    widths: List[int],
    quality: int = 82,
    webp_quality: int = 80
):
    outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(source).convert("RGB")
    base_name = source.stem

    original_w, original_h = img.size
    print(f"Source loaded: {original_w}x{original_h}")

    results = []
    for requested_w in widths:
        target_w = min(requested_w, original_w)  # avoid upscale
        if target_w == original_w:
            # Use original if already at or below original width
            if requested_w > original_w:
                print(f"Skip upscale request {requested_w}px (using original width {original_w}px instead)")
            resized = img.copy()
            target_h = original_h
        else:
            ratio = target_w / original_w
            target_h = int(original_h * ratio)
            resized = img.resize((target_w, target_h), Image.LANCZOS)

        jpeg_path = outdir / f"{base_name}-{target_w}.jpg"
        resized.save(jpeg_path, format="JPEG", quality=quality, optimize=True, progressive=True)
        results.append(jpeg_path)

        # WebP
        try:
            webp_path = outdir / f"{base_name}-{target_w}.webp"
            resized.save(webp_path, format="WEBP", quality=webp_quality, method=6)
            results.append(webp_path)
        except Exception as ex:
            print(f"[warn] WebP save failed for {target_w}px: {ex}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Generate responsive hero images")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--widths", nargs="*", type=int, default=DEFAULT_WIDTHS)
    parser.add_argument("--quality", type=int, default=82, help="JPEG quality (default 82)")
    parser.add_argument("--webp-quality", type=int, default=80, help="WebP quality (default 80)")
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"Source image not found: {args.source}")

    results = generate_variants(args.source, args.outdir, args.widths, args.quality, args.webp_quality)

    print("\nGenerated files:")
    for p in results:
        print(" -", p.name)

    base_name = args.source.stem
    produced_jpg_widths = sorted({int(p.stem.split("-")[-1]) for p in results if p.suffix == ".jpg"})
    produced_webp_widths = sorted({int(p.stem.split("-")[-1]) for p in results if p.suffix == ".webp"})

    webp_srcset = ", ".join([f"images/{base_name}-{w}.webp {w}w" for w in produced_webp_widths])
    jpg_srcset = ", ".join([f"images/{base_name}-{w}.jpg {w}w" for w in produced_jpg_widths])
    largest = max(produced_jpg_widths)

    print("\n<-- Copy for <img srcset> (JPEG only) -->\n")
    print(jpg_srcset)

    print("\n<-- Copy for <picture> (WebP + JPEG fallback) -->\n")
    print('<picture>')
    if webp_srcset:
        print(f'  <source type="image/webp" srcset="{webp_srcset}" sizes="100vw">')
    print(f'  <img src="images/{base_name}-{largest}.jpg" ')
    print(f'       srcset="{jpg_srcset}" sizes="100vw" alt="Premier Suites Homepage demo" ')
    print('       loading="eager" fetchpriority="high" decoding="async">')
    print('</picture>')

if __name__ == "__main__":
    main()