import httpx
from typing import Optional, List
from datetime import datetime
from app.schemas.crypto import CryptoPriceResponse, ChartDataResponse, ChartDataPoint
from app.services.redis_service import redis_service


class CryptoService:
    """仮想通貨価格取得サービス"""

    COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
    CACHE_EXPIRE_SECONDS = 60  # 1分間キャッシュ

    # 主要な仮想通貨のマッピング
    COIN_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "ADA": "cardano",
        "SOL": "solana",
        "DOT": "polkadot",
        "DOGE": "dogecoin",
        "AVAX": "avalanche-2",
        "MATIC": "matic-network",
    }

    async def get_price(self, symbol: str) -> Optional[CryptoPriceResponse]:
        """
        指定された通貨の価格を取得

        Args:
            symbol: 通貨シンボル（例: BTC, ETH）

        Returns:
            CryptoPriceResponse or None
        """
        # キャッシュから取得を試みる
        cache_key = f"crypto:price:{symbol.upper()}"
        cached_data = await redis_service.get(cache_key)

        if cached_data:
            return CryptoPriceResponse(**cached_data)

        # CoinGecko APIから取得
        coin_id = self.COIN_ID_MAP.get(symbol.upper())
        if not coin_id:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API_BASE}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "ids": coin_id,
                        "order": "market_cap_desc",
                        "sparkline": "false"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if not data or len(data) == 0:
                    return None

                coin_data = data[0]
                price_response = CryptoPriceResponse(
                    symbol=symbol.upper(),
                    name=coin_data.get("name", ""),
                    current_price=coin_data.get("current_price", 0.0),
                    price_change_24h=coin_data.get("price_change_24h"),
                    price_change_percentage_24h=coin_data.get("price_change_percentage_24h"),
                    market_cap=coin_data.get("market_cap"),
                    total_volume=coin_data.get("total_volume"),
                    high_24h=coin_data.get("high_24h"),
                    low_24h=coin_data.get("low_24h"),
                    last_updated=datetime.fromisoformat(
                        coin_data.get("last_updated", datetime.now().isoformat()).replace("Z", "+00:00")
                    )
                )

                # キャッシュに保存
                await redis_service.set(
                    cache_key,
                    price_response.model_dump(),
                    expire=self.CACHE_EXPIRE_SECONDS
                )

                return price_response

        except httpx.HTTPError as e:
            print(f"CoinGecko API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    async def get_multiple_prices(self, symbols: List[str]) -> List[CryptoPriceResponse]:
        """
        複数の通貨の価格を取得

        Args:
            symbols: 通貨シンボルのリスト

        Returns:
            CryptoPriceResponseのリスト
        """
        results = []
        for symbol in symbols:
            price = await self.get_price(symbol)
            if price:
                results.append(price)
        return results

    async def get_top_coins(self, limit: int = 10) -> List[CryptoPriceResponse]:
        """
        時価総額トップの通貨を取得

        Args:
            limit: 取得する通貨数

        Returns:
            CryptoPriceResponseのリスト
        """
        cache_key = f"crypto:top:{limit}"
        cached_data = await redis_service.get(cache_key)

        if cached_data:
            return [CryptoPriceResponse(**item) for item in cached_data]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API_BASE}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": limit,
                        "page": 1,
                        "sparkline": "false"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for coin_data in data:
                    # シンボルを探す
                    symbol = coin_data.get("symbol", "").upper()

                    price_response = CryptoPriceResponse(
                        symbol=symbol,
                        name=coin_data.get("name", ""),
                        current_price=coin_data.get("current_price", 0.0),
                        price_change_24h=coin_data.get("price_change_24h"),
                        price_change_percentage_24h=coin_data.get("price_change_percentage_24h"),
                        market_cap=coin_data.get("market_cap"),
                        total_volume=coin_data.get("total_volume"),
                        high_24h=coin_data.get("high_24h"),
                        low_24h=coin_data.get("low_24h"),
                        last_updated=datetime.fromisoformat(
                            coin_data.get("last_updated", datetime.now().isoformat()).replace("Z", "+00:00")
                        )
                    )
                    results.append(price_response)

                # キャッシュに保存
                await redis_service.set(
                    cache_key,
                    [r.model_dump() for r in results],
                    expire=self.CACHE_EXPIRE_SECONDS
                )

                return results

        except httpx.HTTPError as e:
            print(f"CoinGecko API error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []


    async def get_chart_data(
        self,
        symbol: str,
        days: int = 7
    ) -> Optional[ChartDataResponse]:
        """
        指定された通貨のチャートデータを取得

        Args:
            symbol: 通貨シンボル（例: BTC, ETH）
            days: 取得する日数（1, 7, 30, 90, 180, 365）

        Returns:
            ChartDataResponse or None
        """
        # キャッシュから取得を試みる
        cache_key = f"crypto:chart:{symbol.upper()}:{days}"
        cached_data = await redis_service.get(cache_key)

        if cached_data:
            return ChartDataResponse(**cached_data)

        # CoinGecko APIから取得
        coin_id = self.COIN_ID_MAP.get(symbol.upper())
        if not coin_id:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.COINGECKO_API_BASE}/coins/{coin_id}/market_chart",
                    params={
                        "vs_currency": "usd",
                        "days": days,
                        "interval": "daily" if days > 1 else "hourly"
                    },
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()

                if not data or "prices" not in data:
                    return None

                # 価格データを変換
                price_points = [
                    ChartDataPoint(
                        timestamp=int(price[0]),
                        price=float(price[1])
                    )
                    for price in data["prices"]
                ]

                # 通貨名を取得
                coin_name = symbol.upper()
                for coin_map_symbol, coin_map_id in self.COIN_ID_MAP.items():
                    if coin_map_id == coin_id:
                        # 簡易的に名前を設定（本来は別APIで取得すべき）
                        name_map = {
                            "BTC": "Bitcoin",
                            "ETH": "Ethereum",
                            "BNB": "Binance Coin",
                            "XRP": "Ripple",
                            "ADA": "Cardano",
                            "SOL": "Solana",
                            "DOT": "Polkadot",
                            "DOGE": "Dogecoin",
                            "AVAX": "Avalanche",
                            "MATIC": "Polygon",
                        }
                        coin_name = name_map.get(coin_map_symbol, coin_map_symbol)
                        break

                chart_response = ChartDataResponse(
                    symbol=symbol.upper(),
                    name=coin_name,
                    prices=price_points,
                    total_points=len(price_points)
                )

                # キャッシュに保存（チャートデータは5分間キャッシュ）
                await redis_service.set(
                    cache_key,
                    chart_response.model_dump(),
                    expire=300  # 5分
                )

                return chart_response

        except httpx.HTTPError as e:
            print(f"CoinGecko API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


# グローバルインスタンス
crypto_service = CryptoService()
