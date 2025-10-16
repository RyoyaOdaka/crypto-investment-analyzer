import { useState, useEffect } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Checking...')

  useEffect(() => {
    // バックエンドAPIのヘルスチェック
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setApiStatus(data.status || 'connected'))
      .catch(() => setApiStatus('disconnected'))
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Crypto Investment Analyzer
          </h1>
          <p className="text-xl text-gray-600">
            仮想通貨投資分析アプリ
          </p>
          <div className="mt-4">
            <span className="inline-block px-4 py-2 bg-white rounded-full shadow-sm">
              API Status: <span className={apiStatus === 'healthy' ? 'text-green-600' : 'text-red-600'}>
                {apiStatus}
              </span>
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-3">
              リアルタイム価格
            </h2>
            <p className="text-gray-600">
              仮想通貨の価格をリアルタイムで取得・表示
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-3">
              チャート分析
            </h2>
            <p className="text-gray-600">
              テクニカル指標を使った価格チャート分析
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-3">
              ポートフォリオ
            </h2>
            <p className="text-gray-600">
              保有資産の管理と損益計算
            </p>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-500">
            開発中...近日公開予定
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
