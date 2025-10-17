from typing import List
import statistics
from app.schemas.analysis import (
    InvestmentRecommendation,
    TechnicalIndicators,
    InvestmentAnalysisResponse,
    MACDIndicator,
    BollingerBands
)
from app.services.crypto_service import crypto_service


class AnalysisService:
    """投資分析サービス"""

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """EMA（指数移動平均）を計算"""
        if len(prices) < period:
            return []

        ema = []
        multiplier = 2 / (period + 1)

        # 最初のEMAはSMA
        sma = sum(prices[:period]) / period
        ema.append(sma)

        # その後はEMA計算
        for i in range(period, len(prices)):
            ema_value = (prices[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(ema_value)

        return ema

    def calculate_macd(self, prices: List[float]) -> MACDIndicator:
        """MACD（移動平均収束拡散）を計算"""
        if len(prices) < 26:
            return MACDIndicator(
                macd_line=0,
                signal_line=0,
                histogram=0,
                signal="neutral"
            )

        # 12日と26日のEMAを計算
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)

        if not ema_12 or not ema_26:
            return MACDIndicator(
                macd_line=0,
                signal_line=0,
                histogram=0,
                signal="neutral"
            )

        # MACDライン = 12日EMA - 26日EMA
        macd_line_values = [ema_12[i] - ema_26[i] for i in range(len(ema_26))]

        # シグナルライン = MACDラインの9日EMA
        signal_line_values = self.calculate_ema(macd_line_values, 9)

        if not signal_line_values:
            return MACDIndicator(
                macd_line=macd_line_values[-1],
                signal_line=0,
                histogram=macd_line_values[-1],
                signal="neutral"
            )

        macd_line = macd_line_values[-1]
        signal_line = signal_line_values[-1]
        histogram = macd_line - signal_line

        # シグナル判定
        if len(macd_line_values) >= 2 and len(signal_line_values) >= 2:
            prev_histogram = macd_line_values[-2] - signal_line_values[-2]
            if prev_histogram < 0 and histogram > 0:
                signal = "buy"  # ゴールデンクロス
            elif prev_histogram > 0 and histogram < 0:
                signal = "sell"  # デッドクロス
            else:
                signal = "neutral"
        else:
            signal = "neutral"

        return MACDIndicator(
            macd_line=macd_line,
            signal_line=signal_line,
            histogram=histogram,
            signal=signal
        )

    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> BollingerBands:
        """ボリンジャーバンドを計算"""
        if len(prices) < period:
            middle = sum(prices) / len(prices)
            return BollingerBands(
                upper_band=middle,
                middle_band=middle,
                lower_band=middle,
                current_position="middle"
            )

        # 中央線（SMA）
        recent_prices = prices[-period:]
        middle_band = sum(recent_prices) / period

        # 標準偏差
        variance = sum((p - middle_band) ** 2 for p in recent_prices) / period
        std = variance ** 0.5

        # 上下バンド
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        # 現在価格の位置
        current_price = prices[-1]
        if current_price > upper_band:
            position = "above_upper"
        elif current_price > middle_band:
            position = "upper_half"
        elif current_price > lower_band:
            position = "lower_half"
        else:
            position = "below_lower"

        return BollingerBands(
            upper_band=upper_band,
            middle_band=middle_band,
            lower_band=lower_band,
            current_position=position
        )

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI（相対力指数）を計算"""
        if len(prices) < period + 1:
            return 50.0  # データ不足の場合は中立値

        # 価格変動を計算
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        # 上昇と下落を分離
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_volatility(self, prices: List[float]) -> float:
        """ボラティリティ（標準偏差）を計算"""
        if len(prices) < 2:
            return 0.0

        # 価格変動率を計算
        returns = [(prices[i] - prices[i-1]) / prices[i-1] * 100
                   for i in range(1, len(prices))]

        return statistics.stdev(returns) if len(returns) > 1 else 0.0

    def calculate_trend(self, prices: List[float]) -> tuple[str, float]:
        """トレンドとその強度を計算"""
        if len(prices) < 2:
            return "neutral", 0.0

        # 線形回帰の傾きを簡易計算
        n = len(prices)
        x_mean = (n - 1) / 2
        y_mean = sum(prices) / n

        numerator = sum((i - x_mean) * (prices[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "neutral", 0.0

        slope = numerator / denominator

        # トレンド強度を計算（傾きを正規化）
        price_range = max(prices) - min(prices)
        if price_range == 0:
            return "neutral", 0.0

        trend_strength = abs(slope * n / y_mean) * 100
        trend_strength = min(trend_strength, 100.0)  # 0-100にクリップ

        # トレンド判定
        if slope > 0 and trend_strength > 20:
            trend = "bullish"
        elif slope < 0 and trend_strength > 20:
            trend = "bearish"
        else:
            trend = "neutral"

        return trend, trend_strength

    def calculate_recommendation_score(
        self,
        rsi: float,
        trend: str,
        trend_strength: float,
        volatility: float,
        price_change_7d: float,
        price_change_30d: float,
        macd: MACDIndicator,
        bollinger_bands: BollingerBands
    ) -> tuple[float, str, str]:
        """推奨スコアとアクションを計算"""
        score = 50.0  # ベーススコア

        # RSIによるスコア調整
        if rsi < 30:  # 売られすぎ → 買い推奨
            score += 20
        elif rsi > 70:  # 買われすぎ → 売り推奨
            score -= 20
        elif 40 <= rsi <= 60:  # 中立
            score += 5

        # トレンドによるスコア調整
        if trend == "bullish":
            score += trend_strength * 0.3
        elif trend == "bearish":
            score -= trend_strength * 0.3

        # 価格変動によるスコア調整
        if price_change_7d > 5 and price_change_30d > 10:
            score += 15  # 強い上昇トレンド
        elif price_change_7d < -5 and price_change_30d < -10:
            score -= 15  # 強い下降トレンド

        # MACDによるスコア調整
        if macd.signal == "buy":  # ゴールデンクロス
            score += 15
        elif macd.signal == "sell":  # デッドクロス
            score -= 15
        # ヒストグラムの方向性
        if macd.histogram > 0:
            score += 5
        elif macd.histogram < 0:
            score -= 5

        # ボリンジャーバンドによるスコア調整
        if bollinger_bands.current_position == "below_lower":
            score += 12  # 下限突破は買いチャンス
        elif bollinger_bands.current_position == "above_upper":
            score -= 12  # 上限突破は売りチャンス
        elif bollinger_bands.current_position == "lower_half":
            score += 3  # 下半分は買い寄り
        elif bollinger_bands.current_position == "upper_half":
            score -= 3  # 上半分は売り寄り

        # ボラティリティによるリスク調整
        if volatility < 2:
            risk_level = "low"
            score += 5
        elif volatility < 5:
            risk_level = "medium"
        else:
            risk_level = "high"
            score -= 10

        # スコアを0-100にクリップ
        score = max(0, min(100, score))

        # 推奨アクションを決定
        if score >= 75:
            recommendation = "strong_buy"
            action = "強い買い"
        elif score >= 60:
            recommendation = "buy"
            action = "買い"
        elif score >= 40:
            recommendation = "hold"
            action = "様子見"
        else:
            recommendation = "sell"
            action = "売り"

        return score, recommendation, risk_level

    def generate_reasoning(
        self,
        trend: str,
        rsi: float,
        volatility: float,
        price_change_7d: float,
        recommendation: str,
        macd: MACDIndicator,
        bollinger_bands: BollingerBands
    ) -> str:
        """推奨理由を生成"""
        reasons = []

        # トレンド
        if trend == "bullish":
            reasons.append("上昇トレンド継続中")
        elif trend == "bearish":
            reasons.append("下降トレンド")
        else:
            reasons.append("横ばいトレンド")

        # RSI
        if rsi < 30:
            reasons.append("RSIは売られすぎ水準（買いチャンス）")
        elif rsi > 70:
            reasons.append("RSIは買われすぎ水準（調整の可能性）")
        else:
            reasons.append("RSIは適正水準")

        # MACD
        if macd.signal == "buy":
            reasons.append("MACDゴールデンクロス発生（強い買いシグナル）")
        elif macd.signal == "sell":
            reasons.append("MACDデッドクロス発生（売りシグナル）")
        elif macd.histogram > 0:
            reasons.append("MACD上昇モメンタム")
        elif macd.histogram < 0:
            reasons.append("MACD下降モメンタム")

        # ボリンジャーバンド
        if bollinger_bands.current_position == "below_lower":
            reasons.append("ボリンジャーバンド下限突破（反発期待）")
        elif bollinger_bands.current_position == "above_upper":
            reasons.append("ボリンジャーバンド上限突破（過熱感）")

        # ボラティリティ
        if volatility < 2:
            reasons.append("低ボラティリティで安定")
        elif volatility > 5:
            reasons.append("高ボラティリティで変動大")

        # 価格変動
        if price_change_7d > 10:
            reasons.append("直近7日で大幅上昇")
        elif price_change_7d < -10:
            reasons.append("直近7日で大幅下落")

        return "、".join(reasons)

    async def analyze_coin(self, symbol: str) -> InvestmentRecommendation:
        """個別通貨を分析"""
        # 現在価格を取得
        price_data = await crypto_service.get_price(symbol)
        if not price_data:
            raise ValueError(f"Price data not found for {symbol}")

        # 30日間のチャートデータを取得
        chart_data = await crypto_service.get_chart_data(symbol, 30)
        if not chart_data or len(chart_data.prices) < 7:
            raise ValueError(f"Insufficient chart data for {symbol}")

        prices = [p.price for p in chart_data.prices]

        # テクニカル指標を計算
        rsi = self.calculate_rsi(prices)
        volatility = self.calculate_volatility(prices)
        trend, trend_strength = self.calculate_trend(prices)
        macd = self.calculate_macd(prices)
        bollinger_bands = self.calculate_bollinger_bands(prices)

        # 価格変動率を計算
        if len(prices) >= 7:
            price_change_7d = ((prices[-1] - prices[-7]) / prices[-7]) * 100
        else:
            price_change_7d = 0

        price_change_30d = ((prices[-1] - prices[0]) / prices[0]) * 100

        # 推奨スコアを計算
        score, recommendation, risk_level = self.calculate_recommendation_score(
            rsi, trend, trend_strength, volatility, price_change_7d, price_change_30d, macd, bollinger_bands
        )

        # 推奨理由を生成
        reasoning = self.generate_reasoning(
            trend, rsi, volatility, price_change_7d, recommendation, macd, bollinger_bands
        )

        # テクニカル指標
        technical_indicators = TechnicalIndicators(
            rsi=rsi,
            volatility=volatility,
            trend=trend,
            trend_strength=trend_strength,
            price_change_7d=price_change_7d,
            price_change_30d=price_change_30d,
            macd=macd,
            bollinger_bands=bollinger_bands
        )

        return InvestmentRecommendation(
            symbol=symbol,
            name=chart_data.name,
            current_price=price_data.current_price,
            recommendation_score=score,
            recommendation=recommendation,
            risk_level=risk_level,
            technical_indicators=technical_indicators,
            reasoning=reasoning
        )

    async def analyze_top_coins(self, limit: int = 10) -> InvestmentAnalysisResponse:
        """トップ通貨を分析"""
        # 主要通貨のシンボル
        symbols = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "AVAX", "MATIC"]
        symbols = symbols[:limit]

        recommendations = []
        for symbol in symbols:
            try:
                recommendation = await self.analyze_coin(symbol)
                recommendations.append(recommendation)
            except Exception as e:
                print(f"Failed to analyze {symbol}: {e}")
                continue

        # スコアで降順ソート
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return InvestmentAnalysisResponse(
            recommendations=recommendations,
            total=len(recommendations)
        )


# グローバルインスタンス
analysis_service = AnalysisService()
