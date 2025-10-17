from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioWithMetrics,
    PortfolioListResponse,
)
from app.services.portfolio_service import portfolio_service


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/", response_model=PortfolioWithMetrics, status_code=201)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    新しいポートフォリオエントリを作成

    - **symbol**: 通貨シンボル（例: BTC, ETH）
    - **name**: 通貨名
    - **amount**: 保有数量
    - **purchase_price**: 購入時の単価（USD）
    - **purchase_date**: 購入日時
    - **notes**: メモ（オプション）
    """
    portfolio = await portfolio_service.create_portfolio(db, portfolio_data)
    return await portfolio_service.get_portfolio_with_metrics(db, portfolio.id)


@router.get("/", response_model=PortfolioListResponse)
async def get_portfolios(
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=100, description="取得する件数"),
    db: AsyncSession = Depends(get_db)
):
    """
    すべてのポートフォリオを取得（メトリクス付き）

    - **skip**: スキップする件数
    - **limit**: 取得する件数（最大100）
    """
    portfolios_with_metrics = await portfolio_service.get_portfolios_with_metrics(db, skip, limit)

    # 合計を計算
    total_value = sum(p.current_value for p in portfolios_with_metrics)
    total_purchase_value = sum(p.purchase_value for p in portfolios_with_metrics)
    total_profit_loss = total_value - total_purchase_value
    total_profit_loss_percentage = (
        (total_profit_loss / total_purchase_value) * 100
        if total_purchase_value > 0
        else 0
    )

    return PortfolioListResponse(
        portfolios=portfolios_with_metrics,
        total=len(portfolios_with_metrics),
        total_value=total_value,
        total_profit_loss=total_profit_loss,
        total_profit_loss_percentage=total_profit_loss_percentage,
    )


@router.get("/{portfolio_id}", response_model=PortfolioWithMetrics)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    特定のポートフォリオを取得（メトリクス付き）

    - **portfolio_id**: ポートフォリオID
    """
    portfolio = await portfolio_service.get_portfolio_with_metrics(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioWithMetrics)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    ポートフォリオを更新

    - **portfolio_id**: ポートフォリオID
    - **amount**: 保有数量（オプション）
    - **purchase_price**: 購入時の単価（オプション）
    - **purchase_date**: 購入日時（オプション）
    - **notes**: メモ（オプション）
    """
    portfolio = await portfolio_service.update_portfolio(db, portfolio_id, portfolio_data)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return await portfolio_service.get_portfolio_with_metrics(db, portfolio.id)


@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ポートフォリオを削除

    - **portfolio_id**: ポートフォリオID
    """
    success = await portfolio_service.delete_portfolio(db, portfolio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return None
