import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { cryptoApi } from '../services/api';

interface CryptoChartProps {
  symbol: string;
  name?: string;
}

type TimeRange = {
  label: string;
  days: number;
};

const TIME_RANGES: TimeRange[] = [
  { label: '24時間', days: 1 },
  { label: '7日', days: 7 },
  { label: '30日', days: 30 },
  { label: '90日', days: 90 },
  { label: '1年', days: 365 },
];

export function CryptoChart({ symbol, name }: CryptoChartProps) {
  const [selectedDays, setSelectedDays] = useState(7);

  const { data, isLoading, error, isRefetching } = useQuery({
    queryKey: ['chartData', symbol, selectedDays],
    queryFn: () => cryptoApi.getChartData(symbol, selectedDays),
    refetchInterval: 300000, // 5分ごとに自動更新
  });

  // データをRechartsに適した形式に変換
  const chartData = data?.prices.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
      ...(selectedDays > 90 && { year: 'numeric' }),
    }),
    price: point.price,
    timestamp: point.timestamp,
  }));

  // Y軸の範囲を計算
  const prices = data?.prices.map((p) => p.price) || [];
  const minPrice = Math.min(...prices) * 0.98;
  const maxPrice = Math.max(...prices) * 1.02;

  // カスタムツールチップ
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm text-gray-600">
            {new Date(data.timestamp).toLocaleString('ja-JP')}
          </p>
          <p className="text-lg font-bold text-gray-900">
            ${data.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">チャート読み込み中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-semibold">チャートの読み込みに失敗しました</p>
          <p className="text-red-600 text-sm mt-2">
            {error instanceof Error ? error.message : '不明なエラーが発生しました'}
          </p>
        </div>
      </div>
    );
  }

  if (!data || !chartData || chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
          <p className="text-gray-600">チャートデータがありません</p>
        </div>
      </div>
    );
  }

  // 価格変動を計算
  const firstPrice = data.prices[0]?.price || 0;
  const lastPrice = data.prices[data.prices.length - 1]?.price || 0;
  const priceChange = lastPrice - firstPrice;
  const priceChangePercent = (priceChange / firstPrice) * 100;
  const isPositive = priceChange >= 0;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* ヘッダー */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-800">
            {name || data.name} ({data.symbol})
          </h3>
          <div className="flex items-baseline gap-3 mt-2">
            <span className="text-3xl font-bold text-gray-900">
              ${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span
              className={`text-lg font-semibold ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {isPositive ? '+' : ''}
              {priceChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>
        {isRefetching && (
          <div className="flex items-center text-blue-600 text-sm">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            更新中
          </div>
        )}
      </div>

      {/* 期間選択ボタン */}
      <div className="flex flex-wrap gap-2 mb-6">
        {TIME_RANGES.map((range) => (
          <button
            key={range.days}
            onClick={() => setSelectedDays(range.days)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedDays === range.days
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* チャート */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickMargin={10}
          />
          <YAxis
            domain={[minPrice, maxPrice]}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) =>
              `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
            }
            tickMargin={10}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            name="価格 (USD)"
            stroke={isPositive ? '#10b981' : '#ef4444'}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* フッター情報 */}
      <div className="mt-4 text-sm text-gray-500 text-center">
        データポイント: {data.total_points} | 自動更新: 5分ごと
      </div>
    </div>
  );
}
