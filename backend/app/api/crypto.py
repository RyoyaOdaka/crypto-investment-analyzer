from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.crypto import CryptoPriceResponse, CryptoListResponse, ChartDataResponse
from app.services.crypto_service import crypto_service


router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/price/{symbol}", response_model=CryptoPriceResponse)
async def get_crypto_price(symbol: str):
    """
    指定された仮想通貨の現在価格を取得

    - **symbol**: 通貨シンボル（例: BTC, ETH, SOL）
    """
    price = await crypto_service.get_price(symbol.upper())

    if not price:
        raise HTTPException(
            status_code=404,
            detail=f"Cryptocurrency '{symbol.upper()}' not found or not supported"
        )

    return price


@router.get("/prices", response_model=CryptoListResponse)
async def get_multiple_prices(
    symbols: List[str] = Query(
        ...,
        description="通貨シンボルのリスト",
        example=["BTC", "ETH", "SOL"]
    )
):
    """
    複数の仮想通貨の価格を一括取得

    - **symbols**: 通貨シンボルのリスト（例: BTC,ETH,SOL）
    """
    prices = await crypto_service.get_multiple_prices([s.upper() for s in symbols])

    return CryptoListResponse(
        coins=prices,
        total=len(prices)
    )


@router.get("/top", response_model=CryptoListResponse)
async def get_top_cryptocurrencies(
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="取得する通貨数（1-50）"
    )
):
    """
    時価総額トップの仮想通貨を取得

    - **limit**: 取得する通貨数（デフォルト: 10、最大: 50）
    """
    coins = await crypto_service.get_top_coins(limit)

    return CryptoListResponse(
        coins=coins,
        total=len(coins)
    )


@router.get("/chart/{symbol}", response_model=ChartDataResponse)
async def get_crypto_chart(
    symbol: str,
    days: int = Query(
        7,
        ge=1,
        le=365,
        description="取得する日数（1-365）"
    )
):
    """
    指定された仮想通貨のチャートデータを取得

    - **symbol**: 通貨シンボル（例: BTC, ETH, SOL）
    - **days**: 取得する日数（1日、7日、30日、90日、180日、365日）
    """
    chart_data = await crypto_service.get_chart_data(symbol.upper(), days)

    if not chart_data:
        raise HTTPException(
            status_code=404,
            detail=f"Chart data for cryptocurrency '{symbol.upper()}' not found or not supported"
        )

    return chart_data
