import json
from typing import List, Union
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 使用非互動式backend，減少記憶體使用
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from dataclasses import dataclass
from contextlib import contextmanager
from src.core import GeoPlot, GeoData
from src.config import FigConfig, Font, Shapefile

# 設置matplotlib的記憶體管理參數
plt.rcParams["figure.max_open_warning"] = 0  # 關閉過多圖表的警告


@dataclass
class ChoroplethParams:
    """等值區域圖參數物件"""

    data: pd.DataFrame
    column: str
    level: str = "county"
    cmap: str = "GnBu"
    colorbar_format: str = "{x:,.0f}"
    colorbar_tick_visible: bool = True


@dataclass
class Hist2DParams:
    """2D直方圖參數物件"""

    x: List[float]
    y: List[float]
    bins: int = 100
    cmap: str = "GnBu"
    alpha: float = 0.5
    cmin: int = 1


@dataclass
class DotParams:
    """點圖參數物件"""

    x: List[float]
    y: List[float]
    size: Union[int, float] = 1
    color: str = "red"
    alpha: float = 0.5


@dataclass
class BubbleParams:
    """氣泡圖參數物件"""

    x: List[float]
    y: List[float]
    size: List[Union[int, float]] = None
    color: List[str] = None
    alpha: float = 0.5
    cmin: int = 1

    def __post_init__(self):
        if self.size is None:
            self.size = [1] * len(self.x)
        if self.color is None:
            self.color = ["red"] * len(self.x)


class Graph:
    def __init__(self):
        self.fig_config = FigConfig()
        self.shapefile = Shapefile()
        self.geo_plot = GeoPlot()
        self.geo_data = GeoData()

        font = Font()
        font.register(Font().Urbanist)
        font.register(Font().NotoSerifTC)

    @contextmanager
    def _managed_plot(self):
        """Context manager for matplotlib figure memory management"""
        try:
            yield
        finally:
            # 確保所有打開的圖表都被關閉
            plt.close("all")

    def _ensure_figure_closed(self, fig):
        """確保單個figure被正確關閉"""
        if fig is not None:
            plt.close(fig)

    def cleanup_memory(self):
        """清理matplotlib的記憶體和快取"""
        plt.close("all")
        # 清理matplotlib的快取
        if hasattr(plt, "rcParams"):
            plt.rcdefaults()
        # 強制垃圾回收
        import gc

        gc.collect()

    def plot_boundary(self) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot the boundary of the given area.

        Returns
        -------
        tuple[plt.Figure, plt.Axes]
            The figure and axes of the plot.
        """
        area_list = self.geo_plot.area_list
        area_range = self.fig_config.AREA_RANGE

        fig, ax = self.geo_plot.base()
        for i, a in area_list:
            bbox = (
                area_range[a]["bounds"]["min_x"],
                area_range[a]["bounds"]["min_y"],
                area_range[a]["bounds"]["max_x"],
                area_range[a]["bounds"]["max_y"],
            )
            gdf = self.geo_data.get_county_gpd(bbox)
            gdf.boundary.plot(ax=ax.child_axes[i], color="black", linewidth=0.8)

        return fig, ax

    def plot_boundary_with_subsidy(self) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot the boundary of the given area with mark subsidy area.

        Returns
        -------
        tuple[plt.Figure, plt.Axes]
            The figure and axes of the plot.
        """
        area_list = self.geo_plot.area_list
        area_range = self.fig_config.AREA_RANGE
        with open("res/json/town_type_by_town.json", "r", encoding="utf-8") as f:
            town_type = json.load(f)
        colormap = {
            "山地原民區": "#477160",
            "平地原民區": "#A8D8B9",
            "偏遠地區": "#FFC145",
            "離島地區": "#90C2E7",
        }

        fig, ax = self.geo_plot.base()
        for i, a in area_list:
            bbox = (
                area_range[a]["bounds"]["min_x"],
                area_range[a]["bounds"]["min_y"],
                area_range[a]["bounds"]["max_x"],
                area_range[a]["bounds"]["max_y"],
            )
            county_gdf = self.geo_data.get_county_gpd(bbox)
            town_gdf = self.geo_data.get_town_gpd(bbox)
            town_gdf["town_type"] = town_gdf.apply(
                lambda row: town_type.get(row["COUNTYNAME"] + row["TOWNNAME"]),
                axis=1,
            )
            town_gdf["color"] = town_gdf["town_type"].map(
                lambda x: colormap.get(x, "#ffffff00")
            )
            county_gdf.boundary.plot(ax=ax.child_axes[i], color="black", linewidth=0.8)
            town_gdf.boundary.plot(ax=ax.child_axes[i], color="gray", linewidth=0.5)
            town_gdf.plot(ax=ax.child_axes[i], color=town_gdf["color"])

        ax.legend(
            handles=[
                plt.Rectangle((0, 0), 1, 1, color="#477160", label="山地原民區"),
                plt.Rectangle((0, 0), 1, 1, color="#7FB685", label="平地原民區"),
                plt.Rectangle((0, 0), 1, 1, color="#FFC145", label="偏遠地區"),
                plt.Rectangle((0, 0), 1, 1, color="#90C2E7", label="離島地區"),
            ],
            labels=[
                "山地原民區",
                "平地原民區",
                "偏遠地區",
                "離島地區",
            ],
            prop={"family": "Noto Serif TC", "size": 14},
            loc="lower right",
        )
        return fig, ax

    def plot_choropleth(self, params: ChoroplethParams) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot a choropleth map of the given data.

        Parameters
        ----------
        params : ChoroplethParams
            包含繪製等值區域圖所需參數的物件

        Returns
        -------
        tuple[plt.Figure, plt.Axes]
            The figure and axes of the plot.
        """
        area_list = self.geo_plot.area_list
        area_range = self.fig_config.AREA_RANGE

        fig, ax = self.geo_plot.base()
        for i, a in area_list:
            bbox = (
                area_range[a]["bounds"]["min_x"],
                area_range[a]["bounds"]["min_y"],
                area_range[a]["bounds"]["max_x"],
                area_range[a]["bounds"]["max_y"],
            )
            if params.level == "town":
                gdf = self.geo_data.get_town_gpd(bbox)
            else:
                gdf = self.geo_data.get_county_gpd(bbox)

            gdf = self.geo_data.merge_gdf_and_df(
                gdf,
                params.data,
                left_on=["COUNTYNAME", "TOWNNAME"]
                if params.level == "town"
                else ["COUNTYNAME"],
                right_on=["county", "town"] if params.level == "town" else ["county"],
            )
            if gdf.empty:
                county_edge = self.geo_data.get_county_gpd(bbox)
                county_edge.boundary.plot(
                    ax=ax.child_axes[i], color="black", linewidth=0.8
                )
                continue
            gdf.plot(ax=ax.child_axes[i], column=params.column, cmap=params.cmap)

            county_edge = self.geo_data.get_county_gpd(bbox)
            county_edge.boundary.plot(ax=ax.child_axes[i], color="black", linewidth=0.8)

        self._colorbar(
            ax,
            params.data[params.column].min(),
            params.data[params.column].max(),
            params.cmap,
            params.colorbar_format,
            params.colorbar_tick_visible,
        )

        return fig, ax

    def _colorbar(
        self,
        ax,
        vmin: float,
        vmax: float,
        cmap: str,
        colorbar_format: str,
        colorbar_tick_visible: bool = True,
    ) -> plt.colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
        sm._A = []

        cbar = plt.colorbar(
            sm,
            ax=ax,
            location="right",
            orientation="vertical",
            fraction=0.03,
            pad=-0.03,
            format=colorbar_format,
        )

        if colorbar_tick_visible:
            cbar.locator = MaxNLocator(nbins=6)
            cbar.ax.tick_params(
                axis="y",
                labelsize=18,
                labelfontfamily="Urbanist",
                labelrotation=0,
            )
        else:
            cbar.ax.yaxis.set_major_locator(plt.NullLocator())

        return cbar

    def plot_hist2d(
        self,
        params: Hist2DParams,
    ):
        """
        Plot a 2D histogram of the given data.

        Parameters
        ----------
        params : Hist2DParams
            包含繪製2D直方圖所需參數的物件
        """
        area_list = self.geo_plot.area_list
        area_range = self.fig_config.AREA_RANGE

        fig, ax = self.plot_boundary()
        for i, a in area_list:
            bounds = area_range[a]["bounds"]
            ax.child_axes[i].hist2d(
                params.x,
                params.y,
                bins=params.bins,
                cmap=params.cmap,
                alpha=params.alpha,
                range=[
                    (bounds["min_x"], bounds["max_x"]),
                    (bounds["min_y"], bounds["max_y"]),
                ],
                cmin=params.cmin,
            )

        return fig, ax

    def plot_dot(self, params: DotParams) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot a dot chart of the given data.

        Parameters
        ----------
        params : DotParams
            包含繪製點圖所需參數的物件
        """
        area_list = self.geo_plot.area_list

        fig, ax = self.plot_boundary()
        for i, a in area_list:
            ax.child_axes[i].scatter(
                params.x, params.y, s=params.size, c=params.color, alpha=params.alpha
            )

        return fig, ax

    def plot_bubble(
        self,
        params: BubbleParams,
    ) -> tuple[plt.Figure, plt.Axes]:
        """
        Plot a bubble chart of the given data.

        Parameters
        ----------
        params : BubbleParams
            包含繪製氣泡圖所需參數的物件
        """
        area_list = self.geo_plot.area_list

        fig, ax = self.plot_boundary()
        for i, a in area_list:
            ax.child_axes[i].scatter(
                params.x,
                params.y,
                s=params.size,
                c=params.color,
                alpha=params.alpha,
                edgecolor="black",
                linewidth=0.5,
            )

        return fig, ax

    @contextmanager
    def manage_memory(self):
        """
        Context manager for memory management.
        """
        try:
            yield
        finally:
            plt.close("all")
            import gc

            gc.collect()
