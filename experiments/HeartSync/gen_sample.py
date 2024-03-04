"""
This example demonstrates how to simulate a 3D beating heart.
"""

# Copyright (c) 2023 Idiap Research Institute, http://www.idiap.ch/
# Written by François Marelli <francois.marelli@idiap.ch>
#
# This file is part of CBI Toolbox.
#
# CBI Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the 3-Clause BSD License.
#
# CBI Toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# 3-Clause BSD License for more details.
#
# You should have received a copy of the 3-Clause BSD License along
# with CBI Toolbox. If not, see https://opensource.org/licenses/BSD-3-Clause.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse, pathlib
import numpy as np

from cbi_toolbox.simu import primitives, textures, dynamic, optics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=str, default=None)
    parser.add_argument("--time", type=int, default=50)
    parser.add_argument("--depth", type=int, default=64)
    args = parser.parse_args()

    if args.outdir is None:
        outdir = pathlib.Path(__file__).parent / "out"
    else:
        outdir = args.outdir

    outpath = pathlib.Path(outdir) / "data"
    outpath.mkdir(parents=True, exist_ok=True)

    psf = optics.gaussian_psf(
        npix_axial=63, npix_lateral=args.depth, wavelength=600e-9
    ).squeeze()

    np.save(outpath / "psf.npy", psf)

    spim = optics.openspim_illumination(
        npix_fov=args.depth, npix_z=63, slit_opening=4e-3, wavelength=600e-9
    ).squeeze()

    np.save(outpath / "spim.npy", spim)

    del spim, psf

    # Uniform sampling over one period
    phases = np.linspace(0, 1, args.time, endpoint=False)

    # Basic contraction of the coordinates
    coords = dynamic.sigsin_beat_3(phases, args.depth)
    print("Done simulating contraction")

    # Heart walls as an ellipsoid
    ellipse = primitives.forward_ellipse_3(
        coords, center=(0.5, 0.5, 0.5), radius=(0.2, 0.3, 0.4)
    )
    print("Done simulating the heart wall")

    # Adding texture using simplex noise
    simplex = textures.forward_simplex(coords, scale=20, time=True, seed=0)
    print("Done simulating the heart texture")

    del coords
    simplex += 2
    simplex /= simplex.max()
    heart = ellipse * simplex

    np.save(outpath / "sample.npy", heart)