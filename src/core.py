import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # 使用非互動式backend
import matplotlib.pyplot as plt
from src.config import FigConfig, Shapefile


class GeoPlot:
    def __init__(self):
        self.fig_config = FigConfig()
        self.area_list = [area for area in enumerate(self.fig_config.AREA_RANGE)]

    def base(self) -> tuple[plt.Figure, plt.Axes]:
        """
        Create the base figure and axes for the plot.

        Returns
        -------
        tuple[plt.Figure, plt.Axes]
            The figure and axes of the plot.
        """
        fig, ax = plt.subplots(figsize=self.fig_config.SIZE, dpi=self.fig_config.DPI)
        ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(118.93, 122.7)
        ax.set_ylim(21.5, 25.5)

        area_range = self.fig_config.AREA_RANGE

        # taiwan
        self._inset(ax, bounds=(0, 0, 1, 1), label="taiwan", frame_on=False)

        x0, x1 = 0.02, 0.19
        w0, w1 = 0.21, 0.06
        y = 0.35
        # penghu
        h = self._cal_insert_ax_height(area_range["penghu"]["bounds"], w0)
        self._inset(ax, bounds=(x0, y, w0, h), label="penghu")

        # kinmen
        y = y + h + 0.01
        h = self._cal_insert_ax_height(area_range["kinmen"]["bounds"], w0)
        self._inset(ax, bounds=(x0, y, w0, h), label="kinmen")

        # kinmen-wuqiu
        _h = self._cal_insert_ax_height(area_range["kinmen-wuqiu"]["bounds"], w1)
        self._inset(ax, bounds=(x1, y + _h - 0.02, w1, _h), label="kinmen-wuqiu")

        # lienchiang
        y = y + h + 0.01
        h = self._cal_insert_ax_height(area_range["lienchiang"]["bounds"], w0)
        self._inset(ax, bounds=(x0, y, w0, h), label="lienchiang")

        # lienchiang-dongyin
        _h = self._cal_insert_ax_height(area_range["lienchiang-dongyin"]["bounds"], w1)
        self._inset(ax, bounds=(x1, y + _h - 0.03, w1, _h), label="lienchiang-dongyin")

        # lienchiang-juguang
        _h = self._cal_insert_ax_height(area_range["lienchiang-juguang"]["bounds"], w1)
        self._inset(ax, bounds=(x1, y + _h + 0.05, w1, _h), label="lienchiang-juguang")

        return fig, ax

    def _inset(
        self, ax: plt.Axes, bounds: tuple, label: str, frame_on: bool = True
    ) -> plt.Axes:
        ax_in = ax.inset_axes(bounds, label=label)
        ax_in.set_xticks([])
        ax_in.set_yticks([])
        ax_in.set_frame_on(frame_on)

        area_info = self.fig_config.AREA_RANGE[label]
        ax_in.set_xlim(area_info["bounds"]["min_x"], area_info["bounds"]["max_x"])
        ax_in.set_ylim(area_info["bounds"]["min_y"], area_info["bounds"]["max_y"])

        return ax_in

    def _cal_insert_ax_height(self, bounds: dict, width: float) -> tuple[float, float]:
        min_x, max_x, min_y, max_y = (
            bounds["min_x"],
            bounds["max_x"],
            bounds["min_y"],
            bounds["max_y"],
        )
        aspect = (max_y - min_y) / (max_x - min_x)
        height = width * aspect
        return height


class GeoData:
    def __init__(self):
        self.fig_config = FigConfig()
        self.shapefile = Shapefile()

    def get_county_gpd(self, bbox: tuple) -> gpd.GeoDataFrame:
        """
        Get the GeoDataFrame of the county shapefile.

        Parameters
        ----------
        bbox : tuple
            The bounding box of the area, in the form of (min_x, min_y, max_x, max_y).
        """
        gdf = gpd.read_file(self.shapefile.COUNTY, bbox=bbox)
        return gdf

    def get_town_gpd(self, bbox: tuple) -> gpd.GeoDataFrame:
        """
        Get the GeoDataFrame of the town shapefile.

        Parameters
        ----------
        bbox : tuple
            The bounding box of the area, in the form of (min_x, min_y, max_x, max_y).
        """
        gdf = gpd.read_file(self.shapefile.TOWN, bbox=bbox)
        return gdf

    def merge_gdf_and_df(
        self, gdf: gpd.GeoDataFrame, df: pd.DataFrame, **kwargs
    ) -> gpd.GeoDataFrame:
        """
        Merge the GeoDataFrame and DataFrame.

        Parameters
        ----------
        gdf : gpd.GeoDataFrame
            The GeoDataFrame to merge.
        df : pd.DataFrame
            The DataFrame to merge.
        kwargs
            Other keyword arguments to pass to the merge function.
        """
        gdf = gdf.merge(df, **kwargs)
        return gdf
