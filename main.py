#!/usr/bin/env python3
"""
MiMo Crypto Intelligence Agent
Command-line interface for crypto analysis powered by Xiaomi MiMo-V2.5-Pro

Usage:
    python main.py analyze bitcoin
    python main.py sentiment "BTC ETH SOL"
    python main.py whale ethereum
    python main.py whale --divergence ETH
    python main.py whale --concentration ETH
    python main.py whale --heatmap ETH
    python main.py whale --vc-tracking ETH
    python main.py whale --smart-money ETH
    python main.py whale --exchange-flows ETH
    python main.py whale --cross-chain 0x1234...
    python main.py whale --orderbook ETH
    python main.py whale --historical ETH
    python main.py whale --alert ETH --min-usd 500000
    python main.py audit contract.sol
    python main.py demo
"""

import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mimo_client import MiMoClient, MiMoConfig
from src.market_intelligence import MarketIntelligence
from src.sentiment_analyzer import SentimentAnalyzer
from src.airdrop_detector import AirdropDetector
from src.contract_analyzer import ContractAnalyzer
from src.whale_tracker import WhaleTracker

console = Console()


def print_banner():
    """Print agent banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║   🤖 MiMo Crypto Intelligence Agent v1.0                 ║
║   Powered by Xiaomi MiMo-V2.5-Pro                        ║
║   100T Token Creator Incentive Program                    ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(Panel(banner, style="bold cyan"))


def cmd_analyze(args):
    """Analyze a crypto asset."""
    client = MiMoClient()
    market = MarketIntelligence(client)

    console.print(f"\n🔍 Analyzing [bold]{args.asset}[/bold]...\n")

    with console.status("[bold green]MiMo is thinking..."):
        signal = market.analyze_asset(args.asset)

    table = Table(title=f"📊 {signal.asset.upper()} Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    signal_color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(signal.signal, "white")

    table.add_row("Signal", f"[{signal_color}]{signal.signal}[/{signal_color}]")
    table.add_row("Confidence", f"{signal.confidence:.0%}")
    table.add_row("Risk Level", signal.risk_level)
    table.add_row("Timeframe", signal.timeframe)
    table.add_row("Timestamp", signal.timestamp)

    console.print(table)
    console.print(f"\n📝 [bold]Reasoning:[/bold]\n{signal.reasoning}\n")


def cmd_sentiment(args):
    """Analyze market sentiment."""
    client = MiMoClient()
    analyzer = SentimentAnalyzer(client)

    demo_texts = [
        "Bitcoin just broke $100k! Institutional adoption is massive.",
        "Ethereum gas fees are at historic lows, DeFi is booming.",
        "Major bank announces crypto custody services for clients.",
        "Regulatory clarity improving in US and EU markets.",
        "On-chain metrics show accumulation by long-term holders.",
    ]

    console.print(f"\n📰 Analyzing sentiment for [bold]{args.query}[/bold]...\n")

    with console.status("[bold green]MiMo is analyzing sentiment..."):
        result = analyzer.analyze_texts(demo_texts, asset=args.query)

    score_color = "green" if result.overall_score > 0 else "red" if result.overall_score < 0 else "yellow"

    panel_content = f"""
**Asset:** {result.asset}
**Sentiment:** [{score_color}]{result.label}[/{score_color}] ({result.overall_score:+.2f})
**Sources Analyzed:** {result.sources_analyzed}

**Narrative:** {result.narrative}

**Key Themes:** {', '.join(result.key_themes)}

**Bullish Catalysts:**
{chr(10).join(f'  ✅ {c}' for c in result.bullish_catalysts)}

**FUD Factors:**
{chr(10).join(f'  ⚠️ {f}' for f in result.fud_factors)}
"""

    console.print(Panel(Markdown(panel_content), title="📊 Sentiment Analysis", border_style="blue"))


def cmd_whale(args):
    """Whale tracker with 10 advanced features."""
    client = MiMoClient()
    tracker = WhaleTracker(client)
    token = args.token.upper()

    # Determine which feature to run
    if args.divergence:
        console.print(f"\n🐋 vs 👥 Divergence Analysis: [bold]{token}[/bold]\n")
        with console.status("[bold green]Detecting divergence..."):
            div = tracker.detect_divergence(token, hours=args.hours)

        emoji = "🟢" if div.direction == "BULLISH_DIVERGENCE" else "🔴" if div.direction == "BEARISH_DIVERGENCE" else "⚪"
        console.print(f"{emoji} Direction: [bold]{div.direction}[/bold]")
        console.print(f"   Whales: {div.whale_action} | Retail: {div.retail_action}")
        console.print(f"   Strength: {div.strength:.0%}")
        console.print(f"   📝 {div.reasoning}\n")

    elif args.concentration:
        console.print(f"\n📏 Concentration Analysis: [bold]{token}[/bold]\n")
        with console.status("[bold green]Calculating Gini coefficient..."):
            conc = tracker.calculate_concentration(token)

        risk_color = {"CRITICAL": "red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(conc.manipulation_risk, "white")

        table = Table(title=f"📏 Holder Concentration: {token}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Gini Coefficient", f"{conc.gini_coefficient:.4f}")
        table.add_row("Top 10 Holders", f"{conc.top10_pct}%")
        table.add_row("Top 50 Holders", f"{conc.top50_pct}%")
        table.add_row("Top 100 Holders", f"{conc.top100_pct}%")
        table.add_row("Total Holders", f"{conc.total_holders:,}")
        table.add_row("Manipulation Risk", f"[{risk_color}]{conc.manipulation_risk}[/{risk_color}]")
        console.print(table)
        console.print()

    elif args.heatmap:
        console.print(f"\n🌡️ Sentiment Heatmap: [bold]{token}[/bold]\n")
        with console.status("[bold green]Generating heatmap..."):
            heatmap = tracker.generate_heatmap(token, days=7)

        # Show top 5 most active hours
        from collections import defaultdict
        hour_avg = defaultdict(list)
        for entry in heatmap:
            hour_avg[entry.hour].append(entry.activity_score)

        sorted_hours = sorted(hour_avg.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)

        table = Table(title=f"🌡️ Whale Activity Heatmap: {token}")
        table.add_column("Hour (UTC)", style="cyan")
        table.add_column("Activity Score", style="green")
        table.add_column("Avg Net Flow", style="yellow")

        for hour, scores in sorted_hours[:10]:
            avg_score = sum(scores) / len(scores)
            flows = [e.net_flow_usd for e in heatmap if e.hour == hour]
            avg_flow = sum(flows) / len(flows) if flows else 0
            bar = "█" * int(avg_score * 20)
            console.print(f"  {hour:02d}:00  {bar} {avg_score:.2f}  ${avg_flow:+,.0f}")
        console.print()

    elif args.vc_tracking:
        console.print(f"\n🏢 VC Activity Tracking: [bold]{token}[/bold]\n")
        with console.status("[bold green]Tracking VC wallets..."):
            vcs = tracker.track_vc_activity(token, hours=args.hours)

        table = Table(title=f"🏢 VC Wallets Tracking: {token}")
        table.add_column("VC Name", style="cyan")
        table.add_column("Smart Money", style="green")
        table.add_column("Win Rate", style="yellow")
        table.add_column("PnL", style="white")
        for vc in vcs[:5]:
            table.add_row(vc.vc_name, f"{vc.smart_money_score:.0f}", f"{vc.win_rate:.0%}", f"${vc.total_pnl_usd:,.0f}")
        console.print(table)
        console.print()

    elif args.smart_money:
        console.print(f"\n🧠 Smart Money Ranking: [bold]{token}[/bold]\n")
        with console.status("[bold green]Ranking whale wallets..."):
            profiles = tracker.rank_whale_wallets(token, top_n=10)

        table = Table(title=f"🧠 Top Smart Money Wallets: {token}")
        table.add_column("#", style="dim")
        table.add_column("Address", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Win Rate", style="yellow")
        table.add_column("ROI", style="white")
        table.add_column("PnL", style="white")
        for i, p in enumerate(profiles, 1):
            table.add_row(str(i), f"{p.address[:12]}...", f"{p.smart_money_score:.0f}", f"{p.win_rate:.0%}", f"{p.avg_roi:.1f}%", f"${p.total_pnl_usd:,.0f}")
        console.print(table)
        console.print()

    elif args.exchange_flows:
        console.print(f"\n🏦 Exchange Flows: [bold]{token}[/bold]\n")
        with console.status("[bold green]Analyzing exchange flows..."):
            flows = tracker.analyze_exchange_flows(token, hours=args.hours)

        table = Table(title=f"🏦 Exchange Flow Analysis: {token}")
        table.add_column("Exchange", style="cyan")
        table.add_column("Inflow", style="red")
        table.add_column("Outflow", style="green")
        table.add_column("Net Flow", style="white")
        table.add_column("TXs", style="dim")
        for f in flows:
            net_color = "green" if f.net_flow_usd > 0 else "red"
            table.add_row(f.exchange, f"${f.inflow_usd:,.0f}", f"${f.outflow_usd:,.0f}", f"[{net_color}]${f.net_flow_usd:+,.0f}[/{net_color}]", str(f.tx_count))
        console.print(table)
        console.print()

    elif args.cross_chain:
        address = args.cross_chain
        console.print(f"\n🔗 Cross-Chain Tracking: [bold]{address[:10]}...[/bold]\n")
        with console.status("[bold green]Scanning chains..."):
            result = tracker.track_cross_chain(address)

        if "balances" in result:
            table = Table(title=f"🔗 Cross-Chain Balances")
            table.add_column("Chain", style="cyan")
            table.add_column("Balance", style="green")
            table.add_column("Recent TXs", style="yellow")
            table.add_column("Net Flow", style="white")
            for chain, data in result["balances"].items():
                net_color = "green" if data["net_flow"] > 0 else "red"
                table.add_row(chain, f"${data['balance_usd']:,.0f}", str(data["recent_txs"]), f"[{net_color}]${data['net_flow']:+,.0f}[/{net_color}]")
            console.print(table)
        console.print(f"  Primary Chain: {result.get('primary_chain', 'N/A')}")
        console.print(f"  Bridge Detected: {result.get('bridge_detected', False)}")
        console.print()

    elif args.orderbook:
        console.print(f"\n📊 Order Book Walls: [bold]{token}[/bold]\n")
        with console.status("[bold green]Scanning order books..."):
            walls = tracker.scan_orderbook_walls(token)

        table = Table(title=f"📊 Order Book Walls: {token}")
        table.add_column("Exchange", style="cyan")
        table.add_column("Side", style="white")
        table.add_column("Price", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Spoof Risk", style="red")
        for w in walls:
            spoof = "⚠️ YES" if w.is_spoofing_risk else "✅ No"
            side_color = "green" if w.side == "BID" else "red"
            table.add_row(w.exchange, f"[{side_color}]{w.side}[/{side_color}]", f"${w.price:,.2f}", f"${w.size_usd:,.0f}", spoof)
        console.print(table)
        console.print()

    elif args.historical:
        console.print(f"\n📈 Historical Pattern Matching: [bold]{token}[/bold]\n")
        with console.status("[bold green]Matching patterns..."):
            result = tracker.match_historical_patterns(token)

        console.print(f"  Best Match: [bold]{result.get('best_match', 'N/A')}[/bold]")
        console.print(f"  Similarity: {result.get('similarity_score', 0)}%")
        console.print(f"  Historical Outcome: {result.get('outcome_after_match', 'N/A')}")
        console.print(f"  Prediction: {result.get('prediction', 'N/A')}")
        console.print(f"  Confidence: {result.get('confidence', 0)}%")
        console.print()

    elif args.alert:
        min_usd = args.min_usd or 500000
        rule = tracker.add_alert_rule(token, min_usd=min_usd, direction=args.alert_direction or "ANY")
        console.print(f"\n🔔 Alert Rule Created!")
        console.print(f"   Token: {token}")
        console.print(f"   Min USD: ${min_usd:,.0f}")
        console.print(f"   Direction: {rule.direction}")
        console.print(f"   Rule ID: {rule.rule_id}")
        console.print()

    else:
        # Default: full whale analysis
        console.print(f"\n🐋 Full Whale Analysis: [bold]{token}[/bold]\n")
        with console.status("[bold green]Running all 10 whale features..."):
            signal = tracker.analyze_whale_activity(token, hours=args.hours, include_all_features=True)

        console.print(tracker.generate_alert(signal))


def cmd_audit(args):
    """Audit a smart contract."""
    client = MiMoClient()
    analyzer = ContractAnalyzer(client)

    if args.file and Path(args.file).exists():
        contract_code = Path(args.file).read_text()
        contract_name = Path(args.file).stem
    else:
        contract_code = '''
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
        balances[msg.sender] -= amount;
    }
}
'''
        contract_name = "VulnerableBank (Demo)"

    console.print(f"\n🔍 Auditing [bold]{contract_name}[/bold]...\n")

    with console.status("[bold green]MiMo is auditing..."):
        audit = analyzer.analyze_contract(contract_code, contract_name)

    risk_color = {"CRITICAL": "red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(audit.overall_risk, "white")

    table = Table(title=f"🛡️ Security Audit: {audit.contract_name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Overall Risk", f"[{risk_color}]{audit.overall_risk}[/{risk_color}]")
    table.add_row("Security Score", f"{audit.score}/100")
    table.add_row("Vulnerabilities", str(len(audit.vulnerabilities)))
    table.add_row("Gas Optimizations", str(len(audit.gas_optimizations)))

    console.print(table)

    if audit.vulnerabilities:
        console.print("\n⚠️ [bold red]Vulnerabilities Found:[/bold red]")
        for i, vuln in enumerate(audit.vulnerabilities, 1):
            console.print(f"\n  [{i}] [{risk_color}]{vuln.severity}[/{risk_color}] - {vuln.type}")
            console.print(f"      {vuln.description}")
            console.print(f"      💡 {vuln.recommendation}")

    console.print(f"\n📝 [bold]Summary:[/bold]\n{audit.summary}\n")


def cmd_demo(args):
    """Run interactive demo."""
    print_banner()

    client = MiMoClient()

    console.print("[bold]Running MiMo Crypto Agent Demo...[/bold]\n")

    # 1. MiMo connection
    console.print("1️⃣ [bold cyan]Testing MiMo-V2.5-Pro connection...[/bold cyan]")
    with console.status("[bold green]Connecting to MiMo API..."):
        response = client.analyze(
            "What makes Xiaomi MiMo-V2.5-Pro suitable for crypto analysis? Answer in 2-3 sentences.",
            system="You are a helpful AI assistant. Be concise."
        )
    console.print(f"   ✅ MiMo says: {response[:200]}...\n")

    # 2. Market Analysis
    console.print("2️⃣ [bold cyan]Market Analysis Demo (Bitcoin)[/bold cyan]")
    market = MarketIntelligence(client)
    with console.status("[bold green]Analyzing BTC..."):
        signal = market.analyze_asset("bitcoin")
    console.print(f"   📊 Signal: {signal.signal} | Confidence: {signal.confidence:.0%}")
    console.print(f"   💡 {signal.reasoning[:150]}...\n")

    # 3. Whale Tracker (all 10 features)
    console.print("3️⃣ [bold cyan]Whale Tracker - All 10 Features (ETH)[/bold cyan]")
    whale = WhaleTracker(client)
    with console.status("[bold green]Running all whale features..."):
        ws = whale.analyze_whale_activity("ETH", hours=24, include_all_features=True)
    console.print(f"   🐋 Signal: {ws.signal} | Whales: {ws.whale_count}")
    console.print(f"   💰 Net Flow: ${ws.net_flow:+,.0f}")
    console.print(f"   📊 Volume: ${ws.volume_24h:,.0f} | OI: ${ws.open_interest:,.0f} | Funding: {ws.funding_rate:.4f}%")
    if ws.divergence:
        console.print(f"   🐋 vs 👥 Divergence: {ws.divergence.direction}")
    if ws.concentration:
        console.print(f"   📏 Gini: {ws.concentration.gini_coefficient} | Risk: {ws.concentration.manipulation_risk}")
    if ws.smart_money_scores:
        avg_sm = sum(p.smart_money_score for p in ws.smart_money_scores) / len(ws.smart_money_scores)
        console.print(f"   🧠 Smart Money Avg: {avg_sm:.1f}/100")
    console.print(f"   💡 {ws.reasoning[:150]}...\n")

    # 4. Contract Audit
    console.print("4️⃣ [bold cyan]Smart Contract Audit Demo[/bold cyan]")
    analyzer = ContractAnalyzer(client)
    demo_contract = """
    pragma solidity ^0.8.0;
    contract SimpleToken {
        mapping(address => uint256) public balance;
        function transfer(address to, uint256 amount) public {
            require(balance[msg.sender] >= amount);
            balance[msg.sender] -= amount;
            balance[to] += amount;
        }
    }
    """
    with console.status("[bold green]Auditing contract..."):
        audit = analyzer.analyze_contract(demo_contract, "SimpleToken")
    console.print(f"   🛡️ Risk: {audit.overall_risk} | Score: {audit.score}/100")
    console.print(f"   ⚠️ Issues: {len(audit.vulnerabilities)}\n")

    console.print("[bold green]✅ Demo complete! All 10 whale features operational.[/bold green]")
    console.print("\n[dim]Run with --help to see all available commands.[/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="MiMo Crypto Intelligence Agent - AI-powered crypto analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    p_analyze = subparsers.add_parser("analyze", help="Analyze a crypto asset")
    p_analyze.add_argument("asset", help="Coin ID (e.g., bitcoin, ethereum)")
    p_analyze.set_defaults(func=cmd_analyze)

    # Sentiment command
    p_sentiment = subparsers.add_parser("sentiment", help="Analyze market sentiment")
    p_sentiment.add_argument("query", help="Asset or topic to analyze")
    p_sentiment.set_defaults(func=cmd_sentiment)

    # Whale command (with 10 sub-features)
    p_whale = subparsers.add_parser("whale", help="Whale tracker (10 features)")
    p_whale.add_argument("token", help="Token symbol (e.g., ETH, BTC, SOL)")
    p_whale.add_argument("--hours", type=int, default=24, help="Analysis period in hours")
    p_whale.add_argument("--divergence", action="store_true", help="Whale vs Retail divergence")
    p_whale.add_argument("--concentration", action="store_true", help="Holder concentration (Gini)")
    p_whale.add_argument("--heatmap", action="store_true", help="Activity heatmap by hour/day")
    p_whale.add_argument("--vc-tracking", action="store_true", help="Track VC wallets")
    p_whale.add_argument("--smart-money", action="store_true", help="Smart Money wallet ranking")
    p_whale.add_argument("--exchange-flows", action="store_true", help="Exchange inflow/outflow")
    p_whale.add_argument("--cross-chain", type=str, help="Track wallet across chains")
    p_whale.add_argument("--orderbook", action="store_true", help="Order book wall detection")
    p_whale.add_argument("--historical", action="store_true", help="Historical pattern matching")
    p_whale.add_argument("--alert", action="store_true", help="Create alert rule")
    p_whale.add_argument("--min-usd", type=float, help="Min USD for alert")
    p_whale.add_argument("--alert-direction", choices=["BUY", "SELL", "ANY"], default="ANY", help="Alert direction filter")
    p_whale.set_defaults(func=cmd_whale)

    # Audit command
    p_audit = subparsers.add_parser("audit", help="Audit a smart contract")
    p_audit.add_argument("file", nargs="?", help="Solidity file to audit")
    p_audit.set_defaults(func=cmd_audit)

    # Demo command
    p_demo = subparsers.add_parser("demo", help="Run interactive demo")
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
