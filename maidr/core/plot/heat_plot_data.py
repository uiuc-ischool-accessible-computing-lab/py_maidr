from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh

from maidr.core.enum.maidr_key import MaidrKey
from maidr.core.enum.plot_type import PlotType
from maidr.core.maidr_plot_data import MaidrPlotData
from maidr.exception.extraction_error import ExtractionError


class HeatPlotData(MaidrPlotData):
    """
    A class encapsulating all the MAIDR representation of the axes in a figure
    along with the plot.

    This class extends `MaidrPlotData` to specifically handle data extraction and
    representation for heatmaps. It encapsulates the details required to represent a
    heatmap as a part of an interactive MAIDR visualization, including plot type,
    titles, axes labels, and the plot data itself.

    Parameters
    ----------
    axes : Axes
        The matplotlib axes object on which the heatmap is drawn.

    Warnings
    --------
    End users will typically not have to use this class directly.

    See Also
    --------
    MaidrPlotData : The base class for MAIDR plot data objects.
    """

    def __init__(self, axes: Axes) -> None:
        """
        Initializes the HeatPlotData object with matplotlib axes with matplotlib axes
        containing the heatmap.

        Parameters
        ----------
        axes : Axes
            The axes object associated with the heatmap.
        """
        super().__init__(axes, PlotType.HEAT)

    def _extract_maidr_data(self) -> dict:
        """
        Extracts and structures heatmap data for MAIDR visualization.

        Returns
        -------
        dict
            A dictionary containing the extracted maidr heatmap data.
        """
        plt_type = self.type.value
        ax = self.axes

        maidr = {
            MaidrKey.TYPE.value: plt_type,
            MaidrKey.TITLE.value: ax.get_title(),
            MaidrKey.LABEL.value: {
                MaidrKey.FILL.value: None,
            },
            MaidrKey.AXES.value: {
                MaidrKey.X.value: {
                    MaidrKey.LABEL.value: ax.get_xlabel(),
                    MaidrKey.LEVEL.value: self.__extract_level(),
                },
                MaidrKey.Y.value: {
                    MaidrKey.LABEL.value: ax.get_ylabel(),
                },
            },
            MaidrKey.DATA.value: self.__extract_data(),
        }

        return maidr

    def __extract_level(self) -> list:
        """
        Extracts x-axis level values based on tick labels.

        Returns
        -------
        list
            A list of strings representing the x-axis levels.
        """
        return [label.get_text() for label in self.axes.get_xticklabels()]

    def __extract_data(self) -> list[list]:
        """
        Extracts numerical data from the heatmap.

        Returns
        -------
        list[list]
            A 2D list of numerical data extracted from the heatmap.

        Raises
        ------
        ExtractionError
            If the plot object is incompatible for data extraction.
        """
        ax = self.axes
        plot = None
        data = None

        if isinstance(ax, Axes):
            plot = HeatPlotData.__extract_quad_mesh(ax)
        if isinstance(plot, QuadMesh):
            data = HeatPlotData.__extract_quad_mesh_data(plot)

        if data is None:
            raise ExtractionError(self.type, plot)

        return data

    @staticmethod
    def __extract_quad_mesh_data(plot: QuadMesh) -> list[list] | None:
        """
        Extracts numerical data from the specified QuadMesh object if possible.

        Parameters
        ----------
        plot : QuadMesh
            The QuadMesh from which to extract the data.

        Returns
        -------
        list[list] | None
            A 2D list containing the numerical data extracted from the QuadMesh, or None
            if the plot does not contain valid data values or is not a QuadMesh.
        """
        if plot is None or plot.get_array() is None:
            return None

        data = list()
        array = plot.get_array()
        for row in array:  # type: ignore
            row_data = list()
            for item in row:
                if isinstance(item, np.integer):
                    row_data.append(int())
                elif isinstance(item, np.floating):
                    row_data.append(float(item))
                else:
                    row_data.append(item)
            data.append(row_data)

        return data

    @staticmethod
    def __extract_quad_mesh(plot: Axes) -> QuadMesh | None:
        """
        Extracts the QuadMesh from the given Axes object if possible.

        Parameters
        ----------
        plot : Axes
            The Axes object to search for a QuadMesh.

        Returns
        -------
        QuadMesh | None
            The first QuadMesh found within the given Axes object, or None if no
            QuadMesh is present.
        """
        # Ideally, there should only be one QuadMesh for a heatmap
        for collection in plot.collections:
            if isinstance(collection, QuadMesh):
                return collection
