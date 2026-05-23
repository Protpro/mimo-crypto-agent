#!/usr/bin/env python3
"""
MiMo Crypto Intelligence Agent
Command-line interface for crypto analysis powered by Xiaomi MiMo-V2.5-Pro

Usage:
    python main.py analyze bitcoin
    python main.py sentiment "BTC ETH SOL"
    python main.py airdrop --scan
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
    
    # Display results
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
    
    # Demo texts (in production, fetch from Twitter/News API)
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
    
    # Display results
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


def cmd_audit(args):
    """Audit a smart contract."""
    client = MiMoClient()
    analyzer = ContractAnalyzer(client)
    
    # Read contract file or use demo
    if args.file and Path(args.file).exists():
        contract_code = Path(args.file).read_text()
        contract_name = Path(args.file).stem
    else:
        # Demo contract
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
    
    # Display results
    risk_color = {
        "CRITICAL": "red",
        "HIGH": "red",
        "MEDIUM": "yellow",
        "LOW": "green",
    }.get(audit.overall_risk, "white")
    
    table = Table(title=f"🛡️ Security Audit: {audit.contract_name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Overall Risk", f"[{risk_color}]{audit.overall_risk}[/{risk_color}]")
    table.add_row("Security Score", f"{audit.score}/100")
    table.add_row("Vulnerabilities", str(len(audit.vulnerabilities)))
    table.add_row("Gas Optimizations", str(len(audit.gas_optimizations)))
    
    console.print(table)
    
    # Show vulnerabilities
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
    
    # 1. Simple MiMo query
    console.print("1️⃣ [bold cyan]Testing MiMo-V2.5-Pro connection...[/bold cyan]")
    with console.status("[bold green]Connecting to MiMo API..."):
        response = client.analyze(
            "What makes Xiaomi MiMo-V2.5-Pro suitable for crypto analysis? Answer in 2-3 sentences.",
            system="You are a helpful AI assistant. Be concise."
        )
    console.print(f"   ✅ MiMo says: {response[:200]}...\n")
    
    # 2. Market Analysis Demo
    console.print("2️⃣ [bold cyan]Market Analysis Demo (Bitcoin)[/bold cyan]")
    market = MarketIntelligence(client)
    with console.status("[bold green]Analyzing BTC..."):
        signal = market.analyze_asset("bitcoin")
    console.print(f"   📊 Signal: {signal.signal} | Confidence: {signal.confidence:.0%}")
    console.print(f"   💡 {signal.reasoning[:150]}...\n")
    
    # 3. Contract Audit Demo
    console.print("3️⃣ [bold cyan]Smart Contract Audit Demo[/bold cyan]")
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
    
    console.print("[bold green]✅ Demo complete! MiMo Crypto Agent is working.[/bold green]")
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
