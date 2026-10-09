# Sameer Exports (Aligarh) catalogue data

Extracted from two scanned product catalogues (SE 1 / SE 2 PDFs) plus brass-builders.com and the IndiaMART page.

- `images/` ~910 product cutouts, white background, enhanced (named by product code)
- `data/products_raw.json` OCR'd code, category, name/size/finish lines per product
- `data/image_flags.json` image sizes and fill ratio (low fill = check the cutout)
- `oldsite/site.json` text and image list crawled from brass-builders.com
- `scripts/` OCR, parse, crop, segment, enhance pipeline (`overrides.json` = manual boxes)

## Website
`site/` is a static e-commerce catalogue (about 1,000 pages: home, shop with search and filters, 65 category pages, 910 product pages, a quote cart, blog, about, finishes, export, FAQ, contact, privacy and terms). Rebuild with `python build_site.py`. Preview: `python -m http.server 8765 -d site`.

There are no prices: the business quotes per order, so the cart is a quote list that sends an email enquiry.

## Data
`data/products.csv` / `products.json`: code, section, category, name, size, finish, image, catalogue page.

Known gaps: the numerals/letters page (codes like SE-0004) is not captured; chrome/silver items use a whitened rectangle crop rather than a cutout; OCR text was not hand-proofed.

Business: Sameer Exports, C-235, Ramghat Road, UPSIDC Sector 2, Talanagri, Aligarh 202002. Phone +91-571-2513295, info@brass-builders.com. Proprietor Sanjeev Agarwal. GST 09ACZPA8884B1Z2, IEC 0694001716.
