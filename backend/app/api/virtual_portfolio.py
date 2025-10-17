from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.virtual_portfolio import (
    VirtualPortfolioCreate,
    VirtualPortfolio,
    VirtualPortfolioSummary,
    VirtualTransaction,
    TradeRequest,
    TradeResponse
)
from app.services.virtual_portfolio_service import virtual_portfolio_service

router = APIRouter(prefix="/virtual-portfolio", tags=["virtual-portfolio"])


@router.post("/", response_model=VirtualPortfolio)
async def create_portfolio(
    portfolio: VirtualPortfolioCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    仮想ポートフォリオを作成
    """
    return await virtual_portfolio_service.create_portfolio(db, portfolio)


@router.get("/", response_model=List[VirtualPortfolio])
async def get_portfolios(db: AsyncSession = Depends(get_db)):
    """
    全ての仮想ポートフォリオを取得
    """
    return await virtual_portfolio_service.get_all_portfolios(db)


@router.get("/{portfolio_id}", response_model=VirtualPortfolio)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    仮想ポートフォリオを取得
    """
    portfolio = await virtual_portfolio_service.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.get("/{portfolio_id}/summary", response_model=VirtualPortfolioSummary)
async def get_portfolio_summary(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ポートフォリオサマリーを取得（保有資産、損益含む）
    """
    summary = await virtual_portfolio_service.get_portfolio_summary(db, portfolio_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return summary


@router.get("/{portfolio_id}/transactions", response_model=List[VirtualTransaction])
async def get_transactions(
    portfolio_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    取引履歴を取得
    """
    return await virtual_portfolio_service.get_transactions(db, portfolio_id, limit)


@router.post("/trade", response_model=TradeResponse)
async def execute_trade(
    trade: TradeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    取引を実行（買い/売り）
    """
    return await virtual_portfolio_service.execute_trade(db, trade)


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    仮想ポートフォリオを削除
    """
    portfolio = await virtual_portfolio_service.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    await virtual_portfolio_service.delete_portfolio(db, portfolio_id)
    return {"message": "Portfolio deleted successfully"}
