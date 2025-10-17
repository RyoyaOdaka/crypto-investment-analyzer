from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.virtual_portfolio import VirtualPortfolio, VirtualHolding, VirtualTransaction
from app.schemas.virtual_portfolio import (
    VirtualPortfolioCreate,
    VirtualPortfolioSummary,
    VirtualHolding as VirtualHoldingSchema,
    VirtualTransaction as VirtualTransactionSchema,
    TradeRequest,
    TradeResponse
)
from app.services.crypto_service import crypto_service


class VirtualPortfolioService:
    """仮想ポートフォリオサービス"""

    async def create_portfolio(
        self,
        db: AsyncSession,
        portfolio_data: VirtualPortfolioCreate
    ) -> VirtualPortfolio:
        """仮想ポートフォリオを作成"""
        portfolio = VirtualPortfolio(
            name=portfolio_data.name,
            cash_balance=portfolio_data.cash_balance
        )
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        return portfolio

    async def get_portfolio(self, db: AsyncSession, portfolio_id: int) -> Optional[VirtualPortfolio]:
        """仮想ポートフォリオを取得"""
        result = await db.execute(
            select(VirtualPortfolio).where(VirtualPortfolio.id == portfolio_id)
        )
        return result.scalar_one_or_none()

    async def get_all_portfolios(self, db: AsyncSession) -> List[VirtualPortfolio]:
        """全ての仮想ポートフォリオを取得"""
        result = await db.execute(select(VirtualPortfolio))
        return list(result.scalars().all())

    async def delete_portfolio(self, db: AsyncSession, portfolio_id: int):
        """仮想ポートフォリオを削除"""
        await db.execute(
            delete(VirtualPortfolio).where(VirtualPortfolio.id == portfolio_id)
        )
        await db.commit()

    async def get_holdings(self, db: AsyncSession, portfolio_id: int) -> List[VirtualHoldingSchema]:
        """保有資産を取得（現在価格付き）"""
        result = await db.execute(
            select(VirtualHolding).where(VirtualHolding.portfolio_id == portfolio_id)
        )
        holdings = list(result.scalars().all())

        holdings_with_price = []
        for holding in holdings:
            # 現在価格を取得
            price_data = await crypto_service.get_price(holding.symbol)
            current_price = price_data.current_price if price_data else 0.0

            # 損益計算
            current_value = holding.amount * current_price
            cost_basis = holding.amount * holding.avg_purchase_price
            profit_loss = current_value - cost_basis
            profit_loss_percentage = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0.0

            holdings_with_price.append(VirtualHoldingSchema(
                id=holding.id,
                portfolio_id=holding.portfolio_id,
                symbol=holding.symbol,
                name=holding.name,
                amount=holding.amount,
                avg_purchase_price=holding.avg_purchase_price,
                current_price=current_price,
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percentage=profit_loss_percentage,
                created_at=holding.created_at,
                updated_at=holding.updated_at
            ))

        return holdings_with_price

    async def get_transactions(
        self,
        db: AsyncSession,
        portfolio_id: int,
        limit: int = 50
    ) -> List[VirtualTransaction]:
        """取引履歴を取得"""
        result = await db.execute(
            select(VirtualTransaction)
            .where(VirtualTransaction.portfolio_id == portfolio_id)
            .order_by(VirtualTransaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_portfolio_summary(
        self,
        db: AsyncSession,
        portfolio_id: int
    ) -> Optional[VirtualPortfolioSummary]:
        """ポートフォリオサマリーを取得"""
        portfolio = await self.get_portfolio(db, portfolio_id)
        if not portfolio:
            return None

        holdings = await self.get_holdings(db, portfolio_id)

        # 保有資産総額と損益を計算
        total_holdings_value = sum(h.current_value for h in holdings)
        total_cost = sum(h.amount * h.avg_purchase_price for h in holdings)
        total_value = portfolio.cash_balance + total_holdings_value
        total_profit_loss = total_holdings_value - total_cost
        total_profit_loss_percentage = (
            (total_profit_loss / total_cost * 100) if total_cost > 0 else 0.0
        )

        return VirtualPortfolioSummary(
            portfolio=portfolio,
            holdings=holdings,
            total_holdings_value=total_holdings_value,
            total_value=total_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percentage=total_profit_loss_percentage
        )

    async def execute_trade(
        self,
        db: AsyncSession,
        trade: TradeRequest
    ) -> TradeResponse:
        """取引を実行"""
        # ポートフォリオを取得
        portfolio = await self.get_portfolio(db, trade.portfolio_id)
        if not portfolio:
            return TradeResponse(
                success=False,
                message="ポートフォリオが見つかりません",
                transaction=None,
                portfolio_summary=None
            )

        # 現在価格を取得
        price_data = await crypto_service.get_price(trade.symbol)
        if not price_data:
            return TradeResponse(
                success=False,
                message=f"{trade.symbol}の価格データが取得できません",
                transaction=None,
                portfolio_summary=None
            )

        current_price = price_data.current_price
        total_value = trade.amount * current_price

        # 買い注文
        if trade.transaction_type == "buy":
            # 残高チェック
            if portfolio.cash_balance < total_value:
                return TradeResponse(
                    success=False,
                    message=f"残高不足です。必要額: ${total_value:.2f}, 残高: ${portfolio.cash_balance:.2f}",
                    transaction=None,
                    portfolio_summary=None
                )

            # 現金を減らす
            portfolio.cash_balance -= total_value

            # 保有資産を更新または新規作成
            result = await db.execute(
                select(VirtualHolding).where(
                    VirtualHolding.portfolio_id == trade.portfolio_id,
                    VirtualHolding.symbol == trade.symbol
                )
            )
            holding = result.scalar_one_or_none()

            if holding:
                # 既存保有資産の平均取得単価を更新
                total_amount = holding.amount + trade.amount
                total_cost = (holding.amount * holding.avg_purchase_price) + total_value
                holding.avg_purchase_price = total_cost / total_amount
                holding.amount = total_amount
            else:
                # 新規保有資産を作成
                holding = VirtualHolding(
                    portfolio_id=trade.portfolio_id,
                    symbol=trade.symbol,
                    name=price_data.name,
                    amount=trade.amount,
                    avg_purchase_price=current_price
                )
                db.add(holding)

        # 売り注文
        elif trade.transaction_type == "sell":
            # 保有資産を取得
            result = await db.execute(
                select(VirtualHolding).where(
                    VirtualHolding.portfolio_id == trade.portfolio_id,
                    VirtualHolding.symbol == trade.symbol
                )
            )
            holding = result.scalar_one_or_none()

            if not holding:
                return TradeResponse(
                    success=False,
                    message=f"{trade.symbol}を保有していません",
                    transaction=None,
                    portfolio_summary=None
                )

            if holding.amount < trade.amount:
                return TradeResponse(
                    success=False,
                    message=f"保有数量不足です。保有: {holding.amount}, 売却希望: {trade.amount}",
                    transaction=None,
                    portfolio_summary=None
                )

            # 現金を増やす
            portfolio.cash_balance += total_value

            # 保有資産を減らす
            holding.amount -= trade.amount

            # 保有数量がゼロになったら削除
            if holding.amount <= 0:
                await db.delete(holding)

        else:
            return TradeResponse(
                success=False,
                message="無効な取引タイプです (buy/sell のみ)",
                transaction=None,
                portfolio_summary=None
            )

        # 取引履歴を記録
        transaction = VirtualTransaction(
            portfolio_id=trade.portfolio_id,
            symbol=trade.symbol,
            name=price_data.name,
            transaction_type=trade.transaction_type,
            amount=trade.amount,
            price=current_price,
            total_value=total_value
        )
        db.add(transaction)

        await db.commit()
        await db.refresh(transaction)

        # 更新されたサマリーを取得
        summary = await self.get_portfolio_summary(db, trade.portfolio_id)

        return TradeResponse(
            success=True,
            message=f"{trade.transaction_type.upper()} 成功: {trade.amount} {trade.symbol} @ ${current_price:.2f}",
            transaction=VirtualTransactionSchema.model_validate(transaction),
            portfolio_summary=summary
        )


# グローバルインスタンス
virtual_portfolio_service = VirtualPortfolioService()
