import { useState, useEffect } from 'react'
import { TopCryptos } from './components/TopCryptos'
import { CryptoChart } from './components/CryptoChart'
import { Portfolio } from './components/Portfolio'
import { InvestmentAnalysis } from './components/InvestmentAnalysis'
import { Backtest } from './components/Backtest'
import { TradingSimulator } from './components/TradingSimulator'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Checking...')

  useEffect(() => {
    // バックエンドAPIのヘルスチェック
    fetch('/api/v1/../health')
      .then(res => res.json())
      .then(data => setApiStatus(data.status || 'connected'))
      .catch(() => setApiStatus('disconnected'))
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* ヘッダー */}
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-3">
            Crypto Investment Analyzer
          </h1>
          <p className="text-xl text-gray-600 mb-4">
            仮想通貨投資分析アプリ
          </p>
          <div className="inline-flex items-center px-4 py-2 bg-white rounded-full shadow-sm">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              apiStatus === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-700">
              API Status: <span className={apiStatus === 'healthy' ? 'text-green-600 font-semibold' : 'text-red-600'}>
                {apiStatus}
              </span>
            </span>
          </div>
        </header>

        {/* メインコンテンツ */}
        <main className="space-y-12 mb-12">
          {/* AI投資分析 */}
          <section>
            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
              🤖 AI投資分析
            </h2>
            <InvestmentAnalysis />
          </section>

          {/* トップ仮想通貨リスト */}
          <TopCryptos />

          {/* チャートセクション */}
          <section>
            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
              価格チャート
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CryptoChart symbol="BTC" name="Bitcoin" />
              <CryptoChart symbol="ETH" name="Ethereum" />
            </div>
          </section>

          {/* ポートフォリオセクション */}
          <section>
            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
              💼 ポートフォリオ管理
            </h2>
            <Portfolio />
          </section>

          {/* バックテストセクション */}
          <section>
            <Backtest />
          </section>

          {/* 取引シミュレーターセクション */}
          <section>
            <TradingSimulator />
          </section>
        </main>
      </div>
    </div>
  )
}

export default App
