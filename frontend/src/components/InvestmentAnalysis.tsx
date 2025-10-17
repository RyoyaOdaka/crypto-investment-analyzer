import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '../services/api';

export function InvestmentAnalysis() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['investmentRecommendations'],
    queryFn: () => analysisApi.getRecommendations(10),
    refetchInterval: 300000, // 5分ごとに更新
  });

  const getRecommendationBadge = (recommendation: string) => {
    const badges = {
      strong_buy: { color: 'bg-green-600', text: '強い買い', icon: '🚀' },
      buy: { color: 'bg-green-500', text: '買い', icon: '📈' },
      hold: { color: 'bg-yellow-500', text: '様子見', icon: '⏸️' },
      sell: { color: 'bg-red-500', text: '売り', icon: '📉' },
    };
    return badges[recommendation as keyof typeof badges] || badges.hold;
  };

  const getRiskBadge = (risk: string) => {
    const badges = {
      low: { color: 'bg-blue-100 text-blue-800', text: '低リスク' },
      medium: { color: 'bg-yellow-100 text-yellow-800', text: '中リスク' },
      high: { color: 'bg-red-100 text-red-800', text: '高リスク' },
    };
    return badges[risk as keyof typeof badges] || badges.medium;
  };

  const getTrendIcon = (trend: string) => {
    const icons = {
      bullish: { icon: '📈', color: 'text-green-600', text: '上昇' },
      bearish: { icon: '📉', color: 'text-red-600', text: '下降' },
      neutral: { icon: '➡️', color: 'text-gray-600', text: '横ばい' },
    };
    return icons[trend as keyof typeof icons] || icons.neutral;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">分析中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">分析に失敗しました</p>
      </div>
    );
  }

  if (!data || data.recommendations.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">分析データがありません</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
        <h3 className="text-2xl font-bold mb-2">🎯 AI投資推奨</h3>
        <p className="text-indigo-100">
          テクニカル指標に基づく推奨スコア順にランキング表示
        </p>
      </div>

      {/* 推奨リスト */}
      <div className="grid grid-cols-1 gap-4">
        {data.recommendations.map((rec, index) => {
          const recBadge = getRecommendationBadge(rec.recommendation);
          const riskBadge = getRiskBadge(rec.risk_level);
          const trendIcon = getTrendIcon(rec.technical_indicators.trend);
          const scoreColor = rec.recommendation_score >= 70 ? 'text-green-600' :
                            rec.recommendation_score >= 50 ? 'text-yellow-600' : 'text-red-600';

          return (
            <div key={rec.symbol} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              {/* ヘッダー行 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-gray-100 rounded-full w-10 h-10 flex items-center justify-center font-bold text-gray-700">
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="text-xl font-bold text-gray-800">
                      {rec.name} ({rec.symbol})
                    </h4>
                    <p className="text-2xl font-bold text-gray-900">
                      ${rec.current_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-4xl font-bold ${scoreColor}`}>
                    {rec.recommendation_score.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">推奨スコア</div>
                </div>
              </div>

              {/* バッジ */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className={`${recBadge.color} text-white px-4 py-1 rounded-full text-sm font-semibold`}>
                  {recBadge.icon} {recBadge.text}
                </span>
                <span className={`${riskBadge.color} px-3 py-1 rounded-full text-xs font-semibold`}>
                  {riskBadge.text}
                </span>
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-semibold">
                  {trendIcon.icon} {trendIcon.text}トレンド
                </span>
              </div>

              {/* テクニカル指標 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 text-sm">
                {rec.technical_indicators.rsi !== null && (
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-gray-500 text-xs">RSI</div>
                    <div className={`font-bold ${
                      rec.technical_indicators.rsi < 30 ? 'text-green-600' :
                      rec.technical_indicators.rsi > 70 ? 'text-red-600' : 'text-gray-700'
                    }`}>
                      {rec.technical_indicators.rsi.toFixed(1)}
                    </div>
                  </div>
                )}
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-xs">ボラティリティ</div>
                  <div className="font-bold text-gray-700">
                    {rec.technical_indicators.volatility.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-xs">7日変動</div>
                  <div className={`font-bold ${
                    rec.technical_indicators.price_change_7d >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {rec.technical_indicators.price_change_7d >= 0 ? '+' : ''}
                    {rec.technical_indicators.price_change_7d.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-xs">30日変動</div>
                  <div className={`font-bold ${
                    rec.technical_indicators.price_change_30d >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {rec.technical_indicators.price_change_30d >= 0 ? '+' : ''}
                    {rec.technical_indicators.price_change_30d.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* 高度なテクニカル指標 */}
              {(rec.technical_indicators.macd || rec.technical_indicators.bollinger_bands) && (
                <div className="mb-4">
                  <div className="text-xs font-semibold text-gray-600 mb-2">📊 高度なテクニカル指標</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {/* MACD */}
                    {rec.technical_indicators.macd && (
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-3 rounded border border-blue-200">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-xs font-semibold text-indigo-700">MACD</div>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                            rec.technical_indicators.macd.signal === 'buy' ? 'bg-green-500 text-white' :
                            rec.technical_indicators.macd.signal === 'sell' ? 'bg-red-500 text-white' :
                            'bg-gray-400 text-white'
                          }`}>
                            {rec.technical_indicators.macd.signal === 'buy' ? '買い' :
                             rec.technical_indicators.macd.signal === 'sell' ? '売り' : '中立'}
                          </span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">MACDライン:</span>
                            <span className="font-bold text-gray-800">{rec.technical_indicators.macd.macd_line.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">シグナル:</span>
                            <span className="font-bold text-gray-800">{rec.technical_indicators.macd.signal_line.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">ヒストグラム:</span>
                            <span className={`font-bold ${
                              rec.technical_indicators.macd.histogram >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {rec.technical_indicators.macd.histogram >= 0 ? '+' : ''}
                              {rec.technical_indicators.macd.histogram.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* ボリンジャーバンド */}
                    {rec.technical_indicators.bollinger_bands && (
                      <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-3 rounded border border-purple-200">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-xs font-semibold text-purple-700">ボリンジャーバンド</div>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                            rec.technical_indicators.bollinger_bands.current_position === 'below_lower' ? 'bg-green-500 text-white' :
                            rec.technical_indicators.bollinger_bands.current_position === 'above_upper' ? 'bg-red-500 text-white' :
                            rec.technical_indicators.bollinger_bands.current_position === 'lower_half' ? 'bg-blue-400 text-white' :
                            'bg-yellow-400 text-white'
                          }`}>
                            {rec.technical_indicators.bollinger_bands.current_position === 'below_lower' ? '下限下' :
                             rec.technical_indicators.bollinger_bands.current_position === 'above_upper' ? '上限上' :
                             rec.technical_indicators.bollinger_bands.current_position === 'lower_half' ? '下半分' : '上半分'}
                          </span>
                        </div>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-600">上限バンド:</span>
                            <span className="font-bold text-red-600">${rec.technical_indicators.bollinger_bands.upper_band.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">中央線:</span>
                            <span className="font-bold text-gray-800">${rec.technical_indicators.bollinger_bands.middle_band.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">下限バンド:</span>
                            <span className="font-bold text-green-600">${rec.technical_indicators.bollinger_bands.lower_band.toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 推奨理由 */}
              <div className="bg-indigo-50 border-l-4 border-indigo-500 p-3 rounded">
                <div className="text-xs text-indigo-700 font-semibold mb-1">💡 分析理由</div>
                <div className="text-sm text-indigo-900">{rec.reasoning}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* フッター */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        <p className="font-semibold">⚠️ 免責事項</p>
        <p className="mt-1">
          この推奨はテクニカル指標に基づく参考情報です。投資判断は自己責任で行ってください。
          市場は予測不可能であり、過去のパフォーマンスは将来の結果を保証するものではありません。
        </p>
      </div>
    </div>
  );
}
