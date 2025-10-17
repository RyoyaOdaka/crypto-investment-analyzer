from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Portfolio(Base):
    """ポートフォリオモデル"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)  # 通貨シンボル（BTC, ETH, etc.）
    name = Column(String(100), nullable=False)  # 通貨名
    amount = Column(Float, nullable=False)  # 保有数量
    purchase_price = Column(Float, nullable=False)  # 購入時の単価（USD）
    purchase_date = Column(DateTime(timezone=True), nullable=False)  # 購入日時
    notes = Column(Text, nullable=True)  # メモ
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 作成日時
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 更新日時

    def __repr__(self):
        return f"<Portfolio(id={self.id}, symbol={self.symbol}, amount={self.amount})>"
