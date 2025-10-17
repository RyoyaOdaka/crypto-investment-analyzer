from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BacktestStrategy(BaseModel):
    """バックテスト戦略"""
    name: str = Field(..., description="戦略名")
    buy_signal: str = Field(..., description="買いシグナル条件 (rsi_oversold/macd_golden_cross/bb_lower_breach)")
    sell_signal: str = Field(..., description="売りシグナル条件 (rsi_overbought/macd_dead_cross/bb_upper_breach)")
    initial_capital: float = Field(10000.0, description="初期資金（USD）")
    trade_size_percent: float = Field(100.0, description="1回の取引で使用する資金の割合（%）")


class BacktestTrade(BaseModel):
    """バックテスト取引記録"""
    trade_id: int = Field(..., description="取引ID")
    type: str = Field(..., description="取引タイプ (buy/sell)")
    timestamp: datetime = Field(..., description="取引時刻")
    price: float = Field(..., description="取引価格")
    amount: float = Field(..., description="取引数量")
    value: float = Field(..., description="取引金額")
    profit_loss: Optional[float] = Field(None, description="損益（売却時のみ）")
    profit_loss_percent: Optional[float] = Field(None, description="損益率（売却時のみ）")


class BacktestMetrics(BaseModel):
    """バックテストパフォーマンス指標"""
    total_trades: int = Field(..., description="総取引回数")
    winning_trades: int = Field(..., description="勝ちトレード数")
    losing_trades: int = Field(..., description="負けトレード数")
    win_rate: float = Field(..., description="勝率（%）")
    total_return: float = Field(..., description="総リターン（USD）")
    total_return_percent: float = Field(..., description="総リターン率（%）")
    max_drawdown: float = Field(..., description="最大ドローダウン（%）")
    sharpe_ratio: Optional[float] = Field(None, description="シャープレシオ")
    avg_profit_per_trade: float = Field(..., description="平均利益/取引（USD）")
    avg_profit_per_winning_trade: float = Field(..., description="平均利益/勝ちトレード（USD）")
    avg_loss_per_losing_trade: float = Field(..., description="平均損失/負けトレード（USD）")


class BacktestRequest(BaseModel):
    """バックテストリクエスト"""
    symbol: str = Field(..., description="通貨シンボル")
    strategy: BacktestStrategy
    period_days: int = Field(90, description="バックテスト期間（日数）")


class BacktestResponse(BaseModel):
    """バックテストレスポンス"""
    symbol: str = Field(..., description="通貨シンボル")
    name: str = Field(..., description="通貨名")
    strategy: BacktestStrategy
    start_date: datetime = Field(..., description="バックテスト開始日")
    end_date: datetime = Field(..., description="バックテスト終了日")
    initial_capital: float = Field(..., description="初期資金")
    final_capital: float = Field(..., description="最終資金")
    trades: List[BacktestTrade] = Field(..., description="取引履歴")
    metrics: BacktestMetrics = Field(..., description="パフォーマンス指標")
    equity_curve: List[dict] = Field(..., description="資産曲線 [{timestamp, value}]")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "name": "Bitcoin",
                "strategy": {
                    "name": "RSI Reversal",
                    "buy_signal": "rsi_oversold",
                    "sell_signal": "rsi_overbought",
                    "initial_capital": 10000.0,
                    "trade_size_percent": 100.0
                },
                "start_date": "2024-07-01T00:00:00Z",
                "end_date": "2024-10-01T00:00:00Z",
                "initial_capital": 10000.0,
                "final_capital": 12500.0,
                "trades": [],
                "metrics": {
                    "total_trades": 10,
                    "winning_trades": 6,
                    "losing_trades": 4,
                    "win_rate": 60.0,
                    "total_return": 2500.0,
                    "total_return_percent": 25.0,
                    "max_drawdown": -15.5,
                    "sharpe_ratio": 1.5,
                    "avg_profit_per_trade": 250.0,
                    "avg_profit_per_winning_trade": 500.0,
                    "avg_loss_per_losing_trade": -200.0
                },
                "equity_curve": []
            }
        }
