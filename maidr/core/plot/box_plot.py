from __future__ import annotations

from matplotlib.axes import Axes
from seaborn.categorical import BoxPlotContainer

from maidr.core.enum.maidr_key import MaidrKey
from maidr.core.enum.plot_type import PlotType
from maidr.core.maidr_plot import MaidrPlot
from maidr.core.mixin.extractor_mixin import (
    ContainerExtractorMixin,
    LevelExtractorMixin,
)
from maidr.core.mixin.merger_mixin import DictMergerMixin
from maidr.exception.extraction_error import ExtractionError


class _BoxPlotExtractorMixin:
    @staticmethod
    def extract_whiskers(whiskers: list) -> list[dict]:
        return _BoxPlotExtractorMixin.__extract_extremes(
            whiskers, MaidrKey.Q1, MaidrKey.Q3
        )

    @staticmethod
    def extract_caps(caps: list) -> list[dict]:
        return _BoxPlotExtractorMixin.__extract_extremes(
            caps, MaidrKey.MIN, MaidrKey.MAX
        )

    @staticmethod
    def __extract_extremes(
        extremes: list, start_key: MaidrKey, end_key: MaidrKey
    ) -> list[dict]:
        data = list()

        for start, end in zip(extremes[::2], extremes[1::2]):
            start_data = float(start.get_ydata()[0])
            end_data = float(start.get_ydata()[0])

            data.append(
                {
                    start_key.value: start_data,
                    end_key.value: end_data,
                }
            )

        return data

    @staticmethod
    def extract_medians(medians: list) -> list:
        return [float(median.get_ydata()[0]) for median in medians]

    @staticmethod
    def extract_outliers(fliers: list, caps: list) -> list[dict]:
        data = list()

        for outlier, cap in zip(fliers, caps):
            outliers = [float(outlier) for outlier in outlier.get_ydata()]
            _min, _max = cap.values()

            data.append(
                {
                    MaidrKey.LOWER_OUTLIER.value: sorted(
                        [outlier for outlier in outliers if outlier < _min]
                    ),
                    MaidrKey.UPPER_OUTLIER.value: sorted(
                        [outlier for outlier in outliers if outlier > _max]
                    ),
                }
            )

        return data


class BoxPlot(
    MaidrPlot,
    _BoxPlotExtractorMixin,
    ContainerExtractorMixin,
    LevelExtractorMixin,
    DictMergerMixin,
):
    def __init__(self, ax: Axes) -> None:
        super().__init__(ax, PlotType.BOX)

    def _extract_axes_data(self) -> dict:
        base_ax_schema = super()._extract_axes_data()
        box_ax_schema = {
            MaidrKey.X.value: {
                MaidrKey.LEVEL.value: self.extract_level(self.ax),
            },
        }
        return self.merge_dict(base_ax_schema, box_ax_schema)

    def _extract_plot_data(self) -> list:
        plot = self.extract_container(self.ax, BoxPlotContainer)
        data = self.__extract_box_container_data(plot)

        if data is None:
            raise ExtractionError(self.type, plot)

        return data

    def __extract_bxp_maidr(self, bxpstats: dict) -> list[dict]:
        bxp_maidr = list()
        whiskers = self.extract_whiskers(bxpstats["whiskers"])
        caps = self.extract_caps(bxpstats["caps"])
        medians = self.extract_medians(bxpstats["medians"])
        outliers = self.extract_outliers(bxpstats["fliers"], caps)

        for whisker, cap, median, outlier in zip(whiskers, caps, medians, outliers):
            bxp_maidr.append(
                {
                    MaidrKey.LOWER_OUTLIER.value: outlier["lower_outlier"],
                    MaidrKey.MIN.value: cap["min"],
                    MaidrKey.Q1.value: whisker["q1"],
                    MaidrKey.Q2.value: median,
                    MaidrKey.Q3.value: whisker["q3"],
                    MaidrKey.MAX.value: cap["max"],
                    MaidrKey.UPPER_OUTLIER.value: outlier["upper_outlier"],
                }
            )

        return bxp_maidr

    def __extract_box_container_data(self, plot: BoxPlotContainer | None) -> list[dict]:
        bxpstats = {
            "whiskers": plot.whiskers,
            "medians": plot.medians,
            "caps": plot.caps,
            "fliers": plot.fliers,
        }

        return self.__extract_bxp_maidr(bxpstats)
