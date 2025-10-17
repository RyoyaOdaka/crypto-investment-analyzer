from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CryptoPriceResponse(BaseModel):
    """仮想通貨価格レスポンス"""
    symbol: str = Field(..., description="通貨シンボル（例: BTC, ETH）")
    name: str = Field(..., description="通貨名")
    current_price: float = Field(..., description="現在価格（USD）")
    price_change_24h: Optional[float] = Field(None, description="24時間価格変動（USD）")
    price_change_percentage_24h: Optional[float] = Field(None, description="24時間価格変動率（%）")
    market_cap: Optional[float] = Field(None, description="時価総額（USD）")
    total_volume: Optional[float] = Field(None, description="24時間取引量（USD）")
    high_24h: Optional[float] = Field(None, description="24時間最高価格（USD）")
    low_24h: Optional[float] = Field(None, description="24時間最低価格（USD）")
    last_updated: datetime = Field(..., description="最終更新時刻")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 45000.50,
                "price_change_24h": 1250.75,
                "price_change_percentage_24h": 2.85,
                "market_cap": 880000000000,
                "total_volume": 35000000000,
                "high_24h": 45500.00,
                "low_24h": 43200.00,
                "last_updated": "2024-01-01T12:00:00Z"
            }
        }


class CryptoListResponse(BaseModel):
    """仮想通貨リストレスポンス"""
    coins: list[CryptoPriceResponse]
    total: int = Field(..., description="取得した通貨数")


class ChartDataPoint(BaseModel):
    """チャートデータポイント"""
    timestamp: int = Field(..., description="UNIXタイムスタンプ（ミリ秒）")
    price: float = Field(..., description="価格（USD）")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": 1704067200000,
                "price": 45000.50
            }
        }


class ChartDataResponse(BaseModel):
    """チャートデータレスポンス"""
    symbol: str = Field(..., description="通貨シンボル")
    name: str = Field(..., description="通貨名")
    prices: list[ChartDataPoint] = Field(..., description="価格データポイントのリスト")
    total_points: int = Field(..., description="データポイント数")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "name": "Bitcoin",
                "prices": [
                    {"timestamp": 1704067200000, "price": 45000.50},
                    {"timestamp": 1704153600000, "price": 45500.75}
                ],
                "total_points": 2
            }
        }
