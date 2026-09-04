# vigilfont.com

Vigil is licensed under the SIL Open Font License 1.1. See OFL.txt.

Single-page marketing site for **Vigil**, a softened geometric grotesk by Keno Vigil. Static HTML/CSS/JS, no build step.

- `index.html` — the page (hero, type tester, weights, rounding story, in-use, character set, notes index, download)
- `notes/` — one file per post, served at `/notes/{slug}` via `cleanUrls`. `notes/index.html` is the index at `/notes`
- `notes.css` — shared styles for every Notes page. Font `src` paths must stay absolute (`/fonts/…`); posts live one level deep, where a relative path would 404
- `fonts/` — variable WOFF2 (roman + italic), 16 static WOFF2, Vigil Outline Regular + Italic
- `downloads/Vigil.zip` — the full family package
- `vercel.json` — clean URLs, long cache on fonts, attachment header on downloads

Deploy: `vercel --prod` from this folder.

Vigil is released under the SIL Open Font License 1.1. Derived from [Figtree](https://github.com/erikdkennedy/figtree) by Erik Kennedy.
