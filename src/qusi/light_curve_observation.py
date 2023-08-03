from dataclasses import dataclass
from typing import Self

from qusi.light_curve import LightCurve


@dataclass
class LightCurveObservation:
    """
    An observation containing a light curve and label. Note, this is an observation in machine learning terms, not to be
    confused with an astrophysical observation.

    :ivar light_curve: The light curve.
    :ivar label: The integer classification label.
    """
    light_curve: LightCurve
    label: int

    @classmethod
    def new(cls, light_curve: LightCurve, label: int) -> Self:
        """
        Creates a new LightCurveObservation.

        :param light_curve: The light curve.
        :param label: The integer classification label.
        :return: The observation.
        """
        return cls(light_curve=light_curve, label=label)
