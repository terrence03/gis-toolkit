import io
import gc
from contextlib import asynccontextmanager
from typing import List, Optional, Union
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from src.graph import Graph, ChoroplethParams, Hist2DParams, DotParams, BubbleParams


# 請求計數器，用於定期清理記憶體
request_counter = 0
CLEANUP_INTERVAL = 50  # 每50個請求清理一次記憶體


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化
    global request_counter
    request_counter = 0
    graph_instance.cleanup_memory()
    print("記憶體管理已初始化")
    yield
    # 關閉時清理
    graph_instance.cleanup_memory()
    print("應用關閉，記憶體已清理")


app = FastAPI(
    title="地理圖表API",
    description="使用FastAPI提供地理資料視覺化服務",
    lifespan=lifespan,
)

# 建立基礎Graph實例
graph_instance = Graph()

# Jinja2模板設定
templates = Jinja2Templates(directory="templates")


# Pydantic模型用於資料驗證
class ChoroplethData(BaseModel):
    data: List[dict] = Field(
        [
            {"county": "臺北市", "value": 10},
            {"county": "新北市", "value": 20},
        ],
        example=[
            {"county": "臺北市", "value": 10},
            {"county": "新北市", "value": 20},
        ],
    )
    column: str = Field("value", example="value")
    level: Optional[str] = Field("county", example="county")
    cmap: Optional[str] = Field("GnBu", example="GnBu")
    colorbar_format: Optional[str] = Field("{x:,.0f}", example="{x:,.0f}")
    colorbar_tick_visible: Optional[bool] = Field(True, example=True)


class DotPlotData(BaseModel):
    x: List[float] = Field([120.96], example=[120.96])
    y: List[float] = Field([23.70], example=[23.70])
    size: Optional[Union[int, float]] = Field(10, example=10)
    color: Optional[str] = Field("red", example="red")
    alpha: Optional[float] = Field(0.5, example=0.5)


class Hist2DData(BaseModel):
    x: List[float] = Field(
        [120.96, 120.96, 120.96, 119.57, 118.30, 119.90],
        example=[120.96, 120.96, 120.96, 119.57, 118.30, 119.90],
    )
    y: List[float] = Field(
        [23.70, 23.70, 23.70, 23.57, 24.40, 26.20],
        example=[23.70, 23.70, 23.70, 23.57, 24.40, 26.20],
    )
    bins: Optional[int] = Field(100, example=100)
    cmap: Optional[str] = Field("GnBu", example="GnBu")
    alpha: Optional[float] = Field(0.5, example=0.5)
    cmin: Optional[int] = Field(1, example=1)


class BubbleData(BaseModel):
    x: List[float] = Field(
        [120.96, 120.96, 120.96, 119.57, 118.30, 119.90],
        example=[120.96, 120.96, 120.96, 119.57, 118.30, 119.90],
    )
    y: List[float] = Field(
        [23.70, 23.70, 23.70, 23.57, 24.40, 26.20],
        example=[23.70, 23.70, 23.70, 23.57, 24.40, 26.20],
    )
    size: List[Union[int, float]] = Field(
        [10, 20, 30, 40, 50, 60],
        example=[10, 20, 30, 40, 50, 60],
    )
    color: List[str] = Field(
        ["red", "blue", "green", "yellow", "purple", "orange"],
        example=["red", "blue", "green", "yellow", "purple", "orange"],
    )
    alpha: Optional[float] = Field(0.5, example=0.5)


# 轉換matplotlib的figure為圖片並返回
def fig_to_image(fig):
    try:
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=300)
        img_buf.seek(0)
        return img_buf
    finally:
        # 確保figure被正確關閉以釋放記憶體
        import matplotlib.pyplot as plt

        plt.close(fig)


def cleanup_memory_if_needed():
    """根據請求計數定期清理記憶體"""
    global request_counter
    request_counter += 1

    if request_counter >= CLEANUP_INTERVAL:
        graph_instance.cleanup_memory()
        gc.collect()
        request_counter = 0


def handle_plot_request(plot_func, *args, **kwargs):
    """統一處理繪圖請求的記憶體管理"""
    try:
        cleanup_memory_if_needed()
        fig, _ = plot_func(*args, **kwargs)
        img_buf = fig_to_image(fig)
        return StreamingResponse(img_buf, media_type="image/png")
    except Exception as e:
        # 確保在錯誤情況下也清理記憶體
        graph_instance.cleanup_memory()
        raise HTTPException(status_code=500, detail=f"繪圖失敗: {str(e)}")


# 首頁端點，歡迎訊息
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """顯示歡迎訊息並提供API使用指南"""
    return templates.TemplateResponse("home.html", {"request": request})


# 基礎地圖邊界端點
@app.get("/boundary", summary="獲取地圖邊界")
async def get_boundary():
    """返回地圖的邊界圖"""
    return handle_plot_request(graph_instance.plot_boundary)


# 基礎地圖邊界端點+補助地區顏色
@app.get("/boundary_with_subsidy", summary="獲取帶補助地區顏色的地圖邊界")
async def get_boundary_with_subsidy():
    """返回帶補助地區顏色的地圖邊界圖"""
    return handle_plot_request(graph_instance.plot_boundary_with_subsidy)


# 分層設色圖端點
@app.post("/choropleth", summary="建立分層設色圖")
async def create_choropleth(data: ChoroplethData):
    """
    根據提供的資料建立分層設色圖

    - **data**: 包含地理資料的列表，至少需要包含'county'或'town'欄位
    - **column**: 用於著色的資料欄位名稱
    - **level**: 地理資料的層級，默認為'county'
    - **cmap**: 顏色映射，默認為'GnBu'
    - **colorbar_format**: 顏色條格式，默認為'{x:,.0f}'
    - **colorbar_tick_visible**: true/false，顏色條刻度是否可見，默認為true
    """
    df = pd.DataFrame(data.data)

    # 使用新的ChoroplethParams物件
    params = ChoroplethParams(
        data=df,
        column=data.column,
        level=data.level,
        cmap=data.cmap,
        colorbar_format=data.colorbar_format,
        colorbar_tick_visible=data.colorbar_tick_visible,
    )

    return handle_plot_request(graph_instance.plot_choropleth, params)


# 點圖端點
@app.post("/dot", summary="建立點散布圖")
async def create_dot_plot(data: DotPlotData):
    """
    根據提供的座標建立點散布圖

    - **x**: X座標列表
    - **y**: Y座標列表
    - **size**: 點的大小，默認為1
    - **color**: 點的顏色，默認為'red'
    - **alpha**: 透明度，默認為0.5
    """
    # 使用新的DotParams物件
    params = DotParams(
        x=data.x, y=data.y, size=data.size, color=data.color, alpha=data.alpha
    )

    return handle_plot_request(graph_instance.plot_dot, params)


# 2D直方圖端點
@app.post("/hist2d", summary="建立2D直方圖")
async def create_hist2d(data: Hist2DData):
    """
    根據提供的座標建立2D直方圖

    - **x**: X座標列表
    - **y**: Y座標列表
    - **bins**: 柱狀圖格數，默認為100
    - **cmap**: 顏色映射，默認為'GnBu'
    - **alpha**: 透明度，默認為0.5
    - **cmin**: 最小計數，默認為1
    """
    # 使用新的Hist2DParams物件
    params = Hist2DParams(
        x=data.x,
        y=data.y,
        bins=data.bins,
        cmap=data.cmap,
        alpha=data.alpha,
        cmin=data.cmin,
    )

    return handle_plot_request(graph_instance.plot_hist2d, params)


# 氣泡圖端點
@app.post("/bubble", summary="建立氣泡圖")
async def create_bubble(data: BubbleData):
    """
    根據提供的座標建立氣泡圖

    - **x**: X座標列表
    - **y**: Y座標列表
    - **size**: 氣泡大小，默認為10
    - **color**: 氣泡顏色，默認為'red'
    - **alpha**: 透明度，默認為0.5
    """
    # 使用新的BubbleParams物件
    params = BubbleParams(
        x=data.x, y=data.y, size=data.size, color=data.color, alpha=data.alpha
    )

    return handle_plot_request(graph_instance.plot_bubble, params)


# 添加手動清理記憶體的端點（用於測試和維護）
@app.post("/cleanup", summary="手動清理記憶體")
async def manual_cleanup():
    """手動觸發記憶體清理"""
    graph_instance.cleanup_memory()
    gc.collect()
    global request_counter
    request_counter = 0
    return {"message": "記憶體清理完成"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5011)
