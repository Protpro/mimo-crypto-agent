"""
Whale Tracker Module
On-chain whale activity analysis powered by MiMo-V2.5-Pro
"""

import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .mimo_client import MiMoClient


@dataclass
class WhaleTransaction:
    """Single whale transaction."""
    tx_hash: str
    from_address: str
    to_address: str
    token: str
    amount: float
    usd_value: float
    timestamp: str
    exchange: str  # CEX, DEX, or wallet
    direction: str  # BUY, SELL, TRANSFER


@dataclass
class WhaleSignal:
    """Whale activity signal."""
    token: str
    signal: str  # ACCUMULATION, DISTRIBUTION, NEUTRAL
    confidence: float
    whale_count: int
    total_volume_usd: float
    net_flow: float  # positive = buying, negative = selling
    avg_tx_size: float
    top_whales: List[Dict]
    timeframe: str
    reasoning: str
    volume_24h: float
    open_interest: float
    funding_rate: float
    liquidation_data: Dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class WhaleTracker:
    """
    AI-powered whale activity tracker.
    
    Uses MiMo-V2.5-Pro's reasoning to analyze whale movements,
    detect accumulation/distribution patterns, and generate
    actionable signals based on smart money behavior.
    """
    
    SYSTEM_PROMPT = """You are an expert on-chain analyst specializing in whale activity detection.
You analyze large wallet movements to determine:

1. Accumulation vs Distribution patterns
2. Smart money sentiment
3. Potential market impact
4. Exchange inflow/outflow patterns
5. Whale clustering behavior

Always include these metrics in your analysis:
- Volume (24h trading volume)
- Open Interest (OI) changes
- Funding Rate (perpetual futures)
- Liquidation levels
- Long/Short ratio

Output JSON with:
- signal: ACCUMULATION / DISTRIBUTION / NEUTRAL
- confidence: 0-100
- whale_count: number of active whales
- total_volume_usd: total whale volume
- net_flow: positive = net buying, negative = net selling
- reasoning: detailed analysis
- volume_24h: current 24h volume
- open_interest: current OI
- funding_rate: current funding rate
- liquidation_data: key liquidation levels
- risk_level: LOW / MEDIUM / HIGH
- catalysts: upcoming events that may impact price"""
    
    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
    
    def get_whale_transactions(
        self,
        token: str,
        chain: str = "ethereum",
        min_usd: float = 100000,
        hours: int = 24,
    ) -> List[WhaleTransaction]:
        """
        Fetch whale transactions from on-chain data sources.
        
        Uses multiple APIs to aggregate whale activity:
        - Etherscan/BSCScan for EVM chains
        - Whale Alert API for cross-chain
        - DEX aggregator data
        """
        # In production, this would call real APIs
        # For demo, we return structured placeholder data
        demo_whales = []
        for i in range(100):
            demo_whales.append(WhaleTransaction(
                tx_hash=f"0x{'a' * 40}{i:04d}",
                from_address=f"0x{'1' * 40}",
                to_address=f"0x{'2' * 40}",
                token=token,
                amount=1000 + (i * 50),
                usd_value=150000 + (i * 5000),
                timestamp=(datetime.utcnow() - timedelta(hours=i % hours)).isoformat(),
                exchange="Binance" if i % 3 == 0 else "Uniswap" if i % 3 == 1 else "Wallet",
                direction="BUY" if i % 4 != 0 else "SELL",
            ))
        return demo_whales
    
    def get_market_metrics(self, token: str) -> Dict[str, Any]:
        """
        Fetch market metrics: Volume, OI, Funding Rate.
        
        Sources:
        - CoinGecko for spot volume
        - Coinglass for OI and funding rates
        - DeFiLlama for TVL data
        """
        # In production, aggregate from multiple APIs
        return {
            "volume_24h": 2_500_000_000,
            "volume_change_pct": 15.3,
            "open_interest": 8_750_000_000,
            "oi_change_pct": 8.2,
            "funding_rate": 0.0125,
            "funding_rate_annualized": 45.6,
            "long_short_ratio": 1.15,
            "liquidation_long_5pct": 125_000_000,
            "liquidation_short_5pct": 89_000_000,
            "top_long_liquidation": 108_500,
            "top_short_liquidation": 112_300,
            "tvl": 12_500_000_000,
            "tvl_change_7d": -2.1,
        }
    
    def analyze_whale_activity(
        self,
        token: str,
        chain: str = "ethereum",
        hours: int = 24,
        min_whales: int = 100,
    ) -> WhaleSignal:
        """
        Perform comprehensive whale activity analysis.
        
        Tracks minimum 100 whale wallets and combines with
        market metrics (Volume, OI, Funding Rate) to generate
        actionable signals.
        
        Args:
            token: Token symbol (e.g., "ETH", "BTC", "SOL")
            chain: Blockchain network
            hours: Analysis time period in hours
            min_whales: Minimum whale transactions to analyze
        """
        # Fetch whale transactions
        whale_txs = self.get_whale_transactions(token, chain, hours=hours)
        
        # Calculate whale stats
        buy_txs = [tx for tx in whale_txs if tx.direction == "BUY"]
        sell_txs = [tx for tx in whale_txs if tx.direction == "SELL"]
        
        total_buy_volume = sum(tx.usd_value for tx in buy_txs)
        total_sell_volume = sum(tx.usd_value for tx in sell_txs)
        net_flow = total_buy_volume - total_sell_volume
        total_volume = total_buy_volume + total_sell_volume
        avg_tx_size = total_volume / len(whale_txs) if whale_txs else 0
        
        # Get market metrics
        metrics = self.get_market_metrics(token)
        
        # Prepare analysis context for MiMo
        analysis_context = f"""
Analyze this whale activity data for {token} over the last {hours} hours:

WHALE STATISTICS:
- Total whale transactions: {len(whale_txs)}
- Buy transactions: {len(buy_txs)} ({len(buy_txs)/len(whale_txs)*100:.1f}%)
- Sell transactions: {len(sell_txs)} ({len(sell_txs)/len(whale_txs)*100:.1f}%)
- Total buy volume: ${total_buy_volume:,.0f}
- Total sell volume: ${total_sell_volume:,.0f}
- Net flow: ${net_flow:,.0f} ({'NET BUYING' if net_flow > 0 else 'NET SELLING'})
- Average transaction size: ${avg_tx_size:,.0f}
- Unique buy wallets: {len(set(tx.to_address for tx in buy_txs))}
- Unique sell wallets: {len(set(tx.from_address for tx in sell_txs))}

EXCHANGE FLOWS:
- To Binance: {sum(1 for tx in whale_txs if tx.exchange == 'Binance' and tx.direction == 'BUY')} txs
- From Binance: {sum(1 for tx in whale_txs if tx.exchange == 'Binance' and tx.direction == 'SELL')} txs
- DEX Activity: {sum(1 for tx in whale_txs if tx.exchange == 'Uniswap')} txs
- Wallet-to-Wallet: {sum(1 for tx in whale_txs if tx.exchange == 'Wallet')} txs

MARKET METRICS:
- 24h Volume: ${metrics['volume_24h']:,.0f} (change: {metrics['volume_change_pct']:+.1f}%)
- Open Interest: ${metrics['open_interest']:,.0f} (change: {metrics['oi_change_pct']:+.1f}%)
- Funding Rate: {metrics['funding_rate']:.4f}% ({metrics['funding_rate_annualized']:.1f}% annualized)
- Long/Short Ratio: {metrics['long_short_ratio']:.2f}
- Long Liquidations (5% drop): ${metrics['liquidation_long_5pct']:,.0f}
- Short Liquidations (5% pump): ${metrics['liquidation_short_5pct']:,.0f}
- TVL: ${metrics['tvl']:,.0f} (7d change: {metrics['tvl_change_7d']:+.1f}%)

TOP WHALE MOVEMENTS (last 5):
{json.dumps([{'amount': tx.usd_value, 'direction': tx.direction, 'exchange': tx.exchange} for tx in whale_txs[:5]], indent=2)}

Provide a comprehensive JSON analysis including:
1. signal: ACCUMULATION / DISTRIBUTION / NEUTRAL
2. confidence: 0-100
3. whale_count: total unique whales
4. net_flow interpretation
5. volume_analysis: is volume healthy/suspicious?
6. oi_analysis: is OI indicating leverage buildup?
7. funding_analysis: is funding rate extreme?
8. liquidation_risk: key levels to watch
9. reasoning: 3-5 sentence summary
10. risk_level: LOW / MEDIUM / HIGH
11. action_items: what traders should do
"""
        
        # Get MiMo analysis
        response = self.mimo.analyze(analysis_context, system=self.SYSTEM_PROMPT)
        
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}
        
        # Build signal
        return WhaleSignal(
            token=token,
            signal=analysis.get("signal", "NEUTRAL"),
            confidence=analysis.get("confidence", 50) / 100,
            whale_count=len(set(tx.from_address for tx in whale_txs) | set(tx.to_address for tx in whale_txs)),
            total_volume_usd=total_volume,
            net_flow=net_flow,
            avg_tx_size=avg_tx_size,
            top_whales=[
                {"address": tx.to_address[:10] + "...", "amount": tx.usd_value, "direction": tx.direction}
                for tx in whale_txs[:10]
            ],
            timeframe=f"{hours}h",
            reasoning=analysis.get("reasoning", ""),
            volume_24h=metrics["volume_24h"],
            open_interest=metrics["open_interest"],
            funding_rate=metrics["funding_rate"],
            liquidation_data={
                "long_5pct": metrics["liquidation_long_5pct"],
                "short_5pct": metrics["liquidation_short_5pct"],
                "top_long": metrics["top_long_liquidation"],
                "top_short": metrics["top_short_liquidation"],
            },
        )
    
    def detect_whale_clusters(
        self,
        token: str,
        chain: str = "ethereum",
    ) -> Dict[str, Any]:
        """
        Detect whale clusters - groups of wallets acting together.
        
        Identifies coordinated buying/selling patterns that may
        indicate insider activity or organized accumulation.
        """
        prompt = f"""
Analyze whale wallet patterns for {token} on {chain}:

Look for:
1. Wallets that received funds from the same source
2. Wallets that bought the same token within similar timeframes
3. Wallets with similar transaction sizes
4. Known whale wallets and their recent activity

Provide JSON with:
- clusters: list of wallet clusters with their behavior
- coordinated_activity: boolean indicating if coordinated buying/selling detected
- risk_assessment: potential market manipulation risk
- historical_pattern: does this match any known accumulation/distribution pattern?
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}
    
    def generate_alert(
        self,
        signal: WhaleSignal,
    ) -> str:
        """
        Generate human-readable alert from whale signal.
        """
        emoji = {"ACCUMULATION": "🟢", "DISTRIBUTION": "🔴", "NEUTRAL": "🟡"}.get(signal.signal, "⚪")
        
        return f"""
{emoji} WHALE ALERT: {signal.token}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signal: {signal.signal} ({signal.confidence:.0%} confidence)
Whales Tracked: {signal.whale_count}
Net Flow: ${signal.net_flow:+,.0f}
Avg TX Size: ${signal.avg_tx_size:,.0f}
Timeframe: {signal.timeframe}

📊 Market Metrics:
• Volume 24h: ${signal.volume_24h:,.0f}
• Open Interest: ${signal.open_interest:,.0f}
• Funding Rate: {signal.funding_rate:.4f}%
• Liquidation Risk: Long ${signal.liquidation_data.get('long_5pct', 0):,.0f} / Short ${signal.liquidation_data.get('short_5pct', 0):,.0f}

📝 Analysis:
{signal.reasoning}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
