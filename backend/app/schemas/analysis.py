from pydantic import BaseModel, Field
from typing import Optional


class TechnicalIndicators(BaseModel):
    """テクニカル指標"""
    rsi: Optional[float] = Field(None, description="RSI (0-100)")
    volatility: float = Field(..., description="ボラティリティ（%）")
    trend: str = Field(..., description="トレンド (bullish/bearish/neutral)")
    trend_strength: float = Field(..., description="トレンド強度 (0-100)")
    price_change_7d: float = Field(..., description="7日間の価格変動率（%）")
    price_change_30d: float = Field(..., description="30日間の価格変動率（%）")


class InvestmentRecommendation(BaseModel):
    """投資推奨"""
    symbol: str = Field(..., description="通貨シンボル")
    name: str = Field(..., description="通貨名")
    current_price: float = Field(..., description="現在価格（USD）")
    recommendation_score: float = Field(..., description="推奨スコア (0-100)")
    recommendation: str = Field(..., description="推奨アクション (strong_buy/buy/hold/sell)")
    risk_level: str = Field(..., description="リスクレベル (low/medium/high)")
    technical_indicators: TechnicalIndicators
    reasoning: str = Field(..., description="推奨理由")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 45000.50,
                "recommendation_score": 75.5,
                "recommendation": "buy",
                "risk_level": "medium",
                "technical_indicators": {
                    "rsi": 45.2,
                    "volatility": 3.5,
                    "trend": "bullish",
                    "trend_strength": 68.0,
                    "price_change_7d": 5.2,
                    "price_change_30d": 12.8
                },
                "reasoning": "上昇トレンド継続中、RSIは買われすぎ水準ではない"
            }
        }


class InvestmentAnalysisResponse(BaseModel):
    """投資分析レスポンス"""
    recommendations: list[InvestmentRecommendation]
    total: int = Field(..., description="分析した通貨数")
