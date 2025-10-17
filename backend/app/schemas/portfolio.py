from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PortfolioBase(BaseModel):
    """ポートフォリオベーススキーマ"""
    symbol: str = Field(..., description="通貨シンボル（例: BTC, ETH）")
    name: str = Field(..., description="通貨名")
    amount: float = Field(..., gt=0, description="保有数量")
    purchase_price: float = Field(..., gt=0, description="購入時の単価（USD）")
    purchase_date: datetime = Field(..., description="購入日時")
    notes: Optional[str] = Field(None, description="メモ")


class PortfolioCreate(PortfolioBase):
    """ポートフォリオ作成スキーマ"""
    pass


class PortfolioUpdate(BaseModel):
    """ポートフォリオ更新スキーマ"""
    amount: Optional[float] = Field(None, gt=0, description="保有数量")
    purchase_price: Optional[float] = Field(None, gt=0, description="購入時の単価（USD）")
    purchase_date: Optional[datetime] = Field(None, description="購入日時")
    notes: Optional[str] = Field(None, description="メモ")


class PortfolioInDB(PortfolioBase):
    """データベースのポートフォリオスキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioWithMetrics(PortfolioInDB):
    """メトリクス付きポートフォリオスキーマ"""
    current_price: float = Field(..., description="現在価格（USD）")
    current_value: float = Field(..., description="現在の評価額（USD）")
    purchase_value: float = Field(..., description="購入時の総額（USD）")
    profit_loss: float = Field(..., description="損益（USD）")
    profit_loss_percentage: float = Field(..., description="損益率（%）")

    class Config:
        from_attributes = True


class PortfolioListResponse(BaseModel):
    """ポートフォリオリストレスポンス"""
    portfolios: list[PortfolioWithMetrics]
    total: int = Field(..., description="総件数")
    total_value: float = Field(..., description="ポートフォリオ全体の評価額（USD）")
    total_profit_loss: float = Field(..., description="ポートフォリオ全体の損益（USD）")
    total_profit_loss_percentage: float = Field(..., description="ポートフォリオ全体の損益率（%）")
