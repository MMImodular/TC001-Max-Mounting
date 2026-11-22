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

## License

Copyright 2026 Matt Gaines.

This source describes Open Hardware and is licensed under the
[CERN Open Hardware Licence Version 2 - Permissive](LICENSE) (CERN-OHL-P v2).
That covers everything in this repository: the CAD models, the Fusion script,
the docs, and any KiCad/PCB files added later.

You may redistribute and modify this source and make products using it under
the terms of the CERN-OHL-P v2. This source is distributed WITHOUT ANY EXPRESS
OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND
FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-P v2 for applicable
conditions.

Source location: <https://github.com/MMImodular/TC001-Max-Mounting>

TOPDON and TC001 are trademarks of their owner and are used here only to
identify the camera this adapter fits. This project is not affiliated with or
endorsed by TOPDON. USB-C is used only to describe the connector.
