import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { virtualPortfolioApi, VirtualPortfolioSummary } from '../services/api';

export function TradingSimulator() {
  const queryClient = useQueryClient();
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  const [tradeSymbol, setTradeSymbol] = useState('BTC');
  const [tradeAmount, setTradeAmount] = useState<string>('');
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [newPortfolioBalance, setNewPortfolioBalance] = useState('10000');

  // ポートフォリオリストを取得
  const { data: portfolios } = useQuery({
    queryKey: ['virtualPortfolios'],
    queryFn: () => virtualPortfolioApi.getPortfolios(),
  });

  // 選択されたポートフォリオのサマリーを取得
  const { data: summary, refetch: refetchSummary } = useQuery({
    queryKey: ['virtualPortfolioSummary', selectedPortfolioId],
    queryFn: () => virtualPortfolioApi.getPortfolioSummary(selectedPortfolioId!),
    enabled: selectedPortfolioId !== null,
    refetchInterval: 10000, // 10秒ごとに更新
  });

  // 取引履歴を取得
  const { data: transactions } = useQuery({
    queryKey: ['virtualTransactions', selectedPortfolioId],
    queryFn: () => virtualPortfolioApi.getTransactions(selectedPortfolioId!, 20),
    enabled: selectedPortfolioId !== null,
  });

  // ポートフォリオ作成mutation
  const createPortfolioMutation = useMutation({
    mutationFn: ({ name, balance }: { name: string; balance: number }) =>
      virtualPortfolioApi.createPortfolio(name, balance),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['virtualPortfolios'] });
      setSelectedPortfolioId(data.id);
      setShowCreateForm(false);
      setNewPortfolioName('');
      setNewPortfolioBalance('10000');
    },
  });

  // 取引execution mutation
  const tradeMutation = useMutation({
    mutationFn: virtualPortfolioApi.executeTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['virtualPortfolioSummary', selectedPortfolioId] });
      queryClient.invalidateQueries({ queryKey: ['virtualTransactions', selectedPortfolioId] });
      setTradeAmount('');
    },
  });

  // 初回ロード時に最初のポートフォリオを選択
  useEffect(() => {
    if (portfolios && portfolios.length > 0 && selectedPortfolioId === null) {
      setSelectedPortfolioId(portfolios[0].id);
    }
  }, [portfolios, selectedPortfolioId]);

  const handleCreatePortfolio = () => {
    const balance = parseFloat(newPortfolioBalance);
    if (!newPortfolioName || isNaN(balance) || balance <= 0) {
      alert('有効なポートフォリオ名と初期資金を入力してください');
      return;
    }
    createPortfolioMutation.mutate({ name: newPortfolioName, balance });
  };

  const handleTrade = () => {
    if (!selectedPortfolioId) {
      alert('ポートフォリオを選択してください');
      return;
    }

    const amount = parseFloat(tradeAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('有効な数量を入力してください');
      return;
    }

    tradeMutation.mutate({
      portfolio_id: selectedPortfolioId,
      symbol: tradeSymbol,
      transaction_type: tradeType,
      amount,
    });
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-lg shadow-lg p-6 text-white">
        <h3 className="text-2xl font-bold mb-2">💰 取引シミュレーター</h3>
        <p className="text-green-100">
          仮想資金でリスクなく取引の練習ができます
        </p>
      </div>

      {/* ポートフォリオ選択 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-bold text-gray-800">ポートフォリオ</h4>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            {showCreateForm ? 'キャンセル' : '+ 新規作成'}
          </button>
        </div>

        {/* 新規作成フォーム */}
        {showCreateForm && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">ポートフォリオ名</label>
                <input
                  type="text"
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  placeholder="例: 練習用ポートフォリオ"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">初期資金 (USD)</label>
                <input
                  type="number"
                  value={newPortfolioBalance}
                  onChange={(e) => setNewPortfolioBalance(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            <button
              onClick={handleCreatePortfolio}
              disabled={createPortfolioMutation.isPending}
              className="mt-4 w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-400"
            >
              {createPortfolioMutation.isPending ? '作成中...' : '作成'}
            </button>
          </div>
        )}

        {/* ポートフォリオ選択 */}
        {portfolios && portfolios.length > 0 && (
          <select
            value={selectedPortfolioId || ''}
            onChange={(e) => setSelectedPortfolioId(Number(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} - ${p.cash_balance.toFixed(2)}
              </option>
            ))}
          </select>
        )}

        {!portfolios || portfolios.length === 0 && !showCreateForm && (
          <div className="text-center py-4 text-gray-500">
            ポートフォリオがありません。新規作成してください。
          </div>
        )}
      </div>

      {/* ポートフォリオサマリー */}
      {summary && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h4 className="text-lg font-bold text-gray-800 mb-4">ポートフォリオサマリー</h4>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
              <div className="text-xs text-blue-700 font-semibold">現金残高</div>
              <div className="text-2xl font-bold text-blue-600">
                ${summary.portfolio.cash_balance.toFixed(2)}
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
              <div className="text-xs text-purple-700 font-semibold">保有資産</div>
              <div className="text-2xl font-bold text-purple-600">
                ${summary.total_holdings_value.toFixed(2)}
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
              <div className="text-xs text-green-700 font-semibold">総資産</div>
              <div className="text-2xl font-bold text-green-600">
                ${summary.total_value.toFixed(2)}
              </div>
            </div>

            <div className={`bg-gradient-to-br p-4 rounded-lg ${
              summary.total_profit_loss >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'
            }`}>
              <div className={`text-xs font-semibold ${
                summary.total_profit_loss >= 0 ? 'text-green-700' : 'text-red-700'
              }`}>
                総損益
              </div>
              <div className={`text-2xl font-bold ${
                summary.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {summary.total_profit_loss >= 0 ? '+' : ''}${summary.total_profit_loss.toFixed(2)}
              </div>
              <div className={`text-xs ${
                summary.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                ({summary.total_profit_loss_percentage.toFixed(2)}%)
              </div>
            </div>
          </div>

          {/* 保有資産 */}
          {summary.holdings.length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-700 mb-2">保有資産</h5>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">通貨</th>
                      <th className="px-4 py-2 text-right">数量</th>
                      <th className="px-4 py-2 text-right">平均取得単価</th>
                      <th className="px-4 py-2 text-right">現在価格</th>
                      <th className="px-4 py-2 text-right">評価額</th>
                      <th className="px-4 py-2 text-right">損益</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.holdings.map((holding) => (
                      <tr key={holding.id} className="border-t border-gray-200">
                        <td className="px-4 py-2 font-semibold">{holding.symbol}</td>
                        <td className="px-4 py-2 text-right">{holding.amount.toFixed(8)}</td>
                        <td className="px-4 py-2 text-right">${holding.avg_purchase_price.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right">${holding.current_price.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right font-semibold">${holding.current_value.toFixed(2)}</td>
                        <td className={`px-4 py-2 text-right font-semibold ${
                          holding.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {holding.profit_loss >= 0 ? '+' : ''}${holding.profit_loss.toFixed(2)}
                          <br />
                          <span className="text-xs">
                            ({holding.profit_loss_percentage.toFixed(2)}%)
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 取引フォーム */}
      {selectedPortfolioId && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h4 className="text-lg font-bold text-gray-800 mb-4">取引</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">取引タイプ</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setTradeType('buy')}
                  className={`flex-1 py-2 rounded-lg font-semibold transition-colors ${
                    tradeType === 'buy'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  買い
                </button>
                <button
                  onClick={() => setTradeType('sell')}
                  className={`flex-1 py-2 rounded-lg font-semibold transition-colors ${
                    tradeType === 'sell'
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  売り
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">通貨</label>
              <select
                value={tradeSymbol}
                onChange={(e) => setTradeSymbol(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="BTC">Bitcoin (BTC)</option>
                <option value="ETH">Ethereum (ETH)</option>
                <option value="BNB">Binance Coin (BNB)</option>
                <option value="XRP">Ripple (XRP)</option>
                <option value="ADA">Cardano (ADA)</option>
                <option value="SOL">Solana (SOL)</option>
                <option value="DOT">Polkadot (DOT)</option>
                <option value="DOGE">Dogecoin (DOGE)</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">数量</label>
              <input
                type="number"
                value={tradeAmount}
                onChange={(e) => setTradeAmount(e.target.value)}
                step="0.00000001"
                placeholder="例: 0.05"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <button
            onClick={handleTrade}
            disabled={tradeMutation.isPending}
            className={`w-full py-3 rounded-lg font-semibold text-white transition-colors ${
              tradeType === 'buy'
                ? 'bg-green-500 hover:bg-green-600 disabled:bg-gray-400'
                : 'bg-red-500 hover:bg-red-600 disabled:bg-gray-400'
            }`}
          >
            {tradeMutation.isPending ? '処理中...' : tradeType === 'buy' ? '買い注文' : '売り注文'}
          </button>

          {tradeMutation.isSuccess && tradeMutation.data && (
            <div className={`mt-4 p-4 rounded-lg ${
              tradeMutation.data.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            }`}>
              <p className={tradeMutation.data.success ? 'text-green-700' : 'text-red-700'}>
                {tradeMutation.data.message}
              </p>
            </div>
          )}

          {tradeMutation.isError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">エラーが発生しました</p>
            </div>
          )}
        </div>
      )}

      {/* 取引履歴 */}
      {transactions && transactions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h4 className="text-lg font-bold text-gray-800 mb-4">取引履歴</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">日時</th>
                  <th className="px-4 py-2 text-left">タイプ</th>
                  <th className="px-4 py-2 text-left">通貨</th>
                  <th className="px-4 py-2 text-right">数量</th>
                  <th className="px-4 py-2 text-right">価格</th>
                  <th className="px-4 py-2 text-right">金額</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => (
                  <tr key={tx.id} className="border-t border-gray-200">
                    <td className="px-4 py-2">
                      {new Date(tx.created_at).toLocaleString('ja-JP')}
                    </td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        tx.transaction_type === 'buy' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {tx.transaction_type === 'buy' ? '買い' : '売り'}
                      </span>
                    </td>
                    <td className="px-4 py-2 font-semibold">{tx.symbol}</td>
                    <td className="px-4 py-2 text-right">{tx.amount.toFixed(8)}</td>
                    <td className="px-4 py-2 text-right">${tx.price.toLocaleString()}</td>
                    <td className="px-4 py-2 text-right font-semibold">${tx.total_value.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
