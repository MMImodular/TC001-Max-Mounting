# TC001 Max Mounting

Mechanical design for a 1/4"-20 tripod adapter for the TOPDON TC001 Max
thermal camera. The adapter reroutes the camera's USB-C connector through a
custom flex PCB so the camera can sit on a standard tripod mount.

The software side (webcam driver/installer) lives in
[TC001-Max-Webcam](https://github.com/MMImodular/TC001-Max-Webcam).

## Status

Early work in progress. So far there is a parametric model of the camera
itself, built from published specs and photo-scaled estimates. Nothing has
been measured on a real unit yet; see the list of what to measure first in
[`docs/TC001MAX_MECHANICAL.md`](docs/TC001MAX_MECHANICAL.md).

## Layout

| Path | Contents |
|---|---|
| `cad/TOPDON_TC001_Max.f3d` | Fusion 360 archive of the camera model. Every dimension is a named user parameter. |
| `cad/TOPDON_TC001_Max.step` | The same model as STEP (mm), for other CAD tools. Includes the `PlugEnvelope` keep-out body. |
| `docs/TC001MAX_MECHANICAL.md` | Reference dimensions, their sources and confidence, and the model's coordinate frame and parameters. |
| `fusion/build_tc001max.py` | Fusion 360 script that rebuilds the camera model from scratch. |

Planned: `print/` for printable meshes (`.stl` / `.3mf`) of the adapter.
