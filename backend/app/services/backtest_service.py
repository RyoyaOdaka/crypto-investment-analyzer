from typing import List, Tuple
import statistics
from datetime import datetime, timedelta
from app.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestStrategy,
    BacktestTrade,
    BacktestMetrics
)
from app.services.crypto_service import crypto_service
from app.services.analysis_service import analysis_service


class BacktestService:
    """バックテストサービス"""

    def __init__(self):
        self.analysis = analysis_service

    async def run_backtest(self, request: BacktestRequest) -> BacktestResponse:
        """バックテストを実行"""
        # 過去データを取得
        chart_data = await crypto_service.get_chart_data(request.symbol, request.period_days)
        if not chart_data or len(chart_data.prices) < 30:
            raise ValueError(f"Insufficient data for backtesting {request.symbol}")

        prices = [p.price for p in chart_data.prices]
        timestamps = [p.timestamp for p in chart_data.prices]

        # バックテスト実行
        trades, equity_curve = self._simulate_trades(
            prices,
            timestamps,
            request.strategy
        )

        # パフォーマンス指標を計算
        metrics = self._calculate_metrics(
            trades,
            equity_curve,
            request.strategy.initial_capital
        )

        # 最終資金
        final_capital = equity_curve[-1]["value"] if equity_curve else request.strategy.initial_capital

        # 日時をdatetimeに変換
        start_date = datetime.fromtimestamp(timestamps[0] / 1000)
        end_date = datetime.fromtimestamp(timestamps[-1] / 1000)

        return BacktestResponse(
            symbol=request.symbol,
            name=chart_data.name,
            strategy=request.strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=request.strategy.initial_capital,
            final_capital=final_capital,
            trades=trades,
            metrics=metrics,
            equity_curve=equity_curve
        )

    def _simulate_trades(
        self,
        prices: List[float],
        timestamps: List[int],
        strategy: BacktestStrategy
    ) -> Tuple[List[BacktestTrade], List[dict]]:
        """取引をシミュレート"""
        trades = []
        equity_curve = []
        cash = strategy.initial_capital
        position = 0.0  # 保有数量
        position_entry_price = 0.0
        trade_id = 0

        # 各時点でシグナルを評価
        for i in range(30, len(prices)):  # 最初の30日は指標計算に必要
            price_window = prices[:i+1]
            current_price = prices[i]
            current_timestamp = timestamps[i]

            # テクニカル指標を計算
            rsi = self.analysis.calculate_rsi(price_window)
            macd = self.analysis.calculate_macd(price_window)
            bollinger = self.analysis.calculate_bollinger_bands(price_window)

            # 買いシグナル評価
            buy_signal = self._evaluate_buy_signal(strategy.buy_signal, rsi, macd, bollinger, current_price)

            # 売りシグナル評価
            sell_signal = self._evaluate_sell_signal(strategy.sell_signal, rsi, macd, bollinger, current_price)

            # ポジションなし & 買いシグナル → 買い
            if position == 0 and buy_signal and cash > 0:
                trade_amount = (cash * strategy.trade_size_percent / 100) / current_price
                trade_value = trade_amount * current_price

                if trade_value > 0:
                    trade_id += 1
                    trades.append(BacktestTrade(
                        trade_id=trade_id,
                        type="buy",
                        timestamp=datetime.fromtimestamp(current_timestamp / 1000),
                        price=current_price,
                        amount=trade_amount,
                        value=trade_value
                    ))

                    cash -= trade_value
                    position = trade_amount
                    position_entry_price = current_price

            # ポジションあり & 売りシグナル → 売り
            elif position > 0 and sell_signal:
                trade_value = position * current_price
                profit_loss = trade_value - (position * position_entry_price)
                profit_loss_percent = (profit_loss / (position * position_entry_price)) * 100

                trade_id += 1
                trades.append(BacktestTrade(
                    trade_id=trade_id,
                    type="sell",
                    timestamp=datetime.fromtimestamp(current_timestamp / 1000),
                    price=current_price,
                    amount=position,
                    value=trade_value,
                    profit_loss=profit_loss,
                    profit_loss_percent=profit_loss_percent
                ))

                cash += trade_value
                position = 0.0
                position_entry_price = 0.0

            # 資産曲線を記録
            total_value = cash + (position * current_price)
            equity_curve.append({
                "timestamp": current_timestamp,
                "value": total_value
            })

        # 最後にポジションを持っていたら清算
        if position > 0:
            final_price = prices[-1]
            final_timestamp = timestamps[-1]
            trade_value = position * final_price
            profit_loss = trade_value - (position * position_entry_price)
            profit_loss_percent = (profit_loss / (position * position_entry_price)) * 100

            trade_id += 1
            trades.append(BacktestTrade(
                trade_id=trade_id,
                type="sell",
                timestamp=datetime.fromtimestamp(final_timestamp / 1000),
                price=final_price,
                amount=position,
                value=trade_value,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent
            ))

        return trades, equity_curve

    def _evaluate_buy_signal(self, signal: str, rsi: float, macd, bollinger, price: float) -> bool:
        """買いシグナルを評価"""
        if signal == "rsi_oversold":
            return rsi < 30
        elif signal == "macd_golden_cross":
            return macd.signal == "buy"
        elif signal == "bb_lower_breach":
            return bollinger.current_position == "below_lower"
        return False

    def _evaluate_sell_signal(self, signal: str, rsi: float, macd, bollinger, price: float) -> bool:
        """売りシグナルを評価"""
        if signal == "rsi_overbought":
            return rsi > 70
        elif signal == "macd_dead_cross":
            return macd.signal == "sell"
        elif signal == "bb_upper_breach":
            return bollinger.current_position == "above_upper"
        return False

    def _calculate_metrics(
        self,
        trades: List[BacktestTrade],
        equity_curve: List[dict],
        initial_capital: float
    ) -> BacktestMetrics:
        """パフォーマンス指標を計算"""
        if not trades:
            return BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_return=0.0,
                total_return_percent=0.0,
                max_drawdown=0.0,
                sharpe_ratio=None,
                avg_profit_per_trade=0.0,
                avg_profit_per_winning_trade=0.0,
                avg_loss_per_losing_trade=0.0
            )

        # 売り取引のみを抽出（利益計算のため）
        sell_trades = [t for t in trades if t.type == "sell" and t.profit_loss is not None]

        if not sell_trades:
            return BacktestMetrics(
                total_trades=len(trades),
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_return=0.0,
                total_return_percent=0.0,
                max_drawdown=0.0,
                sharpe_ratio=None,
                avg_profit_per_trade=0.0,
                avg_profit_per_winning_trade=0.0,
                avg_loss_per_losing_trade=0.0
            )

        # 勝ち・負けトレード
        winning_trades = [t for t in sell_trades if t.profit_loss > 0]
        losing_trades = [t for t in sell_trades if t.profit_loss <= 0]

        total_trades = len(sell_trades)
        num_winning = len(winning_trades)
        num_losing = len(losing_trades)
        win_rate = (num_winning / total_trades * 100) if total_trades > 0 else 0.0

        # トータルリターン
        total_return = sum(t.profit_loss for t in sell_trades)
        total_return_percent = (total_return / initial_capital) * 100

        # 平均利益・損失
        avg_profit_per_trade = total_return / total_trades if total_trades > 0 else 0.0
        avg_profit_per_winning = (
            sum(t.profit_loss for t in winning_trades) / num_winning
            if num_winning > 0 else 0.0
        )
        avg_loss_per_losing = (
            sum(t.profit_loss for t in losing_trades) / num_losing
            if num_losing > 0 else 0.0
        )

        # 最大ドローダウン
        max_drawdown = self._calculate_max_drawdown(equity_curve)

        # シャープレシオ
        sharpe_ratio = self._calculate_sharpe_ratio(sell_trades) if len(sell_trades) > 1 else None

        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=num_winning,
            losing_trades=num_losing,
            win_rate=win_rate,
            total_return=total_return,
            total_return_percent=total_return_percent,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            avg_profit_per_trade=avg_profit_per_trade,
            avg_profit_per_winning_trade=avg_profit_per_winning,
            avg_loss_per_losing_trade=avg_loss_per_losing
        )

    def _calculate_max_drawdown(self, equity_curve: List[dict]) -> float:
        """最大ドローダウンを計算"""
        if not equity_curve:
            return 0.0

        peak = equity_curve[0]["value"]
        max_dd = 0.0

        for point in equity_curve:
            value = point["value"]
            if value > peak:
                peak = value
            drawdown = ((value - peak) / peak) * 100
            if drawdown < max_dd:
                max_dd = drawdown

        return max_dd

    def _calculate_sharpe_ratio(self, sell_trades: List[BacktestTrade]) -> float:
        """シャープレシオを計算"""
        if len(sell_trades) < 2:
            return 0.0

        returns = [t.profit_loss_percent for t in sell_trades if t.profit_loss_percent is not None]

        if not returns:
            return 0.0

        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 1.0

        # リスクフリーレートは0と仮定
        sharpe = avg_return / std_return if std_return > 0 else 0.0

        return sharpe


# グローバルインスタンス
backtest_service = BacktestService()
