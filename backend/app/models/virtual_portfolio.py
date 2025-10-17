from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class VirtualPortfolio(Base):
    """仮想ポートフォリオ"""
    __tablename__ = "virtual_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="My Virtual Portfolio")
    cash_balance = Column(Float, nullable=False, default=10000.0)  # 現金残高（USD）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VirtualHolding(Base):
    """仮想保有資産"""
    __tablename__ = "virtual_holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)  # 保有数量
    avg_purchase_price = Column(Float, nullable=False)  # 平均取得単価
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VirtualTransaction(Base):
    """仮想取引履歴"""
    __tablename__ = "virtual_transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("virtual_portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # "buy" or "sell"
    amount = Column(Float, nullable=False)  # 取引数量
    price = Column(Float, nullable=False)  # 取引価格
    total_value = Column(Float, nullable=False)  # 取引総額
    created_at = Column(DateTime(timezone=True), server_default=func.now())
