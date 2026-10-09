# Sameer Exports (Aligarh) catalogue data

Extracted from two scanned product catalogues (SE 1 / SE 2 PDFs) plus brass-builders.com and the IndiaMART page.

- `images/` ~910 product cutouts, white background, enhanced (named by product code)
- `data/products_raw.json` OCR'd code, category, name/size/finish lines per product
- `data/image_flags.json` image sizes and fill ratio (low fill = check the cutout)
- `oldsite/site.json` text and image list crawled from brass-builders.com
- `scripts/` OCR, parse, crop, segment, enhance pipeline (`overrides.json` = manual boxes)

Known gaps: ~10% of cutouts have fragments; the numerals/letters page is not captured; no master CSV yet.

Business: Sameer Exports, Aligarh, UP. Proprietor Sanjeev Agarwal. GST 09ACZPA8884B1Z2, IEC 0694001716.
