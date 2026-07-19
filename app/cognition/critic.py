"""Quality gate for strategies, models, research, and architecture proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Critique:
    accepted: bool
    reasons: list[str]
    recommendations: list[str]


class Critic:
    """Rejects proposals below minimum evidence, risk, or quality thresholds."""

    def review(self, proposal: dict[str, Any]) -> Critique:
        reasons: list[str] = []
        if float(proposal.get("score", 0.0)) <= 0:
            reasons.append("Performance score is not positive")
        if float(proposal.get("risk", 0.0)) > float(proposal.get("risk_limit", 1.0)):
            reasons.append("Risk exceeds the configured limit")
        if float(proposal.get("confidence", 0.0)) < float(proposal.get("minimum_confidence", 0.5)):
            reasons.append("Evidence confidence is below the required threshold")
        accepted = not reasons
        return Critique(accepted, reasons or ["Proposal satisfies performance, risk, and confidence gates"], [] if accepted else ["Gather additional evidence or reduce risk before resubmission"])
