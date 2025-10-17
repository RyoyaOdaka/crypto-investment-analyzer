import { CryptoPrice } from '../services/api';

interface CryptoPriceCardProps {
  crypto: CryptoPrice;
}

export function CryptoPriceCard({ crypto }: CryptoPriceCardProps) {
  const priceChange = crypto.price_change_percentage_24h || 0;
  const isPositive = priceChange >= 0;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatLargeNumber = (num: number) => {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toFixed(2)}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-2xl font-bold text-gray-800">{crypto.symbol}</h3>
          <p className="text-sm text-gray-500">{crypto.name}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
          isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {isPositive ? '↑' : '↓'} {Math.abs(priceChange).toFixed(2)}%
        </div>
      </div>

      {/* 現在価格 */}
      <div className="mb-4">
        <div className="text-3xl font-bold text-gray-900">
          {formatPrice(crypto.current_price)}
        </div>
        {crypto.price_change_24h && (
          <div className={`text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? '+' : ''}{formatPrice(crypto.price_change_24h)} (24h)
          </div>
        )}
      </div>

      {/* 統計情報 */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        {crypto.high_24h && (
          <div>
            <div className="text-gray-500">24h 最高</div>
            <div className="font-semibold text-gray-700">
              {formatPrice(crypto.high_24h)}
            </div>
          </div>
        )}
        {crypto.low_24h && (
          <div>
            <div className="text-gray-500">24h 最低</div>
            <div className="font-semibold text-gray-700">
              {formatPrice(crypto.low_24h)}
            </div>
          </div>
        )}
        {crypto.market_cap && (
          <div>
            <div className="text-gray-500">時価総額</div>
            <div className="font-semibold text-gray-700">
              {formatLargeNumber(crypto.market_cap)}
            </div>
          </div>
        )}
        {crypto.total_volume && (
          <div>
            <div className="text-gray-500">24h 取引量</div>
            <div className="font-semibold text-gray-700">
              {formatLargeNumber(crypto.total_volume)}
            </div>
          </div>
        )}
      </div>

      {/* 最終更新時刻 */}
      <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-400">
        更新: {new Date(crypto.last_updated).toLocaleString('ja-JP')}
      </div>
    </div>
  );
}
