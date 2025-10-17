import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioApi, PortfolioCreate } from '../services/api';

export function Portfolio() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<PortfolioCreate>({
    symbol: 'BTC',
    name: 'Bitcoin',
    amount: 0,
    purchase_price: 0,
    purchase_date: new Date().toISOString().slice(0, 16),
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioApi.getPortfolios,
    refetchInterval: 60000,
  });

  const createMutation = useMutation({
    mutationFn: portfolioApi.createPortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] });
      setShowForm(false);
      setFormData({
        symbol: 'BTC',
        name: 'Bitcoin',
        amount: 0,
        purchase_price: 0,
        purchase_date: new Date().toISOString().slice(0, 16),
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: portfolioApi.deletePortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700">エラーが発生しました</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* サマリーカード */}
      {data && data.portfolios.length > 0 && (
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
          <h3 className="text-xl font-semibold mb-4">ポートフォリオサマリー</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-purple-100 text-sm">総評価額</p>
              <p className="text-3xl font-bold">{formatCurrency(data.total_value)}</p>
            </div>
            <div>
              <p className="text-purple-100 text-sm">総損益</p>
              <p className={`text-3xl font-bold ${data.total_profit_loss >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                {data.total_profit_loss >= 0 ? '+' : ''}{formatCurrency(data.total_profit_loss)}
              </p>
            </div>
            <div>
              <p className="text-purple-100 text-sm">損益率</p>
              <p className={`text-3xl font-bold ${data.total_profit_loss_percentage >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                {data.total_profit_loss_percentage >= 0 ? '+' : ''}{data.total_profit_loss_percentage.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 追加ボタン */}
      <div className="flex justify-between items-center">
        <h3 className="text-2xl font-bold text-gray-800">保有資産</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {showForm ? '閉じる' : '+ 追加'}
        </button>
      </div>

      {/* 追加フォーム */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">通貨シンボル</label>
              <input
                type="text"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">通貨名</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">数量</label>
              <input
                type="number"
                step="any"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">購入価格 (USD)</label>
              <input
                type="number"
                step="any"
                value={formData.purchase_price}
                onChange={(e) => setFormData({ ...formData, purchase_price: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">購入日時</label>
              <input
                type="datetime-local"
                value={formData.purchase_date}
                onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">メモ（オプション）</label>
              <input
                type="text"
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
          >
            {createMutation.isPending ? '追加中...' : '追加'}
          </button>
        </form>
      )}

      {/* ポートフォリオリスト */}
      {data && data.portfolios.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {data.portfolios.map((portfolio) => {
            const isProfit = portfolio.profit_loss >= 0;
            return (
              <div key={portfolio.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-bold text-gray-800">
                      {portfolio.name} ({portfolio.symbol})
                    </h4>
                    <p className="text-sm text-gray-500">保有数量: {portfolio.amount}</p>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(portfolio.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    削除
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">購入価格</p>
                    <p className="font-semibold">{formatCurrency(portfolio.purchase_price)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">現在価格</p>
                    <p className="font-semibold">{formatCurrency(portfolio.current_price)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">評価額</p>
                    <p className="font-semibold text-lg">{formatCurrency(portfolio.current_value)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">損益</p>
                    <p className={`font-bold text-lg ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                      {isProfit ? '+' : ''}{formatCurrency(portfolio.profit_loss)}
                      <span className="text-sm ml-1">
                        ({isProfit ? '+' : ''}{portfolio.profit_loss_percentage.toFixed(2)}%)
                      </span>
                    </p>
                  </div>
                </div>
                {portfolio.notes && (
                  <p className="mt-3 text-sm text-gray-600 italic">メモ: {portfolio.notes}</p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-600 mb-4">まだポートフォリオが登録されていません</p>
          <button
            onClick={() => setShowForm(true)}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            最初の資産を追加
          </button>
        </div>
      )}
    </div>
  );
}
