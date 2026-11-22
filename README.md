# TC001 Max 1/4"-20 Mount

Mechanical design for a 1/4"-20 tripod adapter for the TOPDON TC001 Max
thermal camera. The adapter reroutes the camera's USB-C connector through a
custom flex PCB so the camera can sit on a standard tripod mount.

The software side (webcam driver/installer) lives in
[TC001-Max-Webcam](https://github.com/MMImodular/TC001-Max-Webcam). The
reference dimensions this design is built from are documented there in
[`docs/TC001MAX_MECHANICAL.md`](https://github.com/MMImodular/TC001-Max-Webcam/blob/main/docs/TC001MAX_MECHANICAL.md).

## Status

Early work in progress. Geometry is from published specs and estimates; nothing
has been measured on a real unit yet.

## Layout

Planned:

- `cad/` – Fusion 360 archives (`.f3d`) and neutral exports (`.step`)
- `print/` – printable meshes (`.stl` / `.3mf`)
- `docs/` – drawings, photos, notes
