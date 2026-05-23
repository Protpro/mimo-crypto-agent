"""
Smart Contract Analyzer
AI-powered Solidity/smart contract security analysis using MiMo-V2.5-Pro
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

from .mimo_client import MiMoClient


@dataclass
class Vulnerability:
    """Detected vulnerability in smart contract."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    type: str
    description: str
    location: str
    recommendation: str
    cwe_id: str = ""


@dataclass
class ContractAudit:
    """Smart contract audit result."""
    contract_name: str
    overall_risk: str  # CRITICAL, HIGH, MEDIUM, LOW
    score: int  # 0-100
    vulnerabilities: List[Vulnerability]
    gas_optimizations: List[str]
    best_practices: List[str]
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ContractAnalyzer:
    """
    AI-powered smart contract security analyzer.
    
    Uses MiMo-V2.5-Pro's code understanding capabilities to detect
    vulnerabilities, gas inefficiencies, and security issues in
    Solidity smart contracts.
    """
    
    SYSTEM_PROMPT = """You are an expert smart contract security auditor specializing in Solidity/EVM.
You analyze contracts for:
1. Security vulnerabilities (reentrancy, overflow, access control, etc.)
2. Gas optimization opportunities
3. Best practice violations
4. Logic errors
5. Centralization risks

Output JSON with:
- overall_risk: CRITICAL/HIGH/MEDIUM/LOW
- score: security score 0-100
- vulnerabilities: array of {severity, type, description, location, recommendation, cwe_id}
- gas_optimizations: array of suggestions
- best_practices: array of recommendations
- summary: overall assessment"""
    
    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client
    
    def analyze_contract(
        self,
        contract_code: str,
        contract_name: str = "Unknown",
    ) -> ContractAudit:
        """
        Analyze a Solidity smart contract for vulnerabilities.
        
        Args:
            contract_code: Solidity source code
            contract_name: Name of the contract
        """
        prompt = f"""
Analyze this Solidity smart contract for security issues:

Contract: {contract_name}
```solidity
{contract_code[:8000]}  # Limit to prevent token overflow
```

Provide a detailed JSON security audit.
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            data = json.loads(json_match.group()) if json_match else {}
        
        vulnerabilities = [
            Vulnerability(
                severity=v.get("severity", "INFO"),
                type=v.get("type", "Unknown"),
                description=v.get("description", ""),
                location=v.get("location", ""),
                recommendation=v.get("recommendation", ""),
                cwe_id=v.get("cwe_id", ""),
            )
            for v in data.get("vulnerabilities", [])
        ]
        
        return ContractAudit(
            contract_name=contract_name,
            overall_risk=data.get("overall_risk", "MEDIUM"),
            score=data.get("score", 50),
            vulnerabilities=vulnerabilities,
            gas_optimizations=data.get("gas_optimizations", []),
            best_practices=data.get("best_practices", []),
            summary=data.get("summary", ""),
        )
    
    def compare_contracts(
        self,
        contract_a: str,
        contract_b: str,
        name_a: str = "Contract A",
        name_b: str = "Contract B",
    ) -> Dict[str, Any]:
        """
        Compare two contracts for security and efficiency.
        
        Useful for evaluating forks, upgrades, or alternative implementations.
        """
        prompt = f"""
Compare these two smart contracts and provide a security/efficiency comparison:

=== {name_a} ===
```solidity
{contract_a[:4000]}
```

=== {name_b} ===
```solidity
{contract_b[:4000]}
```

Provide JSON comparison with:
1. security_winner: which contract is more secure
2. gas_winner: which is more gas efficient
3. differences: key differences found
4. recommendation: which to use and why
"""
        
        response = self.mimo.analyze(prompt, system=self.SYSTEM_PROMPT)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}
