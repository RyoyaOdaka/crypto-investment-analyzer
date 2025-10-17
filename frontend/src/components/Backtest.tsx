import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { backtestApi, BacktestResponse } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function Backtest() {
  const [symbol, setSymbol] = useState('BTC');
  const [buySignal, setBuySignal] = useState('rsi_oversold');
  const [sellSignal, setSellSignal] = useState('rsi_overbought');
  const [initialCapital, setInitialCapital] = useState(10000);
  const [tradeSizePercent, setTradeSizePercent] = useState(100);
  const [periodDays, setPeriodDays] = useState(90);
  const [results, setResults] = useState<BacktestResponse | null>(null);

  const { data: strategies } = useQuery({
    queryKey: ['backtestStrategies'],
    queryFn: () => backtestApi.getStrategies(),
  });

  const mutation = useMutation({
    mutationFn: backtestApi.runBacktest,
    onSuccess: (data) => {
      setResults(data);
    },
  });

  const handleRunBacktest = () => {
    mutation.mutate({
      symbol,
      strategy: {
        name: 'Custom Strategy',
        buy_signal: buySignal,
        sell_signal: sellSignal,
        initial_capital: initialCapital,
        trade_size_percent: tradeSizePercent,
      },
      period_days: periodDays,
    });
  };

  // 資産曲線データをチャート用に変換
  const equityChartData = results?.equity_curve.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString(),
    value: point.value.toFixed(2),
  })) || [];

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg shadow-lg p-6 text-white">
        <h3 className="text-2xl font-bold mb-2">📊 バックテスト</h3>
        <p className="text-purple-100">
          過去データで戦略をテストしてパフォーマンスを検証
        </p>
      </div>

      {/* 設定フォーム */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h4 className="text-lg font-bold text-gray-800 mb-4">戦略設定</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 通貨選択 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">通貨</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="BTC">Bitcoin (BTC)</option>
              <option value="ETH">Ethereum (ETH)</option>
              <option value="BNB">Binance Coin (BNB)</option>
              <option value="XRP">Ripple (XRP)</option>
              <option value="ADA">Cardano (ADA)</option>
            </select>
          </div>

          {/* 期間 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">バックテスト期間</label>
            <select
              value={periodDays}
              onChange={(e) => setPeriodDays(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value={30}>30日</option>
              <option value={90}>90日</option>
              <option value={180}>180日</option>
              <option value={365}>1年</option>
            </select>
          </div>

          {/* 買いシグナル */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">買いシグナル</label>
            <select
              value={buySignal}
              onChange={(e) => setBuySignal(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {strategies?.buy_signals.map((signal: any) => (
                <option key={signal.value} value={signal.value}>{signal.label}</option>
              ))}
            </select>
          </div>

          {/* 売りシグナル */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">売りシグナル</label>
            <select
              value={sellSignal}
              onChange={(e) => setSellSignal(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {strategies?.sell_signals.map((signal: any) => (
                <option key={signal.value} value={signal.value}>{signal.label}</option>
              ))}
            </select>
          </div>

          {/* 初期資金 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">初期資金 (USD)</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* 取引サイズ */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">取引サイズ (%)</label>
            <input
              type="number"
              value={tradeSizePercent}
              onChange={(e) => setTradeSizePercent(Number(e.target.value))}
              min="1"
              max="100"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        {/* 実行ボタン */}
        <div className="mt-6">
          <button
            onClick={handleRunBacktest}
            disabled={mutation.isPending}
            className={`w-full px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
              mutation.isPending
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700'
            }`}
          >
            {mutation.isPending ? 'バックテスト実行中...' : 'バックテスト実行'}
          </button>
        </div>

        {mutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            エラーが発生しました。もう一度お試しください。
          </div>
        )}
      </div>

      {/* 結果表示 */}
      {results && (
        <div className="space-y-6">
          {/* パフォーマンス指標 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="text-lg font-bold text-gray-800 mb-4">パフォーマンス指標</h4>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                <div className="text-xs text-green-700 font-semibold">総リターン</div>
                <div className={`text-2xl font-bold ${
                  results.metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {results.metrics.total_return >= 0 ? '+' : ''}
                  ${results.metrics.total_return.toFixed(2)}
                </div>
                <div className={`text-sm ${
                  results.metrics.total_return_percent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {results.metrics.total_return_percent.toFixed(2)}%
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                <div className="text-xs text-blue-700 font-semibold">勝率</div>
                <div className="text-2xl font-bold text-blue-600">
                  {results.metrics.win_rate.toFixed(1)}%
                </div>
                <div className="text-xs text-blue-600">
                  {results.metrics.winning_trades}勝 / {results.metrics.losing_trades}敗
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                <div className="text-xs text-purple-700 font-semibold">シャープレシオ</div>
                <div className="text-2xl font-bold text-purple-600">
                  {results.metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
                </div>
              </div>

              <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg">
                <div className="text-xs text-red-700 font-semibold">最大ドローダウン</div>
                <div className="text-2xl font-bold text-red-600">
                  {results.metrics.max_drawdown.toFixed(2)}%
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">総取引数</div>
                <div className="font-bold text-gray-800">{results.metrics.total_trades}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">平均利益/取引</div>
                <div className="font-bold text-gray-800">${results.metrics.avg_profit_per_trade.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-gray-500">初期→最終資金</div>
                <div className="font-bold text-gray-800">
                  ${results.initial_capital.toFixed(0)} → ${results.final_capital.toFixed(0)}
                </div>
              </div>
            </div>
          </div>

          {/* 資産曲線チャート */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="text-lg font-bold text-gray-800 mb-4">資産曲線</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={equityChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2} name="資産価値 ($)" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 取引履歴 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h4 className="text-lg font-bold text-gray-800 mb-4">取引履歴 ({results.trades.length}件)</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">ID</th>
                    <th className="px-4 py-2 text-left">タイプ</th>
                    <th className="px-4 py-2 text-left">日時</th>
                    <th className="px-4 py-2 text-right">価格</th>
                    <th className="px-4 py-2 text-right">数量</th>
                    <th className="px-4 py-2 text-right">金額</th>
                    <th className="px-4 py-2 text-right">損益</th>
                  </tr>
                </thead>
                <tbody>
                  {results.trades.map((trade) => (
                    <tr key={trade.trade_id} className="border-t border-gray-200">
                      <td className="px-4 py-2">{trade.trade_id}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          trade.type === 'buy' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {trade.type === 'buy' ? '買い' : '売り'}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        {new Date(trade.timestamp).toLocaleDateString('ja-JP')}
                      </td>
                      <td className="px-4 py-2 text-right">${trade.price.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                      <td className="px-4 py-2 text-right">{trade.amount.toFixed(8)}</td>
                      <td className="px-4 py-2 text-right">${trade.value.toFixed(2)}</td>
                      <td className="px-4 py-2 text-right">
                        {trade.profit_loss !== undefined && trade.profit_loss !== null ? (
                          <span className={trade.profit_loss >= 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                            {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                            <br />
                            <span className="text-xs">
                              ({trade.profit_loss_percent?.toFixed(2)}%)
                            </span>
                          </span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
