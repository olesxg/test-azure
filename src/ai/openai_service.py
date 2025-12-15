import json
from typing import List, Dict
from openai import AsyncOpenAI
from src.arbitrage.analyzer import ArbitrageOpportunity


class OpenAIAnalyzer:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze_opportunities(
        self, opportunities: List[ArbitrageOpportunity]
    ) -> Dict:
        if not opportunities:
            return {"recommendation": "no_opportunities", "analysis": "No data"}

        prompt = self._build_prompt(opportunities)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cryptocurrency arbitrage trading expert. Analyze opportunities and provide concise recommendations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            analysis = response.choices[0].message.content
            return {
                "recommendation": self._extract_recommendation(analysis),
                "analysis": analysis,
                "opportunities_count": len(opportunities),
                "top_profit_percent": opportunities[0].profit_percent,
            }
        except Exception as e:
            return {"recommendation": "error", "analysis": str(e)}

    def _build_prompt(self, opportunities: List[ArbitrageOpportunity]) -> str:
        top_opps = opportunities[:5]
        opp_text = "\n".join(
            [
                f"- {o.symbol}: Buy on {o.buy_exchange} at ${o.buy_price:.2f}, "
                f"Sell on {o.sell_exchange} at ${o.sell_price:.2f}, "
                f"Profit: {o.profit_percent:.2f}% (${o.profit_usd:.2f})"
                for o in top_opps
            ]
        )

        return f"""Analyze these cryptocurrency arbitrage opportunities:

            {opp_text}

            Provide:
            1. Best opportunity to execute
            2. Risk assessment
            3. Market conditions insight
            4. Recommendation (execute/wait/avoid)

            Keep response under 300 words."""

    def _extract_recommendation(self, analysis: str) -> str:
        analysis_lower = analysis.lower()
        if "execute" in analysis_lower and "avoid" not in analysis_lower:
            return "execute"
        elif "wait" in analysis_lower:
            return "wait"
        elif "avoid" in analysis_lower:
            return "avoid"
        return "analyze"
