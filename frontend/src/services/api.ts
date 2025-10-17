import axios from 'axios';

// Viteのプロキシを使用（/api -> http://backend:8000）
export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// レスポンスの型定義
export interface CryptoPrice {
  symbol: string;
  name: string;
  current_price: number;
  price_change_24h?: number;
  price_change_percentage_24h?: number;
  market_cap?: number;
  total_volume?: number;
  high_24h?: number;
  low_24h?: number;
  last_updated: string;
}

export interface CryptoListResponse {
  coins: CryptoPrice[];
  total: number;
}

export interface ChartDataPoint {
  timestamp: number;
  price: number;
}

export interface ChartDataResponse {
  symbol: string;
  name: string;
  prices: ChartDataPoint[];
  total_points: number;
}

export interface Portfolio {
  id: number;
  symbol: string;
  name: string;
  amount: number;
  purchase_price: number;
  purchase_date: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  current_price: number;
  current_value: number;
  purchase_value: number;
  profit_loss: number;
  profit_loss_percentage: number;
}

export interface PortfolioCreate {
  symbol: string;
  name: string;
  amount: number;
  purchase_price: number;
  purchase_date: string;
  notes?: string;
}

export interface PortfolioListResponse {
  portfolios: Portfolio[];
  total: number;
  total_value: number;
  total_profit_loss: number;
  total_profit_loss_percentage: number;
}

export interface MACDIndicator {
  macd_line: number;
  signal_line: number;
  histogram: number;
  signal: string;
}

export interface BollingerBands {
  upper_band: number;
  middle_band: number;
  lower_band: number;
  current_position: string;
}

export interface TechnicalIndicators {
  rsi: number | null;
  volatility: number;
  trend: string;
  trend_strength: number;
  price_change_7d: number;
  price_change_30d: number;
  macd: MACDIndicator | null;
  bollinger_bands: BollingerBands | null;
}

export interface InvestmentRecommendation {
  symbol: string;
  name: string;
  current_price: number;
  recommendation_score: number;
  recommendation: string;
  risk_level: string;
  technical_indicators: TechnicalIndicators;
  reasoning: string;
}

export interface InvestmentAnalysisResponse {
  recommendations: InvestmentRecommendation[];
  total: number;
}

// API関数
export const cryptoApi = {
  getPrice: async (symbol: string): Promise<CryptoPrice> => {
    const response = await api.get<CryptoPrice>(`/crypto/price/${symbol}`);
    return response.data;
  },

  getMultiplePrices: async (symbols: string[]): Promise<CryptoListResponse> => {
    const params = new URLSearchParams();
    symbols.forEach(symbol => params.append('symbols', symbol));
    const response = await api.get<CryptoListResponse>(`/crypto/prices?${params}`);
    return response.data;
  },

  getTopCoins: async (limit: number = 10): Promise<CryptoListResponse> => {
    const response = await api.get<CryptoListResponse>(`/crypto/top?limit=${limit}`);
    return response.data;
  },

  getChartData: async (symbol: string, days: number = 7): Promise<ChartDataResponse> => {
    const response = await api.get<ChartDataResponse>(`/crypto/chart/${symbol}?days=${days}`);
    return response.data;
  },
};

export const portfolioApi = {
  getPortfolios: async (): Promise<PortfolioListResponse> => {
    const response = await api.get<PortfolioListResponse>('/portfolio/');
    return response.data;
  },

  createPortfolio: async (data: PortfolioCreate): Promise<Portfolio> => {
    const response = await api.post<Portfolio>('/portfolio/', data);
    return response.data;
  },

  deletePortfolio: async (id: number): Promise<void> => {
    await api.delete(`/portfolio/${id}`);
  },
};

export const analysisApi = {
  getRecommendations: async (limit: number = 10): Promise<InvestmentAnalysisResponse> => {
    const response = await api.get<InvestmentAnalysisResponse>(`/analysis/recommendations?limit=${limit}`);
    return response.data;
  },

  getRecommendation: async (symbol: string): Promise<InvestmentRecommendation> => {
    const response = await api.get<InvestmentRecommendation>(`/analysis/recommend/${symbol}`);
    return response.data;
  },
};

export interface BacktestStrategy {
  name: string;
  buy_signal: string;
  sell_signal: string;
  initial_capital: number;
  trade_size_percent: number;
}

export interface BacktestTrade {
  trade_id: number;
  type: string;
  timestamp: string;
  price: number;
  amount: number;
  value: number;
  profit_loss?: number;
  profit_loss_percent?: number;
}

export interface BacktestMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_return: number;
  total_return_percent: number;
  max_drawdown: number;
  sharpe_ratio?: number;
  avg_profit_per_trade: number;
  avg_profit_per_winning_trade: number;
  avg_loss_per_losing_trade: number;
}

export interface BacktestRequest {
  symbol: string;
  strategy: BacktestStrategy;
  period_days: number;
}

export interface BacktestResponse {
  symbol: string;
  name: string;
  strategy: BacktestStrategy;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  trades: BacktestTrade[];
  metrics: BacktestMetrics;
  equity_curve: { timestamp: number; value: number }[];
}

export const backtestApi = {
  runBacktest: async (request: BacktestRequest): Promise<BacktestResponse> => {
    const response = await api.post<BacktestResponse>('/backtest/run', request);
    return response.data;
  },

  getStrategies: async () => {
    const response = await api.get('/backtest/strategies');
    return response.data;
  },
};
