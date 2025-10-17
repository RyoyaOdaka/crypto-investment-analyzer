from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VirtualPortfolioBase(BaseModel):
    """仮想ポートフォリオベース"""
    name: str = Field("My Virtual Portfolio", description="ポートフォリオ名")
    cash_balance: float = Field(10000.0, description="現金残高（USD）")


class VirtualPortfolioCreate(VirtualPortfolioBase):
    """仮想ポートフォリオ作成"""
    pass


class VirtualPortfolio(VirtualPortfolioBase):
    """仮想ポートフォリオ"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VirtualHoldingBase(BaseModel):
    """仮想保有資産ベース"""
    symbol: str = Field(..., description="通貨シンボル")
    name: str = Field(..., description="通貨名")
    amount: float = Field(..., description="保有数量")
    avg_purchase_price: float = Field(..., description="平均取得単価")


class VirtualHolding(VirtualHoldingBase):
    """仮想保有資産"""
    id: int
    portfolio_id: int
    current_price: float = Field(..., description="現在価格")
    current_value: float = Field(..., description="現在評価額")
    profit_loss: float = Field(..., description="損益")
    profit_loss_percentage: float = Field(..., description="損益率（%）")
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VirtualTransactionBase(BaseModel):
    """仮想取引ベース"""
    symbol: str = Field(..., description="通貨シンボル")
    name: str = Field(..., description="通貨名")
    transaction_type: str = Field(..., description="取引タイプ (buy/sell)")
    amount: float = Field(..., description="取引数量")
    price: float = Field(..., description="取引価格")


class VirtualTransactionCreate(VirtualTransactionBase):
    """仮想取引作成"""
    portfolio_id: int = Field(..., description="ポートフォリオID")


class VirtualTransaction(VirtualTransactionBase):
    """仮想取引"""
    id: int
    portfolio_id: int
    total_value: float = Field(..., description="取引総額")
    created_at: datetime

    class Config:
        from_attributes = True


class VirtualPortfolioSummary(BaseModel):
    """仮想ポートフォリオサマリー"""
    portfolio: VirtualPortfolio
    holdings: List[VirtualHolding]
    total_holdings_value: float = Field(..., description="保有資産総額")
    total_value: float = Field(..., description="総資産（現金+保有資産）")
    total_profit_loss: float = Field(..., description="総損益")
    total_profit_loss_percentage: float = Field(..., description="総損益率（%）")


class TradeRequest(BaseModel):
    """取引リクエスト"""
    portfolio_id: int = Field(..., description="ポートフォリオID")
    symbol: str = Field(..., description="通貨シンボル")
    transaction_type: str = Field(..., description="取引タイプ (buy/sell)")
    amount: float = Field(..., description="取引数量", gt=0)


class TradeResponse(BaseModel):
    """取引レスポンス"""
    success: bool
    message: str
    transaction: Optional[VirtualTransaction]
    portfolio_summary: Optional[VirtualPortfolioSummary]
