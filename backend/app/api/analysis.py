from fastapi import APIRouter, HTTPException, Query
from app.schemas.analysis import InvestmentRecommendation, InvestmentAnalysisResponse
from app.services.analysis_service import analysis_service


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/recommend/{symbol}", response_model=InvestmentRecommendation)
async def get_investment_recommendation(symbol: str):
    """
    指定された仮想通貨の投資推奨を取得

    - **symbol**: 通貨シンボル（例: BTC, ETH, SOL）

    テクニカル指標に基づいて投資推奨スコアとアクションを返します。
    """
    try:
        recommendation = await analysis_service.analyze_coin(symbol.upper())
        return recommendation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/recommendations", response_model=InvestmentAnalysisResponse)
async def get_top_recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=10,
        description="分析する通貨数（1-10）"
    )
):
    """
    主要仮想通貨の投資推奨をスコア順に取得

    - **limit**: 分析する通貨数（デフォルト: 10、最大: 10）

    推奨スコアが高い順に並べて返します。
    """
    try:
        recommendations = await analysis_service.analyze_top_coins(limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
