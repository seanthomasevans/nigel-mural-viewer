# Dear Rockaway Beach, Thank You Rockaway Beach — Mural Preview

Interactive 3D preview of the proposed mural by **Nigel Scott** on the lifeguard
storage container at **97th Street and Shore Front Parkway, Rockaway Beach, NY**.

Two variants of the long-side mural are presented; both end caps carry the
square companion piece.

## Live preview

Served from the `gh-pages` branch via GitHub Pages.

## Project layout

```
build_container.py        Blender script: builds 20ft ISO container with
                          UV-mapped murals on front + both ends
textures/                 Web-resolution mural exports (2400px long edge)
web/                      Static site served by GitHub Pages
  index.html              model-viewer single-page viewer
  models/                 container-v1.glb, container-v2.glb (glTF binary)
```

## Rebuilding the models

```bash
# from project root
blender -b -P build_container.py -- textures/mural-1-landscape.jpg web/models/container-v1.glb
blender -b -P build_container.py -- textures/mural-2-landscape.jpg web/models/container-v2.glb
```

The end-cap texture (`mural-3-square.jpg`) is hard-coded inside the script.

## Stack

- Blender 4.x glTF exporter
- Google `<model-viewer>` 4.0.0 web component
- Plain HTML / CSS / vanilla JS, no build step
