import { useQuery } from '@tanstack/react-query';
import { cryptoApi } from '../services/api';
import { CryptoPriceCard } from './CryptoPriceCard';

export function TopCryptos() {
  const { data, isLoading, error, isRefetching } = useQuery({
    queryKey: ['topCryptos'],
    queryFn: () => cryptoApi.getTopCoins(10),
    refetchInterval: 60000, // 1分ごとに自動更新
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-700 font-semibold">エラーが発生しました</p>
        <p className="text-red-600 text-sm mt-2">
          {error instanceof Error ? error.message : 'データの取得に失敗しました'}
        </p>
      </div>
    );
  }

  if (!data || data.coins.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <p className="text-gray-600">データがありません</p>
      </div>
    );
  }

  return (
    <div>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">
            時価総額トップ10
          </h2>
          <p className="text-gray-600 mt-1">
            取得: {data.total}通貨
          </p>
        </div>
        {isRefetching && (
          <div className="flex items-center text-blue-600 text-sm">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            更新中...
          </div>
        )}
      </div>

      {/* 価格カードグリッド */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.coins.map((crypto) => (
          <CryptoPriceCard key={crypto.symbol} crypto={crypto} />
        ))}
      </div>

      {/* フッター情報 */}
      <div className="mt-6 text-center text-sm text-gray-500">
        データは1分ごとに自動更新されます
      </div>
    </div>
  );
}
