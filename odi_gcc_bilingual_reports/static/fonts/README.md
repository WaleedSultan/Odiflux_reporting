# Arabic fonts (OFL)

Drop a license-clean Arabic font here so PDF / wkhtmltopdf / Odoo report
engine can shape Arabic glyphs correctly.

## Recommended (OFL)

1. **IBM Plex Sans Arabic** — https://github.com/IBM/plex  
   Place e.g. `IBMPlexSansArabic-Regular.ttf` (and Bold if desired) in this folder.
2. **Noto Naskh Arabic** — https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic  
   Place e.g. `NotoNaskhArabic-Regular.ttf`.

CSS `@font-face` in `static/src/css/report_bilingual.css` expects:

```
IBMPlexSansArabic-Regular.ttf
```

Rename or edit the `src:` URL to match the file you drop.

## Optional download (network / day-1 PDF spike)

If the build host allows outbound HTTPS, you can fetch OFL IBM Plex Sans Arabic:

```bash
cd static/fonts
# Example — pin a release asset URL from IBM/plex when network is available:
# wget -O IBMPlexSansArabic-Regular.ttf '<release-asset-url>'
```

Do **not** vendor proprietary fonts. Keep `LICENSE.txt` / OFL notice beside the TTF.

## Why early

Arabic shaping failures show up only on real PDF hosts (Odoo.sh / Docker).
Spike a sample bilingual invoice PDF on **day 1** before polishing layout.
