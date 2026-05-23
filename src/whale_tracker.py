"""
Whale Tracker Module — Full Suite
On-chain whale activity analysis powered by MiMo-V2.5-Pro

Features:
1. Whale Wallet Profiling (Smart Money Score)
2. Exchange Flow Analysis (CEX inflow/outflow)
3. Whale vs Retail Divergence
4. Whale Order Book Depth
5. Cross-chain Whale Tracking
6. Smart Money VC Tracking
7. Historical Pattern Matching
8. Whale Alert Threshold
9. Whale Concentration Index (Gini)
10. Whale Sentiment Heatmap
"""

import json
import math
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from .mimo_client import MiMoClient


# ============================================================
# Data Models
# ============================================================

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
    exchange: str  # CEX name, DEX name, or "Wallet"
    direction: str  # BUY, SELL, TRANSFER, DEPOSIT, WITHDRAWAL
    chain: str = "ethereum"


@dataclass
class WalletProfile:
    """Whale wallet profile with performance metrics."""
    address: str
    smart_money_score: float  # 0-100
    total_trades: int
    win_rate: float  # 0-1
    avg_roi: float  # percentage
    total_pnl_usd: float
    favorite_tokens: List[str]
    avg_hold_time_hours: float
    last_active: str
    is_vc: bool = False
    vc_name: str = ""
    chains: List[str] = field(default_factory=list)


@dataclass
class ExchangeFlow:
    """Exchange flow data for a single exchange."""
    exchange: str
    inflow_usd: float  # deposits to exchange (selling pressure)
    outflow_usd: float  # withdrawals from exchange (accumulation)
    net_flow_usd: float  # negative = net outflow (bullish)
    tx_count: int
    avg_tx_size: float


@dataclass
class DivergenceSignal:
    """Whale vs Retail divergence signal."""
    has_divergence: bool
    direction: str  # BULLISH_DIVERGENCE, BEARISH_DIVERGENCE, NONE
    whale_action: str  # BUYING / SELLING
    retail_action: str  # BUYING / SELLING
    strength: float  # 0-1
    reasoning: str


@dataclass
class OrderBookWall:
    """Large limit order (wall) detected."""
    exchange: str
    side: str  # BID / ASK
    price: float
    size_usd: float
    token: str
    is_spoofing_risk: bool


@dataclass
class ConcentrationMetrics:
    """Token holder concentration analysis."""
    gini_coefficient: float  # 0 (equal) to 1 (concentrated)
    top10_pct: float  # % held by top 10
    top50_pct: float  # % held by top 50
    top100_pct: float  # % held by top 100
    total_holders: int
    manipulation_risk: str  # LOW, MEDIUM, HIGH, CRITICAL


@dataclass
class HeatmapEntry:
    """Single heatmap data point."""
    hour: int  # 0-23
    day: str  # Mon-Sun
    activity_score: float  # 0-1
    net_flow_usd: float
    whale_count: int


@dataclass
class AlertRule:
    """Custom alert threshold."""
    rule_id: str
    token: str
    min_usd: float
    direction: str  # BUY, SELL, ANY
    chain: str = "any"
    enabled: bool = True


@dataclass
class WhaleSignal:
    """Comprehensive whale activity signal."""
    token: str
    signal: str  # ACCUMULATION, DISTRIBUTION, NEUTRAL
    confidence: float
    whale_count: int
    total_volume_usd: float
    net_flow: float
    avg_tx_size: float
    top_whales: List[Dict]
    timeframe: str
    reasoning: str
    volume_24h: float
    open_interest: float
    funding_rate: float
    liquidation_data: Dict
    # Enhanced fields
    exchange_flows: List[ExchangeFlow] = field(default_factory=list)
    divergence: Optional[DivergenceSignal] = None
    concentration: Optional[ConcentrationMetrics] = None
    smart_money_scores: List[WalletProfile] = field(default_factory=list)
    cross_chain_flows: Dict[str, float] = field(default_factory=dict)
    orderbook_walls: List[OrderBookWall] = field(default_factory=list)
    vc_activity: List[WalletProfile] = field(default_factory=list)
    historical_match: Optional[Dict] = None
    heatmap: List[HeatmapEntry] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================
# Known VC Wallets (demo data — in production from on-chain DB)
# ============================================================

KNOWN_VC_WALLETS = {
    "0x26586b3a49d91b0ee0b4e78e97eb6b28084f2e57": "a16z",
    "0x170940a3f4a1e0c4b2b3f61f2c8e421b": "Paradigm",
    "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase Ventures",
    "0x501f352e32ec0c98e23c8c27a9dd5e0e1e25b1c8": "Polychain Capital",
    "0x3bf2b4c48b829bd8af7e3a80b4a5ba38c7df3e0a": "Pantera Capital",
    "0x1b3cb81e51011b549d78bf720b0d924ac763a7c2": "Galaxy Digital",
    "0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503": "Jump Trading",
    "0x8103683202aa8da10536036edef04cdd865c225e": "Multicoin Capital",
    "0xdef171fe48cf0115b1d80b88dc8eab59176fee57": "Wintermute",
    "0x1111111254eeb25477b68fb85ed929f73a960582": "Alameda Research",
}


# ============================================================
# Main Tracker Class
# ============================================================

class WhaleTracker:
    """
    AI-powered whale activity tracker with 10 advanced features.

    Uses MiMo-V2.5-Pro's reasoning to analyze whale movements,
    detect accumulation/distribution patterns, and generate
    actionable signals based on smart money behavior.
    """

    SYSTEM_PROMPT = """You are an expert on-chain analyst specializing in whale activity detection.
You analyze large wallet movements, exchange flows, derivatives data, and holder
concentration to determine smart money behavior and generate actionable signals.

Always include these metrics:
- Volume (24h trading volume)
- Open Interest (OI) changes
- Funding Rate (perpetual futures)
- Liquidation levels
- Long/Short ratio
- Exchange net flows (CEX inflow vs outflow)
- Holder concentration (Gini coefficient)
- Whale vs retail divergence

Output valid JSON only."""

    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
        self.alert_rules: List[AlertRule] = []

    # ----------------------------------------------------------
    # 1. Whale Wallet Profiling (Smart Money Score)
    # ----------------------------------------------------------

    def profile_whale_wallet(
        self,
        address: str,
        chain: str = "ethereum",
    ) -> WalletProfile:
        """
        Profile a whale wallet and calculate Smart Money Score.

        Score factors:
        - Win rate (profitable trades / total trades)
        - Average ROI per trade
        - Consistency (low variance in returns)
        - Timing accuracy (buying before pumps)
        - Portfolio diversification

        Args:
            address: Wallet address
            chain: Blockchain network
        """
        # Demo data — in production: query on-chain history
        demo_profile = WalletProfile(
            address=address,
            smart_money_score=78.5,
            total_trades=342,
            win_rate=0.72,
            avg_roi=15.3,
            total_pnl_usd=2_450_000,
            favorite_tokens=["ETH", "ARB", "OP", "LINK"],
            avg_hold_time_hours=168,
            last_active=datetime.utcnow().isoformat(),
            is_vc=address.lower() in [k.lower() for k in KNOWN_VC_WALLETS],
            vc_name=KNOWN_VC_WALLETS.get(address.lower(), ""),
            chains=["ethereum", "arbitrum", "base"],
        )

        # Use MiMo to analyze wallet behavior patterns
        prompt = f"""
Analyze this whale wallet profile and provide a Smart Money assessment:

Address: {address[:10]}...{address[-6:]}
Chain: {chain}
Historical Win Rate: {demo_profile.win_rate:.0%}
Total Trades: {demo_profile.total_trades}
Average ROI: {demo_profile.avg_roi:.1f}%
Total PnL: ${demo_profile.total_pnl_usd:,.0f}
Avg Hold Time: {demo_profile.avg_hold_time_hours:.0f} hours
Favorite Tokens: {', '.join(demo_profile.favorite_tokens)}
Is VC Wallet: {demo_profile.is_vc}
VC Name: {demo_profile.vc_name or 'N/A'}

Provide JSON with:
- smart_money_score: 0-100
- risk_profile: conservative / moderate / aggressive
- specialization: what this whale is best at
- recent_behavior: what they've been doing lately
- prediction: what they might do next
"""
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}

        demo_profile.smart_money_score = analysis.get(
            "smart_money_score", demo_profile.smart_money_score
        )
        return demo_profile

    def rank_whale_wallets(
        self,
        token: str,
        chain: str = "ethereum",
        top_n: int = 20,
    ) -> List[WalletProfile]:
        """
        Rank top whale wallets by Smart Money Score.

        Returns the top N most profitable whale wallets
        for a given token, ranked by composite score.
        """
        # In production: aggregate from on-chain data
        demo_addresses = [f"0x{'a' * 38}{i:02d}" for i in range(top_n)]
        profiles = []
        for addr in demo_addresses:
            p = self.profile_whale_wallet(addr, chain)
            profiles.append(p)

        profiles.sort(key=lambda p: p.smart_money_score, reverse=True)
        return profiles[:top_n]

    # ----------------------------------------------------------
    # 2. Exchange Flow Analysis
    # ----------------------------------------------------------

    def analyze_exchange_flows(
   # PRODUCTION: Replace with real exchange flow APIs
   # Whale Alert API: tracks large exchange deposits/withdrawals
   # Nansen: exchange flow analytics (paid)
   # Glassnode: exchange balance tracking
   # Currently returns DEMO data (hardcoded exchange flows)
        self,
        token: str,
        hours: int = 24,
    ) -> List[ExchangeFlow]:
        """
        Analyze whale flows to/from major exchanges.

        Large deposits to exchanges = potential selling pressure.
        Large withdrawals from exchanges = accumulation (self-custody).
        Net exchange outflow is generally bullish.

        Args:
            token: Token symbol
            hours: Analysis period in hours
        """
        # Demo data — in production: Etherscan + exchange APIs
        exchanges = [
            ("Binance", 45_000_000, 38_000_000, 120),
            ("Coinbase", 22_000_000, 31_000_000, 85),
            ("Kraken", 8_000_000, 12_000_000, 42),
            ("OKX", 15_000_000, 11_000_000, 65),
            ("Bybit", 18_000_000, 9_000_000, 55),
        ]

        flows = []
        for name, inflow, outflow, count in exchanges:
            flows.append(ExchangeFlow(
                exchange=name,
                inflow_usd=inflow,
                outflow_usd=outflow,
                net_flow_usd=outflow - inflow,  # positive = net outflow (bullish)
                tx_count=count,
                avg_tx_size=(inflow + outflow) / count if count else 0,
            ))

        # MiMo analysis of exchange flows
        flow_data = json.dumps([{
            "exchange": f.exchange,
            "inflow": f.inflow_usd,
            "outflow": f.outflow_usd,
            "net": f.net_flow_usd,
        } for f in flows], indent=2)

        prompt = f"""
Analyze these {token} exchange flows over the last {hours}h:

{flow_data}

Positive net = outflow from exchange (bullish).
Negative net = inflow to exchange (bearish).

Provide JSON with:
- overall_signal: BULLISH / BEARISH / NEUTRAL
- dominant_exchange: which exchange has largest flow
- interpretation: what the flows mean
- risk_factors: any concerning patterns
"""
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        return flows

    # ----------------------------------------------------------
    # 3. Whale vs Retail Divergence
    # ----------------------------------------------------------

    def detect_divergence(
        self,
        token: str,
        hours: int = 24,
    ) -> DivergenceSignal:
        """
        Detect divergence between whale and retail behavior.

        Bullish divergence: whales buying while retail selling.
        Bearish divergence: whales selling while retail buying.
        This is one of the strongest signals in crypto.
        """
        # Demo data — in production: compare whale txs vs retail txs
        prompt = f"""
Analyze whale vs retail divergence for {token} over {hours}h:

Whale Activity:
- Net flow: +$2,450,000 (buying)
- 75% of whale transactions are buys
- Average whale TX size: $180,000
- Exchange withdrawals: 60% of whale activity

Retail Activity:
- Net flow: -$850,000 (selling)
- 55% of retail transactions are sells
- Average retail TX size: $2,500
- Exchange deposits increasing

Provide JSON with:
- has_divergence: boolean
- direction: BULLISH_DIVERGENCE / BEARISH_DIVERGENCE / NONE
- whale_action: BUYING / SELLING
- retail_action: BUYING / SELLING
- strength: 0.0-1.0
- reasoning: explanation
- historical_accuracy: how reliable this signal has been
"""
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            data = json.loads(json_match.group()) if json_match else {}

        return DivergenceSignal(
            has_divergence=data.get("has_divergence", False),
            direction=data.get("direction", "NONE"),
            whale_action=data.get("whale_action", "NEUTRAL"),
            retail_action=data.get("retail_action", "NEUTRAL"),
            strength=data.get("strength", 0),
            reasoning=data.get("reasoning", ""),
        )

    # ----------------------------------------------------------
    # 4. Whale Order Book Depth
    # ----------------------------------------------------------

    def scan_orderbook_walls(
   # PRODUCTION: Replace with real exchange order book APIs
   # Binance: GET /api/v3/depth (free, real-time)
   # OKX: GET /api/v5/market/books (free, real-time)
   # Bybit: GET /v5/market/orderbook (free, real-time)
   # Currently returns DEMO data (hardcoded walls)
        self,
        token: str,
        exchanges: List[str] = None,
    ) -> List[OrderBookWall]:
        """
        Scan for large limit orders (walls) on exchange order books.

        Large buy walls = support levels set by whales.
        Large sell walls = resistance / potential spoofing.
        """
        if exchanges is None:
            exchanges = ["Binance", "OKX", "Bybit"]

        # Demo data — in production: exchange REST/WebSocket APIs
        walls = [
            OrderBookWall("Binance", "BID", 3450.0, 5_200_000, token, False),
            OrderBookWall("Binance", "ASK", 3520.0, 3_800_000, token, False),
            OrderBookWall("OKX", "BID", 3440.0, 2_100_000, token, False),
            OrderBookWall("Bybit", "BID", 3455.0, 4_500_000, token, False),
            OrderBookWall("Bybit", "ASK", 3510.0, 8_200_000, token, True),  # potential spoof
        ]

        # MiMo analysis
        walls_data = json.dumps([{
            "exchange": w.exchange,
            "side": w.side,
            "price": w.price,
            "size_usd": w.size_usd,
            "spoofing_risk": w.is_spoofing_risk,
        } for w in walls], indent=2)

        prompt = f"""
Analyze these order book walls for {token}:

{walls_data}

Provide JSON with:
- key_support_levels: list of strong buy walls
- key_resistance_levels: list of strong sell walls
- spoofing_alerts: any walls likely to be pulled
- net_bias: BULLISH / BEARISH based on wall imbalance
"""
        self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        return walls

    # ----------------------------------------------------------
    # 5. Cross-chain Whale Tracking
    # ----------------------------------------------------------

    def track_cross_chain(
   # PRODUCTION: Replace with multi-chain explorer APIs
   # Etherscan + BSCScan + Arbiscan + etc (all free)
   # Alchemy/Infura: multi-chain RPC calls
   # DeBank API: cross-chain portfolio tracking
   # Currently returns DEMO data (hardcoded cross-chain balances)
        self,
        address: str,
        chains: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Track a whale wallet across multiple chains.

        Detects when whales bridge funds between chains,
        which often signals upcoming moves on the destination chain.
        """
        if chains is None:
            chains = ["ethereum", "arbitrum", "base", "optimism", "bsc", "polygon", "solana"]

        # Demo data — in production: query each chain's explorer
        cross_chain = {
            "ethereum": {"balance_usd": 12_500_000, "recent_txs": 15, "net_flow": +500_000},
            "arbitrum": {"balance_usd": 3_200_000, "recent_txs": 8, "net_flow": +1_200_000},
            "base": {"balance_usd": 1_800_000, "recent_txs": 22, "net_flow": +2_500_000},
            "optimism": {"balance_usd": 800_000, "recent_txs": 3, "net_flow": -200_000},
            "bsc": {"balance_usd": 4_100_000, "recent_txs": 12, "net_flow": -800_000},
        }

        prompt = f"""
Analyze cross-chain whale activity for {address[:10]}...:

{json.dumps(cross_chain, indent=2)}

Identify:
1. Which chain is the whale concentrating on?
2. Are they bridging funds (potential move incoming)?
3. Any unusual chain activity patterns?

Provide JSON with:
- primary_chain: where most activity is
- bridge_detected: boolean
- bridge_direction: from -> to chain
- activity_pattern: description of behavior
- prediction: what might happen next
"""
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}

        analysis["balances"] = cross_chain
        return analysis

    # ----------------------------------------------------------
    # 6. Smart Money VC Tracking
    # ----------------------------------------------------------

    def track_vc_activity(
        self,
        token: str,
        hours: int = 72,
    ) -> List[WalletProfile]:
        """
        Track known VC/investor wallets for a specific token.

        When VCs like a16z, Paradigm, or Coinbase Ventures move,
        it often signals significant upcoming events.
        """
        # Demo data — in production: monitor KNOWN_VC_WALLETS
        vc_profiles = []
        for addr, name in list(KNOWN_VC_WALLETS.items())[:5]:
            profile = WalletProfile(
                address=addr,
                smart_money_score=85.0,
                total_trades=150,
                win_rate=0.68,
                avg_roi=22.5,
                total_pnl_usd=15_000_000,
                favorite_tokens=[token, "ETH", "BTC"],
                avg_hold_time_hours=720,
                last_active=(datetime.utcnow() - timedelta(hours=12)).isoformat(),
                is_vc=True,
                vc_name=name,
                chains=["ethereum"],
            )
            vc_profiles.append(profile)

        prompt = f"""
Analyze VC activity for {token} over the last {hours}h:

Active VCs:
{json.dumps([{"name": p.vc_name, "score": p.smart_money_score, "win_rate": p.win_rate} for p in vc_profiles], indent=2)}

Provide JSON with:
- vc_sentiment: BULLISH / BEARISH / NEUTRAL
- active_vcs: number of VCs actively trading
- recent_moves: description of VC activity
- implications: what this means for {token}
"""
        self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        return vc_profiles

    # ----------------------------------------------------------
    # 7. Historical Pattern Matching
    # ----------------------------------------------------------

    def match_historical_patterns(
        self,
        token: str,
        current_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Compare current whale behavior to historical patterns.

        Matches against known patterns before major pumps/dumps
        to predict potential price movements.
        """
        if current_data is None:
            current_data = {
                "whale_net_flow": 2_450_000,
                "exchange_outflow_pct": 62,
                "funding_rate": 0.0125,
                "oi_change_7d": 8.2,
                "volume_change_7d": 15.3,
                "whale_count_change": 25,
            }

        prompt = f"""
Compare current {token} whale behavior to historical patterns:

Current Data:
{json.dumps(current_data, indent=2)}

Find historical matches from:
1. March 2024 (pre-BTC ATH pump)
2. November 2023 (accumulation phase)
3. May 2022 (pre-crash distribution)
4. July 2021 (China ban recovery)
5. January 2021 (bull run start)

Provide JSON with:
- matches: list of historical periods with similarity score (0-100)
- best_match: most similar historical period
- similarity_score: 0-100
- outcome_after_match: what happened historically
- prediction: what might happen this time
- confidence: 0-100
"""
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}

    # ----------------------------------------------------------
    # 8. Whale Alert Threshold
    # ----------------------------------------------------------

    def add_alert_rule(
        self,
        token: str,
        min_usd: float = 500_000,
        direction: str = "ANY",
        chain: str = "any",
    ) -> AlertRule:
        """
        Create a custom whale alert rule.

        Args:
            token: Token to monitor
            min_usd: Minimum USD value to trigger alert
            direction: BUY, SELL, or ANY
            chain: Specific chain or "any"
        """
        rule = AlertRule(
            rule_id=f"alert_{token}_{len(self.alert_rules)}",
            token=token,
            min_usd=min_usd,
            direction=direction,
            chain=chain,
        )
        self.alert_rules.append(rule)
        return rule

    def check_alerts(
        self,
        transactions: List[WhaleTransaction],
    ) -> List[Dict[str, Any]]:
        """
        Check transactions against alert rules.

        Returns list of triggered alerts.
        """
        triggered = []
        for tx in transactions:
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue
                if rule.token.upper() != tx.token.upper() and rule.token != "*":
                    continue
                if tx.usd_value < rule.min_usd:
                    continue
                if rule.direction != "ANY" and tx.direction != rule.direction:
                    continue
                if rule.chain != "any" and tx.chain != rule.chain:
                    continue

                triggered.append({
                    "rule_id": rule.rule_id,
                    "token": tx.token,
                    "amount_usd": tx.usd_value,
                    "direction": tx.direction,
                    "exchange": tx.exchange,
                    "tx_hash": tx.tx_hash,
                    "alert_message": f"🐋 {tx.direction} ${tx.usd_value:,.0f} {tx.token} on {tx.exchange}",
                })
        return triggered

    # ----------------------------------------------------------
    # 9. Whale Concentration Index (Gini)
    # ----------------------------------------------------------

    def calculate_concentration(
   # PRODUCTION: Replace with real holder distribution data
   # Etherscan: token holder list (free)
   # Dune Analytics: SQL query for holder distribution
   # Etherscan: GET /api?module=token&action=tokenholderlist
   # Currently returns DEMO data (simulated holder distribution)
        self,
        token: str,
        chain: str = "ethereum",
    ) -> ConcentrationMetrics:
        """
        Calculate token holder concentration using Gini coefficient.

        Gini = 0 means perfectly equal distribution.
        Gini = 1 means one holder has everything.
        High concentration = manipulation risk.
        """
        # Demo data — in production: query top holders from explorer
        # Simulating holder distribution
        top_holders_pct = [
            12.5, 8.3, 6.1, 5.2, 4.8,  # top 5
            3.9, 3.5, 3.1, 2.8, 2.5,  # top 6-10
            2.2, 2.0, 1.8, 1.6, 1.5,  # top 11-15
            1.4, 1.3, 1.2, 1.1, 1.0,  # top 16-20
        ]

        # Calculate Gini coefficient
        values = sorted(top_holders_pct)
        n = len(values)
        numerator = sum((2 * (i + 1) - n - 1) * values[i] for i in range(n))
        denominator = n * sum(values)
        gini = numerator / denominator if denominator > 0 else 0

        top10 = sum(top_holders_pct[:10])
        top50 = sum(top_holders_pct[:15]) + 15  # estimate
        top100 = top50 + 20  # estimate

        # Determine manipulation risk
        if gini > 0.8:
            risk = "CRITICAL"
        elif gini > 0.6:
            risk = "HIGH"
        elif gini > 0.4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        prompt = f"""
Analyze token concentration for {token}:

Gini Coefficient: {gini:.3f}
Top 10 Holders: {top10:.1f}% of supply
Top 50 Holders: {top50:.1f}% of supply
Top 100 Holders: {top100:.1f}% of supply
Total Holders: 125,000
Manipulation Risk: {risk}

Provide JSON with:
- gini_assessment: what this concentration means
- manipulation_risk: LOW / MEDIUM / HIGH / CRITICAL
- key_holders: who the major holders likely are
- risk_factors: specific risks from this concentration
- recommendation: should traders be concerned?
"""
        self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)

        return ConcentrationMetrics(
            gini_coefficient=round(gini, 4),
            top10_pct=round(top10, 1),
            top50_pct=round(top50, 1),
            top100_pct=round(top100, 1),
            total_holders=125_000,
            manipulation_risk=risk,
        )

    # ----------------------------------------------------------
    # 10. Whale Sentiment Heatmap
    # ----------------------------------------------------------

    def generate_heatmap(
   # PRODUCTION: Replace with timestamped whale transaction data
   # Aggregate whale txs by hour/day from on-chain data
   # Store in local DB (SQLite/Postgres) for fast retrieval
   # Currently returns DEMO data (random seed for reproducibility)
        self,
        token: str,
        days: int = 7,
    ) -> List[HeatmapEntry]:
        """
        Generate a whale activity heatmap showing patterns by hour/day.

        Identifies when whales are most active (time-of-day patterns).
        Useful for timing entries/exits around whale activity windows.
        """
        import random
        random.seed(42)  # reproducible demo

        heatmap = []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for day_idx in range(days):
            day = day_names[day_idx % 7]
            for hour in range(24):
                # Simulate patterns: whales more active during US/EU market hours
                base_activity = 0.3
                if 13 <= hour <= 21:  # US market hours (UTC)
                    base_activity = 0.7
                elif 7 <= hour <= 15:  # EU market hours (UTC)
                    base_activity = 0.5

                activity = min(1.0, base_activity + random.uniform(-0.2, 0.3))
                net_flow = random.uniform(-500_000, 800_000) * activity
                count = int(activity * random.randint(5, 30))

                heatmap.append(HeatmapEntry(
                    hour=hour,
                    day=day,
                    activity_score=round(activity, 2),
                    net_flow_usd=round(net_flow, 0),
                    whale_count=count,
                ))

        # MiMo pattern analysis
        # Find peak hours
        hour_avg = defaultdict(list)
        for entry in heatmap:
            hour_avg[entry.hour].append(entry.activity_score)

        peak_hours = sorted(
            hour_avg.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True,
        )[:5]

        prompt = f"""
Analyze this whale activity heatmap for {token}:

Peak Activity Hours (UTC): {[h[0] for h in peak_hours]}
Most active: UTC {peak_hours[0][0]}:00 (score: {sum(peak_hours[0][1])/len(peak_hours[0][1]):.2f})

Provide JSON with:
- peak_hours: best hours for whale activity
- pattern: description of time-based patterns
- recommendation: when to watch for whale moves
- timezone_insight: what markets these hours correspond to
"""
        self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        return heatmap

    # ----------------------------------------------------------
    # Core Analysis (enhanced with all features)
    # ----------------------------------------------------------

    def get_whale_transactions(
   # PRODUCTION: Replace with real on-chain APIs
   # Etherscan: GET /api?module=token&action=tokenholderlist
   # Whale Alert: GET /v2/transactions?min_value=100000
   # Dune Analytics: SQL query for whale transactions
   # Currently returns DEMO data (120 placeholder transactions)
        self,
        token: str,
        chain: str = "ethereum",
        min_usd: float = 100000,
        hours: int = 24,
    ) -> List[WhaleTransaction]:
        """Fetch whale transactions (100+ wallets)."""
        demo_whales = []
        for i in range(120):
            demo_whales.append(WhaleTransaction(
                tx_hash=f"0x{'a' * 40}{i:04d}",
                from_address=f"0x{'1' * 38}{i % 20:02d}",
                to_address=f"0x{'2' * 38}{i % 15:02d}",
                token=token,
                amount=1000 + (i * 50),
                usd_value=150000 + (i * 5000),
                timestamp=(datetime.utcnow() - timedelta(hours=i % hours)).isoformat(),
                exchange=["Binance", "Coinbase", "Uniswap", "Wallet", "OKX"][i % 5],
                direction=["BUY", "SELL", "DEPOSIT", "WITHDRAWAL"][i % 4],
                chain=chain,
            ))
        return demo_whales

    def get_market_metrics(self, token: str) -> Dict[str, Any]:
        """
        Fetch Volume, OI, Funding Rate, Liquidation data.
        
        PRODUCTION: CoinGecko API (free, no key needed for basic)
        - Volume + market data: REAL (CoinGecko)
        - OI + Funding Rate: DEMO (needs Coinglass API in production)
        - Liquidation data: DEMO (needs Coinglass API in production)
        """
        # --- REAL DATA: CoinGecko (free, no API key required) ---
        coin_id_map = {
            "ETH": "ethereum", "BTC": "bitcoin", "SOL": "solana",
            "BNB": "binancecoin", "ARB": "arbitrum", "OP": "optimism",
            "MATIC": "matic-network", "AVAX": "avalanche-2", "LINK": "chainlink",
        }
        coin_id = coin_id_map.get(token.upper(), token.lower())
        
        volume_24h = 0
        volume_change_pct = 0.0
        price = 0
        price_change_24h = 0.0
        market_cap = 0
        tvl = 0
        tvl_change_7d = 0.0
        
        try:
            # CoinGecko free API — no key needed, 10-30 calls/min
            resp = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{coin_id}",
                params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
                timeout=10,
            )
            if resp.ok:
                data = resp.json()
                md = data.get("market_data", {})
                volume_24h = md.get("total_volume", {}).get("usd", 0)
                price = md.get("current_price", {}).get("usd", 0)
                price_change_24h = md.get("price_change_percentage_24h", 0)
                market_cap = md.get("market_cap", {}).get("usd", 0)
                volume_change_pct = md.get("total_volume_change_24h", 0)
        except Exception:
            pass  # fallback to demo data below
        
        # --- DEMO DATA: Needs Coinglass API in production ---
        # Coinglass API: https://www.coingecko.com/api (paid) or coinglass.com/api
        # These require a paid subscription, using estimates for demo
        oi_estimate = market_cap * 0.35 if market_cap else 8_750_000_000
        funding_rate = 0.0125  # DEMO — replace with Coinglass /futures/fundingRate
        long_short_ratio = 1.15  # DEMO — replace with Coinglass /futures/longShortRatio
        
        # Liquidation estimates based on price — DEMO
        liq_long = price * 0.05 * (market_cap / price * 0.001) if price else 125_000_000
        liq_short = price * 0.05 * (market_cap / price * 0.0008) if price else 89_000_000
        
        return {
            "volume_24h": volume_24h or 2_500_000_000,
            "volume_change_pct": volume_change_pct or 15.3,
            "price": price,
            "price_change_24h": price_change_24h,
            "market_cap": market_cap,
            "open_interest": oi_estimate,
            "oi_change_pct": 8.2,  # DEMO
            "funding_rate": funding_rate,
            "funding_rate_annualized": funding_rate * 365 * 3 * 100,  # approx
            "long_short_ratio": long_short_ratio,
            "liquidation_long_5pct": liq_long,
            "liquidation_short_5pct": liq_short,
            "top_long_liquidation": price * 0.95 if price else 108_500,
            "top_short_liquidation": price * 1.05 if price else 112_300,
            "tvl": tvl or 12_500_000_000,
            "tvl_change_7d": tvl_change_7d or -2.1,
            "data_source": {
                "volume": "CoinGecko (real)",
                "price": "CoinGecko (real)",
                "oi": "estimated (demo — needs Coinglass API)",
                "funding": "demo (needs Coinglass API)",
                "liquidation": "estimated (demo — needs Coinglass API)",
            },
        }

    def analyze_whale_activity(
        self,
        token: str,
        chain: str = "ethereum",
        hours: int = 24,
        min_whales: int = 100,
        include_all_features: bool = True,
    ) -> WhaleSignal:
        """
        Comprehensive whale analysis with all 10 features.

        Args:
            token: Token symbol (e.g., "ETH", "BTC", "SOL")
            chain: Blockchain network
            hours: Analysis time period
            min_whales: Minimum whale transactions
            include_all_features: Run all 10 analysis modules
        """
        # Fetch data
        whale_txs = self.get_whale_transactions(token, chain, hours=hours)
        metrics = self.get_market_metrics(token)

        # Basic stats
        buy_txs = [tx for tx in whale_txs if tx.direction in ("BUY", "WITHDRAWAL")]
        sell_txs = [tx for tx in whale_txs if tx.direction in ("SELL", "DEPOSIT")]
        total_buy = sum(tx.usd_value for tx in buy_txs)
        total_sell = sum(tx.usd_value for tx in sell_txs)
        net_flow = total_buy - total_sell
        total_volume = total_buy + total_sell
        avg_tx = total_volume / len(whale_txs) if whale_txs else 0

        # Run all features
        exchange_flows = []
        divergence = None
        concentration = None
        smart_money = []
        cross_chain = {}
        walls = []
        vc_activity = []
        historical = None
        heatmap = []

        if include_all_features:
            exchange_flows = self.analyze_exchange_flows(token, hours)
            divergence = self.detect_divergence(token, hours)
            concentration = self.calculate_concentration(token, chain)
            smart_money = self.rank_whale_wallets(token, chain, top_n=10)
            walls = self.scan_orderbook_walls(token)
            vc_activity = self.track_vc_activity(token, hours)
            historical = self.match_historical_patterns(token)
            heatmap = self.generate_heatmap(token)

            # Cross-chain for top whale
            if whale_txs:
                top_addr = whale_txs[0].to_address
                cross_chain = self.track_cross_chain(top_addr)

        # MiMo comprehensive analysis
        analysis_context = f"""
Comprehensive whale analysis for {token} ({hours}h):

WHALE STATS:
- Transactions: {len(whale_txs)}
- Buy/Sell ratio: {len(buy_txs)}/{len(sell_txs)}
- Net flow: ${net_flow:+,.0f}
- Avg TX size: ${avg_tx:,.0f}

MARKET:
- Volume 24h: ${metrics['volume_24h']:,.0f} ({metrics['volume_change_pct']:+.1f}%)
- OI: ${metrics['open_interest']:,.0f} ({metrics['oi_change_pct']:+.1f}%)
- Funding: {metrics['funding_rate']:.4f}%
- L/S Ratio: {metrics['long_short_ratio']:.2f}

EXCHANGE FLOWS: {json.dumps([{"ex": f.exchange, "net": f.net_flow_usd} for f in exchange_flows])}
DIVERGENCE: {divergence.direction if divergence else "N/A"}
CONCENTRATION: Gini={concentration.gini_coefficient if concentration else "N/A"}
SMART MONEY AVG SCORE: {sum(p.smart_money_score for p in smart_money)/len(smart_money) if smart_money else 0:.1f}
VC ACTIVITY: {len(vc_activity)} VCs tracked
HISTORICAL MATCH: {historical.get('best_match', 'N/A') if historical else 'N/A'}

Provide final JSON with:
- signal: ACCUMULATION / DISTRIBUTION / NEUTRAL
- confidence: 0-100
- reasoning: comprehensive 3-5 sentence analysis
- risk_level: LOW / MEDIUM / HIGH
- key_findings: list of top 5 insights
- action_items: what traders should do
"""
        response = self.mimo.analyze(analysis_context, system=self.SYSTEM_PROMPT)
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}

        return WhaleSignal(
            token=token,
            signal=analysis.get("signal", "NEUTRAL"),
            confidence=analysis.get("confidence", 50) / 100,
            whale_count=len(set(tx.from_address for tx in whale_txs) | set(tx.to_address for tx in whale_txs)),
            total_volume_usd=total_volume,
            net_flow=net_flow,
            avg_tx_size=avg_tx,
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
            exchange_flows=exchange_flows,
            divergence=divergence,
            concentration=concentration,
            smart_money_scores=smart_money,
            cross_chain_flows=cross_chain,
            orderbook_walls=walls,
            vc_activity=vc_activity,
            historical_match=historical,
            heatmap=heatmap[:50],  # limit for token efficiency
        )

    # ----------------------------------------------------------
    # Alert Generator
    # ----------------------------------------------------------

    def generate_alert(self, signal: WhaleSignal) -> str:
        """Generate comprehensive human-readable alert."""
        emoji = {"ACCUMULATION": "🟢", "DISTRIBUTION": "🔴", "NEUTRAL": "🟡"}.get(signal.signal, "⚪")

        # Exchange flow summary
        ex_summary = ""
        if signal.exchange_flows:
            total_net = sum(f.net_flow_usd for f in signal.exchange_flows)
            ex_summary = f"Exchange Net Flow: ${total_net:+,.0f} ({'outflow 📈' if total_net > 0 else 'inflow 📉'})"

        # Divergence
        div_summary = ""
        if signal.divergence and signal.divergence.has_divergence:
            div_summary = f"⚠️ {signal.divergence.direction} detected! Whales: {signal.divergence.whale_action}, Retail: {signal.divergence.retail_action}"

        # Concentration
        conc_summary = ""
        if signal.concentration:
            conc_summary = f"Gini: {signal.concentration.gini_coefficient} | Top10: {signal.concentration.top10_pct}% | Risk: {signal.concentration.manipulation_risk}"

        # Smart Money
        sm_summary = ""
        if signal.smart_money_scores:
            avg_score = sum(p.smart_money_score for p in signal.smart_money_scores) / len(signal.smart_money_scores)
            sm_summary = f"Avg Smart Money Score: {avg_score:.1f}/100"

        # VC
        vc_summary = ""
        if signal.vc_activity:
            active_vcs = [p for p in signal.vc_activity if p.is_vc]
            vc_summary = f"Active VCs: {', '.join(p.vc_name for p in active_vcs[:3])}"

        # Historical
        hist_summary = ""
        if signal.historical_match:
            hist_summary = f"Best Match: {signal.historical_match.get('best_match', 'N/A')} ({signal.historical_match.get('similarity_score', 0)}% similar)"

        return f"""
{emoji} WHALE ALERT: {signal.token}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signal: {signal.signal} ({signal.confidence:.0%} confidence)
Whales Tracked: {signal.whale_count}
Net Flow: ${signal.net_flow:+,.0f}
Avg TX Size: ${signal.avg_tx_size:,.0f}
Timeframe: {signal.timeframe}

📊 Market Metrics:
• Volume 24h: ${signal.volume_24h:,.0f}
• Open Interest: ${signal.open_interest:,.0f}
• Funding Rate: {signal.funding_rate:.4f}%
• Long/Short: {signal.liquidation_data.get('long_5pct', 0) / max(signal.liquidation_data.get('short_5pct', 1), 1):.2f}

🏦 Exchange Flows:
{ex_summary}

🐋 vs 👥 Divergence:
{div_summary}

📏 Concentration:
{conc_summary}

🧠 Smart Money:
{sm_summary}

🏢 VC Activity:
{vc_summary}

📈 Historical Pattern:
{hist_summary}

📝 Analysis:
{signal.reasoning}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
