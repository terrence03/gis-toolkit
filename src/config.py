from pathlib import Path
from matplotlib import font_manager

WORK_DIR = Path("/app")


class Font:
    FONT_DIR = WORK_DIR / "res" / "fonts"

    CharisSIL = FONT_DIR / "CharisSIL-Regular.ttf"
    CharisSIL_Bold = FONT_DIR / "CharisSIL-Bold.ttf"
    NotoSerifTC = FONT_DIR / "NotoSerifTC-Regular.ttf"
    NotoSerifTC_Bold = FONT_DIR / "NotoSerifTC-Bold.ttf"
    TimesNewRoman = FONT_DIR / "TimesNewRoman-Regular.ttf"
    TimesNewRoman_Bold = FONT_DIR / "TimesNewRoman-Bold.ttf"
    Urbanist = FONT_DIR / "Urbanist-Regular.ttf"

    def register(self, font):
        font_manager.fontManager.addfont(font)

    def register_all(self):
        font_manager.fontManager.addfont(Font.CharisSIL)
        font_manager.fontManager.addfont(Font.CharisSIL_Bold)
        font_manager.fontManager.addfont(Font.NotoSerifTC)
        font_manager.fontManager.addfont(Font.NotoSerifTC_Bold)
        font_manager.fontManager.addfont(Font.TimesNewRoman)
        font_manager.fontManager.addfont(Font.TimesNewRoman_Bold)
        font_manager.fontManager.addfont(Font.Urbanist)

    def show_all(self):
        font_names = sorted([font.name for font in font_manager.fontManager.ttflist])
        print("所有可用字體：")
        for name in font_names:
            print(name)


class Shapefile:
    SHAPEFILE_DIR = WORK_DIR / "res" / "shp"

    COUNTY = SHAPEFILE_DIR / "COUNTY_MOI_1090820.shp"
    TOWN = SHAPEFILE_DIR / "TOWN_MOI_1120825.shp"


class Json:
    JSON_DIR = WORK_DIR / "res" / "json"

    COUNTY_TOWN = JSON_DIR / "county_town.json"
    TOWN_TYPE_BY_TOWN = JSON_DIR / "town_type_by_town.json"
    TOWN_TYPE_BY_TYPE = JSON_DIR / "town_type_by_type.json"
    NO_GAS_STATION_TOWN = JSON_DIR / "no_gas_station_town.json"


class FigConfig:
    WIDTH = 14.65
    HEIGHT = 16
    DPI = 200
    SIZE = (WIDTH, HEIGHT)

    AREA_RANGE = {
        "taiwan": {
            "name": "台灣本島",
            "level": 0,
            "center": (120.96, 23.7),
            "bounds": {
                "min_x": 118.9,
                "max_x": 122.6,
                "min_y": 21.75,
                "max_y": 25.35,
            },
        },
        "penghu": {
            "name": "澎湖縣",
            "level": 1,
            "center": (119.57, 23.57),
            "bounds": {
                "min_x": 119.3,
                "max_x": 119.74,
                "min_y": 23.16,
                "max_y": 23.86,
            },
        },
        "kinmen": {
            "name": "金門縣",
            "level": 1,
            "center": (118.3, 24.4),
            "bounds": {
                "min_x": 118.1,
                "max_x": 118.6,
                "min_y": 24.34,
                "max_y": 24.56,
            },
        },
        "kinmen-wuqiu": {
            "name": "金門縣烏坵鄉",
            "level": 2,
            "center": (119.5, 24.8),
            "bounds": {
                "min_x": 119.42,
                "max_x": 119.5,
                "min_y": 24.96,
                "max_y": 25.02,
            },
        },
        "lienchiang": {
            "name": "連江縣",
            "level": 1,
            "center": (119.90, 26.20),
            "bounds": {
                "min_x": 119.86,
                "max_x": 120.1,
                "min_y": 26.12,
                "max_y": 26.30,
            },
        },
        "lienchiang-dongyin": {
            "name": "連江縣東引鄉",
            "level": 2,
            "center": (120.5, 26.3),
            "bounds": {
                "min_x": 120.45,
                "max_x": 120.52,
                "min_y": 26.34,
                "max_y": 26.4,
            },
        },
        "lienchiang-juguang": {
            "name": "連江縣莒光鄉",
            "level": 2,
            "center": (119.9, 25.9),
            "bounds": {
                "min_x": 119.91,
                "max_x": 120,
                "min_y": 25.93,
                "max_y": 26,
            },
        },
    }
