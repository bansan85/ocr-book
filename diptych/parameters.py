import types
from typing import Tuple, Union

from .angle import Angle


class ErodeParameters:
    class Impl(types.SimpleNamespace):
        size: Tuple[int, int]
        iterations: int

    def __init__(self, size: Tuple[int, int], iterations: int) -> None:
        self.__param = ErodeParameters.Impl(size=size, iterations=iterations)

    @property
    def size(self) -> Tuple[int, int]:
        return self.__param.size

    @size.setter
    def size(self, val: Tuple[int, int]) -> None:
        self.__param.size = val

    @property
    def iterations(self) -> int:
        return self.__param.iterations

    @iterations.setter
    def iterations(self, val: int) -> None:
        self.__param.iterations = val

    def init_default_values(
        self,
        key: str,
        value: Union[int, float, Tuple[int, int], Angle],
    ) -> None:
        if key == "Size" and isinstance(value, tuple):
            self.size = value
        elif key == "Iterations" and isinstance(value, int):
            self.iterations = value
        else:
            raise Exception("Invalid property.", key)


class CannyParameters:
    class Impl(types.SimpleNamespace):
        minimum: int
        maximum: int
        aperture_size: int

    def __init__(self, minimum: int, maximum: int, aperture_size: int) -> None:
        self.__param = CannyParameters.Impl(
            minimum=minimum, maximum=maximum, aperture_size=aperture_size
        )

    @property
    def minimum(self) -> int:
        return self.__param.minimum

    @minimum.setter
    def minimum(self, val: int) -> None:
        self.__param.minimum = val

    @property
    def maximum(self) -> int:
        return self.__param.maximum

    @maximum.setter
    def maximum(self, val: int) -> None:
        self.__param.maximum = val

    @property
    def aperture_size(self) -> int:
        return self.__param.aperture_size

    @aperture_size.setter
    def aperture_size(self, val: int) -> None:
        self.__param.aperture_size = val

    def init_default_values(
        self,
        key: str,
        value: Union[int, float, Tuple[int, int], Angle],
    ) -> None:
        if key == "Min" and isinstance(value, int):
            self.minimum = value
        elif key == "Max" and isinstance(value, int):
            self.maximum = value
        elif key == "ApertureSize" and isinstance(value, int):
            self.aperture_size = value
        else:
            raise Exception("Invalid property.", key)


class HoughLinesParameters:
    class Impl(types.SimpleNamespace):
        delta_rho: int
        delta_tetha: Angle
        threshold: int
        min_line_length: int
        max_line_gap: int
        scale: float

    def __init__(  # pylint: disable=too-many-arguments
        self,
        delta_rho: int,
        delta_tetha: Angle,
        threshold: int,
        min_line_length: int,
        max_line_gap: int,
        scale: float,
    ) -> None:
        self.__param = HoughLinesParameters.Impl(
            delta_rho=delta_rho,
            delta_tetha=delta_tetha,
            threshold=threshold,
            min_line_length=min_line_length,
            max_line_gap=max_line_gap,
            scale=scale,
        )

    @property
    def delta_rho(self) -> int:
        return self.__param.delta_rho

    @delta_rho.setter
    def delta_rho(self, val: int) -> None:
        self.__param.delta_rho = val

    @property
    def delta_tetha(self) -> Angle:
        return self.__param.delta_tetha

    @delta_tetha.setter
    def delta_tetha(self, val: Angle) -> None:
        self.__param.delta_tetha = val

    @property
    def threshold(self) -> int:
        return int(self.__param.threshold * self.scale)

    @threshold.setter
    def threshold(self, val: int) -> None:
        self.__param.threshold = val

    @property
    def min_line_length(self) -> int:
        return int(self.__param.min_line_length * self.scale)

    @min_line_length.setter
    def min_line_length(self, val: int) -> None:
        self.__param.min_line_length = val

    @property
    def max_line_gap(self) -> int:
        return int(self.__param.max_line_gap * self.scale)

    @max_line_gap.setter
    def max_line_gap(self, val: int) -> None:
        self.__param.max_line_gap = val

    @property
    def scale(self) -> float:
        return self.__param.scale

    @scale.setter
    def scale(self, val: float) -> None:
        self.__param.scale = val

    def init_default_values(
        self,
        key: str,
        value: Union[int, float, Tuple[int, int], Angle],
    ) -> None:
        if key == "DeltaRho" and isinstance(value, int):
            self.delta_rho = value
        elif key == "DeltaTetha" and isinstance(value, Angle):
            self.delta_tetha = value
        elif key == "Threshold" and isinstance(value, int):
            self.threshold = value
        elif key == "MinLineLength" and isinstance(value, int):
            self.min_line_length = value
        elif key == "MaxLineGap" and isinstance(value, int):
            self.max_line_gap = value
        elif key == "Scale" and isinstance(value, float):
            self.scale = value
        else:
            raise Exception("Invalid property.", key)
