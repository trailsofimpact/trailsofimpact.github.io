# Trails of Impact — sources du site

Cette branche contient les sources ; la branche `main` contient le site publié (GitHub Pages).

- `site/` : pages, styles, images et `build.py`. Construire : `cd site && python3 build.py`, puis copier `site/dist/` dans la branche `main`.
- `social/` : générateur des visuels des réseaux sociaux (`make_slides.py`, rendu avec Playwright).
