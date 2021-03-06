

from dataclasses import dataclass

import numpy as np
import astropy.units as u

__all__ = ['Telescope', 'kuiper_mont4k']

ARCSEC_PER_RADIAN = (1 * u.rad).to(u.arcsec).value


@dataclass
class Telescope:
    diameter: u.Quantity        # Primary mirror diameter
    f_ratio: float              # Focal ratio of optical system
    pix_size: u.Quantity        # Detector pixel size
    obscuration: float = 0.0    # Fractional obscuration due to secondary mirror/baffles
    focus_slope: float = 1.0    # change in pupil diameter in pixels per focus readout unit

    def __post_init__(self):
        self.focal_length = self.diameter * self.f_ratio  # Focal length of optical system
        self.radius = self.diameter / 2.0  # Radius of primary mirror
        self.nmperrad = self.radius.to(u.nm).value  # nm of wavefront tilt per raadian
        self.nmperasec = self.nmperrad / ARCSEC_PER_RADIAN  # nm of wavefront tilt per arcsecond
        self.plate_scale = ARCSEC_PER_RADIAN * u.arcsec / self.focal_length.to(u.mm)  # Plate scale of focal plane

    @property
    def convergence_angle(self):
        """
        Angle of convergence of the telescope optics
        """
        return np.arctan2(self.radius, self.focal_length)

    @property
    def offset_slope(self):
        """
        Change in focal point per focus readout unit
        """
        foc_um_slope = self.focus_slope * self.pix_size
        offset_slope = 0.5 * foc_um_slope / np.tan(self.convergence_angle)
        return offset_slope

    def simple_focus(self, pupsize: float, direction: str = "intra", binning: int = 3):
        """
        Given a pupil diameter in pixels and a direction from best-focus, calculate focus correction
        """
        if direction not in ['intra', 'extra']:
            raise Exception("Specified direction must be either 'intra' or 'extra' focal.")
        corr = pupsize / (self.focus_slope / binning)
        if 'extra' in direction:
            corr *= -1
        return corr


kuiper_mont4k = Telescope(
    diameter=1.54 * u.m,
    f_ratio=13.5,
    pix_size=14 * u.um,
    obscuration=0.266,
    focus_slope=0.06919 * 3  # empirically determined 2019-02-21 at 3x3 binning. units are pixels per focus count.
)
