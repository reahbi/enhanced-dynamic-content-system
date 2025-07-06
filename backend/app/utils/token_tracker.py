"""
Token usage tracking for Gemini API calls
"""

import logging
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Token usage record"""
    operation: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass
class PricingTier:
    """Gemini 2.5 Flash pricing tier"""
    max_tokens: int
    input_price_per_million: float
    output_price_per_million: float

class TokenTracker:
    """Tracks token usage and calculates costs for Gemini API"""
    
    # Gemini 2.5 Flash pricing (as of the provided image)
    PRICING_TIERS = [
        PricingTier(max_tokens=1_000_000, input_price_per_million=0.075, output_price_per_million=0.30),
        PricingTier(max_tokens=float('inf'), input_price_per_million=0.15, output_price_per_million=0.60)
    ]
    
    def __init__(self):
        self.usage_records: List[TokenUsage] = []
        self.lock = threading.Lock()
        self.session_start = datetime.now()
        
    def add_usage(self, operation: str, prompt_tokens: int, response_tokens: int, total_tokens: int):
        """Add token usage record"""
        with self.lock:
            usage = TokenUsage(
                operation=operation,
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
                total_tokens=total_tokens
            )
            self.usage_records.append(usage)
            logger.info(f"[Token Tracker] {operation}: prompt={prompt_tokens}, response={response_tokens}, total={total_tokens}")
    
    def get_session_summary(self) -> Dict:
        """Get session token usage summary with cost calculation"""
        with self.lock:
            if not self.usage_records:
                return {
                    "total_prompt_tokens": 0,
                    "total_response_tokens": 0,
                    "total_tokens": 0,
                    "operation_count": 0,
                    "operations": {},
                    "estimated_cost_krw": 0,
                    "session_duration": str(datetime.now() - self.session_start)
                }
            
            # Calculate totals
            total_prompt = sum(u.prompt_tokens for u in self.usage_records)
            total_response = sum(u.response_tokens for u in self.usage_records)
            total_tokens = sum(u.total_tokens for u in self.usage_records)
            
            # Group by operation
            operations = {}
            for usage in self.usage_records:
                if usage.operation not in operations:
                    operations[usage.operation] = {
                        "count": 0,
                        "prompt_tokens": 0,
                        "response_tokens": 0,
                        "total_tokens": 0
                    }
                op = operations[usage.operation]
                op["count"] += 1
                op["prompt_tokens"] += usage.prompt_tokens
                op["response_tokens"] += usage.response_tokens
                op["total_tokens"] += usage.total_tokens
            
            # Calculate cost (in KRW)
            cost_krw = self._calculate_cost_krw(total_prompt, total_response)
            
            return {
                "total_prompt_tokens": total_prompt,
                "total_response_tokens": total_response,
                "total_tokens": total_tokens,
                "operation_count": len(self.usage_records),
                "operations": operations,
                "estimated_cost_krw": cost_krw,
                "session_duration": str(datetime.now() - self.session_start)
            }
    
    def _calculate_cost_krw(self, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate cost in KRW based on Gemini 2.5 Flash pricing"""
        total_cost_usd = self._calculate_cost_usd(prompt_tokens, response_tokens)
        # Convert to KRW (assuming 1 USD = 1,300 KRW)
        exchange_rate = 1300
        total_cost_krw = total_cost_usd * exchange_rate
        return total_cost_krw
    
    def _calculate_cost_usd(self, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate cost in USD based on Gemini 2.5 Flash pricing"""
        # Determine pricing tier
        total_tokens = prompt_tokens + response_tokens
        
        # For simplicity, using the first tier pricing (most common case)
        # In production, you might want to track cumulative monthly usage
        tier = self.PRICING_TIERS[0]
        
        # Calculate cost in dollars
        input_cost = (prompt_tokens / 1_000_000) * tier.input_price_per_million
        output_cost = (response_tokens / 1_000_000) * tier.output_price_per_million
        total_cost_usd = input_cost + output_cost
        
        return total_cost_usd
    
    def log_workflow_summary(self, workflow_name: str):
        """Log summary for a complete workflow"""
        summary = self.get_session_summary()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[Token Tracker] Workflow Summary: {workflow_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Total Operations: {summary['operation_count']}")
        logger.info(f"Total Tokens: {summary['total_tokens']:,}")
        logger.info(f"  - Prompt Tokens: {summary['total_prompt_tokens']:,}")
        logger.info(f"  - Response Tokens: {summary['total_response_tokens']:,}")
        # Calculate USD cost
        cost_usd = self._calculate_cost_usd(summary['total_prompt_tokens'], summary['total_response_tokens'])
        logger.info(f"Estimated Cost: ${cost_usd:,.4f} USD (₩{summary['estimated_cost_krw']:,.2f} KRW)")
        logger.info(f"Session Duration: {summary['session_duration']}")
        logger.info(f"\nOperations Breakdown:")
        
        for op_name, op_stats in summary['operations'].items():
            logger.info(f"  {op_name}:")
            logger.info(f"    - Count: {op_stats['count']}")
            logger.info(f"    - Total Tokens: {op_stats['total_tokens']:,}")
            logger.info(f"    - Prompt: {op_stats['prompt_tokens']:,}, Response: {op_stats['response_tokens']:,}")
        
        logger.info(f"{'='*60}\n")
    
    def reset(self):
        """Reset tracking for new session"""
        with self.lock:
            self.usage_records.clear()
            self.session_start = datetime.now()

# Global token tracker instance
token_tracker = TokenTracker()