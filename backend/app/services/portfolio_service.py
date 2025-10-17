from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioWithMetrics
from app.services.crypto_service import crypto_service


class PortfolioService:
    """ポートフォリオサービス"""

    async def create_portfolio(
        self,
        db: AsyncSession,
        portfolio_data: PortfolioCreate
    ) -> Portfolio:
        """ポートフォリオを作成"""
        portfolio = Portfolio(**portfolio_data.model_dump())
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        return portfolio

    async def get_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> Optional[Portfolio]:
        """IDでポートフォリオを取得"""
        result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        return result.scalar_one_or_none()

    async def get_portfolios(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Portfolio]:
        """すべてのポートフォリオを取得"""
        result = await db.execute(
            select(Portfolio).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int,
        portfolio_data: PortfolioUpdate
    ) -> Optional[Portfolio]:
        """ポートフォリオを更新"""
        portfolio = await self.get_portfolio(db, portfolio_id)
        if not portfolio:
            return None

        update_data = portfolio_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(portfolio, field, value)

        await db.commit()
        await db.refresh(portfolio)
        return portfolio

    async def delete_portfolio(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> bool:
        """ポートフォリオを削除"""
        result = await db.execute(
            delete(Portfolio).where(Portfolio.id == portfolio_id)
        )
        await db.commit()
        return result.rowcount > 0

    async def get_portfolio_with_metrics(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> Optional[PortfolioWithMetrics]:
        """メトリクス付きでポートフォリオを取得"""
        portfolio = await self.get_portfolio(db, portfolio_id)
        if not portfolio:
            return None

        # 現在価格を取得
        current_price_data = await crypto_service.get_price(portfolio.symbol)
        if not current_price_data:
            return None

        current_price = current_price_data.current_price
        current_value = portfolio.amount * current_price
        purchase_value = portfolio.amount * portfolio.purchase_price
        profit_loss = current_value - purchase_value
        profit_loss_percentage = (profit_loss / purchase_value) * 100 if purchase_value > 0 else 0

        return PortfolioWithMetrics(
            id=portfolio.id,
            symbol=portfolio.symbol,
            name=portfolio.name,
            amount=portfolio.amount,
            purchase_price=portfolio.purchase_price,
            purchase_date=portfolio.purchase_date,
            notes=portfolio.notes,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            current_price=current_price,
            current_value=current_value,
            purchase_value=purchase_value,
            profit_loss=profit_loss,
            profit_loss_percentage=profit_loss_percentage,
        )

    async def get_portfolios_with_metrics(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[PortfolioWithMetrics]:
        """メトリクス付きですべてのポートフォリオを取得"""
        portfolios = await self.get_portfolios(db, skip, limit)
        result = []

        for portfolio in portfolios:
            metrics = await self.get_portfolio_with_metrics(db, portfolio.id)
            if metrics:
                result.append(metrics)

        return result


# グローバルインスタンス
portfolio_service = PortfolioService()
