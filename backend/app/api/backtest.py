from fastapi import APIRouter, HTTPException
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/backtest", tags=["backtest"])


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    バックテストを実行

    指定された戦略で過去データをバックテストし、パフォーマンス指標を返す
    """
    try:
        result = await backtest_service.run_backtest(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/strategies")
async def get_available_strategies():
    """
    利用可能な戦略リストを取得
    """
    return {
        "buy_signals": [
            {"value": "rsi_oversold", "label": "RSI売られすぎ (< 30)"},
            {"value": "macd_golden_cross", "label": "MACDゴールデンクロス"},
            {"value": "bb_lower_breach", "label": "ボリンジャーバンド下限突破"}
        ],
        "sell_signals": [
            {"value": "rsi_overbought", "label": "RSI買われすぎ (> 70)"},
            {"value": "macd_dead_cross", "label": "MACDデッドクロス"},
            {"value": "bb_upper_breach", "label": "ボリンジャーバンド上限突破"}
        ]
    }
