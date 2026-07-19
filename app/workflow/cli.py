from __future__ import annotations

import argparse
import json

from app.workflow.automation import WorkflowAutomation


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phoenix AI Trader automation workflow")
    parser.add_argument("--branch", default=None, help="Git branch to create when checks pass")
    args = parser.parse_args()

    automation = WorkflowAutomation()
    result = automation.run(branch_name=args.branch)
    print(json.dumps({
        "tests_passed": result.tests_passed,
        "backtests_passed": result.backtests_passed,
        "proposal": result.proposal,
        "branch_created": result.branch_created,
        "pr_created": result.pr_created,
    }, indent=2))


if __name__ == "__main__":
    main()
