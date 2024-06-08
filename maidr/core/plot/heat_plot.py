from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.collections import QuadMesh

from maidr.core.enum import MaidrKey, PlotType
from maidr.core.plot import MaidrPlot
from maidr.exception import ExtractionError
from maidr.utils.mixin import (
    DictMergerMixin,
    LevelExtractorMixin,
    ScalarMappableExtractorMixin,
)


class HeatPlot(
    MaidrPlot, LevelExtractorMixin, ScalarMappableExtractorMixin, DictMergerMixin
):
    def __init__(self, ax: Axes, **kwargs) -> None:
        self._fill_label = kwargs.pop("fill_label")
        super().__init__(ax, PlotType.HEAT)

    def render(self) -> dict:
        base_maidr = super().render()
        heat_maidr = {
            MaidrKey.LABELS: {
                MaidrKey.FILL: self._fill_label,
            },
        }
        return self.merge_dict(base_maidr, heat_maidr)

    def _extract_axes_data(self) -> dict:
        base_ax_schema = super()._extract_axes_data()
        heat_ax_schema = {
            MaidrKey.X: {
                MaidrKey.LEVEL: self.extract_level(self.ax, MaidrKey.X),
            },
            MaidrKey.Y: {
                MaidrKey.LEVEL: self.extract_level(self.ax, MaidrKey.Y),
            },
        }
        return self.merge_dict(base_ax_schema, heat_ax_schema)

    def _extract_plot_data(self) -> list[list]:
        plot = self.extract_scalar_mappable(self.ax)
        data = HeatPlot._extract_scalar_mappable_data(plot)

        if data is None:
            raise ExtractionError(self.type, plot)

        return data

    @staticmethod
    def _extract_scalar_mappable_data(sm: ScalarMappable | None) -> list[list] | None:
        if sm is None or sm.get_array() is None:
            return None

        array = sm.get_array().data
        if isinstance(sm, QuadMesh):
            # Data gets flattened in ScalarMappable, when the plot is from QuadMesh.
            # So, reshaping the data to reflect the original quadrilaterals
            m, n, _ = sm.get_coordinates().shape
            array = array.reshape(m - 1, n - 1)  # Coordinates shape is (M + 1, N + 1)

        return [list(map(float, row)) for row in array]
