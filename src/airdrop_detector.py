"""
Airdrop Opportunity Detector
AI-powered airdrop farming intelligence using MiMo-V2.5-Pro
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .mimo_client import MiMoClient


@dataclass
class AirdropOpportunity:
    """Detected airdrop opportunity."""
    project: str
    chain: str
    estimated_value: str
    probability: str  # HIGH, MEDIUM, LOW
    requirements: List[str]
    deadline: Optional[str]
    risk_level: str
    action_steps: List[str]
    reasoning: str
    sources: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AirdropDetector:
    """
    AI-powered airdrop opportunity detection.
    
    Uses MiMo-V2.5-Pro's reasoning to analyze on-chain patterns,
    project announcements, and historical airdrop data to identify
    potential airdrop opportunities before they happen.
    """
    
    SYSTEM_PROMPT = """You are an expert airdrop analyst in the crypto/Web3 space.
You analyze project funding, testnet activity, governance participation,
and historical patterns to predict potential airdrops.

For each opportunity, provide JSON with:
1. project: project name
2. chain: blockchain network
3. estimated_value: expected airdrop value range
4. probability: HIGH (confirmed/likely), MEDIUM (possible), LOW (speculative)
5. requirements: list of actions needed to qualify
6. deadline: when to act by (if known)
7. risk_level: LOW, MEDIUM, HIGH
8. action_steps: step-by-step guide
9. reasoning: why this airdrop is likely
10. sources: where this info comes from"""
    
    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
    
    def analyze_project(self, project_info: str) -> AirdropOpportunity:
        """
        Analyze a specific project for airdrop potential.
        
        Args:
            project_info: Description of the project, funding, team, etc.
        """
        prompt = f"""
Analyze this Web3 project for potential airdrop opportunity:

{project_info}

Provide a detailed JSON analysis of the airdrop potential.
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            data = json.loads(json_match.group()) if json_match else {}
        
        return AirdropOpportunity(
            project=data.get("project", "Unknown"),
            chain=data.get("chain", "Unknown"),
            estimated_value=data.get("estimated_value", "Unknown"),
            probability=data.get("probability", "LOW"),
            requirements=data.get("requirements", []),
            deadline=data.get("deadline"),
            risk_level=data.get("risk_level", "MEDIUM"),
            action_steps=data.get("action_steps", []),
            reasoning=data.get("reasoning", ""),
            sources=data.get("sources", []),
        )
    
    def scan_funded_projects(
        self,
        projects: List[Dict[str, Any]],
    ) -> List[AirdropOpportunity]:
        """
        Scan multiple recently funded projects for airdrop potential.
        
        Args:
            projects: List of project dicts with name, funding, chain, etc.
        """
        prompt = f"""
Analyze these {len(projects)} recently funded Web3 projects for airdrop potential:

{json.dumps(projects, indent=2)}

For each project that has HIGH or MEDIUM airdrop probability, provide a JSON array of opportunities.
Only include projects with meaningful airdrop potential.
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            data = json.loads(json_match.group()) if json_match else []
        
        opportunities = []
        for item in (data if isinstance(data, list) else [data]):
            opportunities.append(AirdropOpportunity(
                project=item.get("project", "Unknown"),
                chain=item.get("chain", "Unknown"),
                estimated_value=item.get("estimated_value", "Unknown"),
                probability=item.get("probability", "LOW"),
                requirements=item.get("requirements", []),
                deadline=item.get("deadline"),
                risk_level=item.get("risk_level", "MEDIUM"),
                action_steps=item.get("action_steps", []),
                reasoning=item.get("reasoning", ""),
                sources=item.get("sources", []),
            ))
        
        return opportunities
    
    def generate_farming_strategy(
        self,
        opportunities: List[AirdropOpportunity],
        available_chains: List[str],
        budget_usd: float,
    ) -> Dict[str, Any]:
        """
        Generate an optimized airdrop farming strategy.
        
        Uses MiMo's reasoning to prioritize opportunities and
        allocate resources efficiently across chains.
        """
        opps_summary = [
            {
                "project": o.project,
                "chain": o.chain,
                "probability": o.probability,
                "risk": o.risk_level,
                "requirements": o.requirements,
            }
            for o in opportunities
        ]
        
        prompt = f"""
Generate an optimal airdrop farming strategy:

Available Opportunities:
{json.dumps(opps_summary, indent=2)}

Available Chains: {', '.join(available_chains)}
Budget: ${budget_usd}

Provide JSON strategy with:
1. priority_ranking: ordered list of opportunities by expected ROI
2. chain_allocation: how to distribute effort across chains
3. time_estimate: hours needed per opportunity
4. gas_budget: estimated gas costs
5. risk_warnings: important risks to consider
6. execution_order: step-by-step action plan
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}
