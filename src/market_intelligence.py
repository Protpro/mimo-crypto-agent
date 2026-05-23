"""
Market Intelligence Module
Real-time crypto market analysis powered by MiMo-V2.5-Pro
"""

import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .mimo_client import MiMoClient


@dataclass
class MarketSignal:
    """Trading signal with confidence and reasoning."""
    asset: str
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-1
    reasoning: str
    timeframe: str
    risk_level: str
    timestamp: str


class MarketIntelligence:
    """
    AI-powered market intelligence using MiMo's reasoning capabilities.
    
    Combines real-time market data with MiMo's deep analysis for
    actionable trading insights and market sentiment.
    """
    
    SYSTEM_PROMPT = """You are an expert crypto market analyst powered by Xiaomi MiMo-V2.5-Pro.
Your analysis combines technical indicators, on-chain data, and market sentiment.
Always provide:
1. Clear BUY/SELL/HOLD recommendation
2. Confidence level (0-100%)
3. Detailed reasoning
4. Risk assessment
5. Timeframe for the signal

Output in JSON format with keys: signal, confidence, reasoning, risk_level, timeframe, key_levels, catalysts"""
    
    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
    
    def get_market_data(self, coin_id: str = "bitcoin") -> Dict[str, Any]:
        """Fetch current market data from CoinGecko."""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
            }
            resp = requests.get(url, params=params, timeout=10)
            return resp.json() if resp.ok else {}
        except Exception:
            return {}
    
    def get_trending_coins(self) -> List[Dict]:
        """Get trending coins from CoinGecko."""
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            resp = requests.get(url, timeout=10)
            data = resp.json() if resp.ok else {}
            return data.get("coins", [])
        except Exception:
            return []
    
    def analyze_asset(self, coin_id: str = "bitcoin") -> MarketSignal:
        """
        Perform deep analysis on a crypto asset.
        
        Uses MiMo-V2.5-Pro's reasoning to analyze market data
        and generate actionable trading signals.
        """
        # Fetch market data
        market_data = self.get_market_data(coin_id)
        
        if not market_data:
            return MarketSignal(
                asset=coin_id,
                signal="HOLD",
                confidence=0.0,
                reasoning="Unable to fetch market data",
                timeframe="N/A",
                risk_level="HIGH",
                timestamp=datetime.utcnow().isoformat(),
            )
        
        # Extract key metrics
        market_info = market_data.get("market_data", {})
        analysis_context = f"""
Analyze this crypto asset and provide a trading signal:

Asset: {market_data.get('name', coin_id)} ({market_data.get('symbol', '?').upper()})
Current Price: ${market_info.get('current_price', {}).get('usd', 'N/A')}
24h Change: {market_info.get('price_change_percentage_24h', 'N/A')}%
7d Change: {market_info.get('price_change_percentage_7d', 'N/A')}%
30d Change: {market_info.get('price_change_percentage_30d', 'N/A')}%
Market Cap: ${market_info.get('market_cap', {}).get('usd', 'N/A'):,}
24h Volume: ${market_info.get('total_volume', {}).get('usd', 'N/A'):,}
ATH: ${market_info.get('ath', {}).get('usd', 'N/A')}
ATH Change: {market_info.get('ath_change_percentage', {}).get('usd', 'N/A')}%
Supply: {market_info.get('circulating_supply', 'N/A')} / {market_info.get('max_supply', 'N/A')}

Provide a JSON analysis with signal, confidence, reasoning, risk_level, timeframe, key_levels, and catalysts.
"""
        
        # Get MiMo analysis
        response = self.mimo.analyze(analysis_context, system=self.SYSTEM_PROMPT)
        
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}
        
        return MarketSignal(
            asset=coin_id,
            signal=analysis.get("signal", "HOLD"),
            confidence=analysis.get("confidence", 50) / 100,
            reasoning=analysis.get("reasoning", ""),
            timeframe=analysis.get("timeframe", "1-7 days"),
            risk_level=analysis.get("risk_level", "MEDIUM"),
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def analyze_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze an entire portfolio and provide rebalancing suggestions.
        
        Args:
            holdings: List of {"coin_id": str, "amount": float, "entry_price": float}
        """
        portfolio_context = f"""
Analyze this crypto portfolio and provide optimization suggestions:

Holdings:
{json.dumps(holdings, indent=2)}

Provide JSON with:
1. total_value: estimated current value
2. allocation: percentage per asset
3. risk_score: 1-10
4. suggestions: list of rebalancing recommendations
5. opportunities: potential new positions
6. warnings: any risk alerts
"""
        
        response = self.mimo.analyze(portfolio_context, system=self.SYSTEM_PROMPT)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}
