<p align="center">
  <a href="https://fontzz.vercel.app"><img alt="fontzz" src="docs/img/banner.png"></a>
</p>

<h1 align="center">fontzz</h1>

<p align="center">Thirty original type families drawn entirely in code (sans, serif, Didone, Art Deco, dot matrix, two monospaced), every weight from 100 to 900, with a one-page site to try them and hand them to your agent. <a href="https://fontzz.vercel.app">fontzz.vercel.app</a></p>

## Tech stack

- Python generator in `type/`: every glyph is parametric, three masters (Thin, Regular, Black) per family, no font editor involved; serifs, flares, ball terminals, slant, fixed-width spacing and dot-matrix sampling are all parameters
- fontmake builds the variable font, fontTools and skia-pathops cut the nine static weights, kerning comes from glyph side profiles
- Each family: 285 characters (Latin-1, Latin Extended-A subset, figures, currency, arrows), WOFF2 at 9 to 37 KB
- Every TTF and WOFF2 passes OTS, the sanitizer Chrome and Firefox run on web fonts
- `site/`: Vite 5, React 18, TypeScript, plain CSS, no UI library, about 62 KB of gzipped JS

## Cloning & running

1. Clone: `git clone https://github.com/Luffixos/fontzz.git && cd fontzz`
2. Run the site: `npm --prefix site install && npm --prefix site run dev`, then open http://localhost:5178
3. Set up the generator: `python3 -m venv .venv && .venv/bin/pip install -r type/requirements.txt`
4. Rebuild every family into `site/public`: `cd type && ../.venv/bin/python release.py`
5. Rebuild one family while drawing: `../.venv/bin/python release.py halden`, then check it with `../.venv/bin/python cmp.py out/cmp.png 400`

## Roadmap

- [ ] add stencil and inline display families
- [ ] hint the statics so small sizes on Windows look as crisp as the variable font
- [ ] add italics, starting with Halden and Folio
- [ ] add code ligatures and a slashed zero to Signal and Tally
- Cyrillic and Greek are skipped for now: I'd rather finish Latin properly than ship three half-done scripts.

## License

The fonts are released under the SIL Open Font License 1.1, so they're free for personal and commercial use. Every download includes `OFL.txt`, and the full text is in [LICENSE](LICENSE).

Built by [Hassan](https://x.com/nutlope) and [Youssef](https://x.com/YoussefUIUX).
