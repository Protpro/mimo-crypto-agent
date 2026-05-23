"""
Sentiment Analyzer Module
Social media & news sentiment analysis powered by MiMo-V2.5-Pro
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

from .mimo_client import MiMoClient


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    asset: str
    overall_score: float  # -1 to 1
    label: str  # VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH
    sources_analyzed: int
    key_themes: List[str]
    narrative: str
    fud_factors: List[str]
    bullish_catalysts: List[str]
    timestamp: str


class SentimentAnalyzer:
    """
    AI-powered sentiment analysis using MiMo's natural language understanding.
    
    Analyzes social media posts, news articles, and community discussions
    to gauge market sentiment for crypto assets.
    """
    
    SYSTEM_PROMPT = """You are an expert sentiment analyst for cryptocurrency markets.
Your job is to analyze text data and determine market sentiment.

Analyze the provided text and output JSON with:
1. overall_score: float from -1 (very bearish) to 1 (very bullish)
2. label: one of VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH
3. key_themes: list of main topics/themes found
4. narrative: 2-3 sentence summary of the current narrative
5. fud_factors: list of fear/uncertainty/doubt elements
6. bullish_catalysts: list of positive catalysts
7. confidence: 0-100 how confident in this assessment"""
    
    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
    
    def analyze_texts(
        self,
        texts: List[str],
        asset: str = "crypto market",
    ) -> SentimentResult:
        """
        Analyze a collection of texts for sentiment.
        
        Args:
            texts: List of text strings (tweets, news, posts)
            asset: The crypto asset being analyzed
            
        Returns:
            SentimentResult with detailed sentiment breakdown
        """
        # Combine texts with indices for reference
        combined = "\n---\n".join(
            f"[Source {i+1}]: {text[:500]}" for i, text in enumerate(texts[:20])
        )
        
        prompt = f"""
Analyze the sentiment of these {len(texts)} sources about {asset}:

{combined}

Provide a JSON sentiment analysis.
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            analysis = json.loads(json_match.group()) if json_match else {}
        
        # Map score to label if not provided
        score = analysis.get("overall_score", 0)
        if "label" not in analysis:
            if score < -0.6:
                label = "VERY_BEARISH"
            elif score < -0.2:
                label = "BEARISH"
            elif score < 0.2:
                label = "NEUTRAL"
            elif score < 0.6:
                label = "BULLISH"
            else:
                label = "VERY_BULLISH"
        else:
            label = analysis["label"]
        
        return SentimentResult(
            asset=asset,
            overall_score=score,
            label=label,
            sources_analyzed=len(texts),
            key_themes=analysis.get("key_themes", []),
            narrative=analysis.get("narrative", ""),
            fud_factors=analysis.get("fud_factors", []),
            bullish_catalysts=analysis.get("bullish_catalysts", []),
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def analyze_news_batch(self, news_items: List[Dict[str, str]]) -> SentimentResult:
        """
        Analyze a batch of news articles.
        
        Args:
            news_items: List of {"title": str, "summary": str, "source": str}
        """
        texts = [
            f"{item.get('title', '')}: {item.get('summary', '')}"
            for item in news_items
        ]
        return self.analyze_texts(texts, asset="crypto market")
    
    def detect_narrative_shift(
        self,
        current_texts: List[str],
        historical_texts: List[str],
        asset: str = "crypto market",
    ) -> Dict[str, Any]:
        """
        Detect shifts in market narrative between two time periods.
        
        Uses MiMo's reasoning to identify changing sentiment patterns.
        """
        prompt = f"""
Compare these two sets of market discussions about {asset} and identify any narrative shifts:

=== CURRENT PERIOD ({len(current_texts)} sources) ===
{chr(10).join(f"- {t[:300]}" for t in current_texts[:10])}

=== HISTORICAL PERIOD ({len(historical_texts)} sources) ===
{chr(10).join(f"- {t[:300]}" for t in historical_texts[:10])}

Analyze the shift in narrative and output JSON with:
1. shift_detected: boolean
2. direction: "bullish_shift", "bearish_shift", or "neutral"
3. magnitude: 1-10 how significant the shift
4. key_changes: list of what changed
5. implications: what this means for the asset
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"shift_detected": False}
