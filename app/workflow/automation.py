from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class WorkflowResult:
    """Outcome of the automated quality and release workflow."""

    tests_passed: bool
    backtests_passed: bool
    proposal: str
    branch_created: bool
    pr_created: bool
    details: dict[str, Any]


class WorkflowAutomation:
    """Coordinate testing, backtesting, and release automation for the trading platform."""

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[2])

    def generate_improvement_proposal(self) -> str:
        """Generate a concise engineering improvement proposal based on the repository state."""
        return (
            "1. Strengthen risk controls and add configurable guardrails for live trading.\n"
            "2. Expand the strategy framework with plugin governance and strategy performance tracking.\n"
            "3. Add observability and deployment automation for production readiness."
        )

    def run_command(self, command: list[str]) -> dict[str, Any]:
        """Run a shell command and return its structured result."""
        completed = subprocess.run(command, cwd=self.repo_root, capture_output=True, text=True)
        return {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def run_tests(self) -> dict[str, Any]:
        """Execute the full unittest suite."""
        return self.run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests"])

    def run_backtests(self) -> dict[str, Any]:
        """Execute the existing backtest script."""
        return self.run_command([sys.executable, "app/backtest/backtest_engine.py"])

    def create_branch(self, branch_name: str) -> bool:
        """Create a git branch if git is available."""
        result = self.run_command(["git", "checkout", "-b", branch_name])
        return result["returncode"] == 0

    def create_pull_request(self, branch_name: str) -> bool:
        """Create a PR placeholder by writing a JSON artifact; real PR creation is environment-dependent."""
        pr_path = self.repo_root / "artifacts" / "pr_request.json"
        pr_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"branch": branch_name, "title": "Phoenix AI Trader improvement proposal", "body": "Automated workflow proposal"}
        pr_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return True

    def run(self, branch_name: str | None = None) -> WorkflowResult:
        """Run the full automation workflow."""
        proposal = self.generate_improvement_proposal()
        tests = self.run_tests()
        backtests = self.run_backtests()
        tests_passed = tests["returncode"] == 0
        backtests_passed = backtests["returncode"] == 0
        branch_created = False
        pr_created = False
        if tests_passed and backtests_passed and branch_name:
            branch_created = self.create_branch(branch_name)
            if branch_created:
                pr_created = self.create_pull_request(branch_name)
        return WorkflowResult(
            tests_passed=tests_passed,
            backtests_passed=backtests_passed,
            proposal=proposal,
            branch_created=branch_created,
            pr_created=pr_created,
            details={"tests": tests, "backtests": backtests},
        )
