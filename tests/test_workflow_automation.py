import unittest

from app.workflow.automation import WorkflowAutomation


class WorkflowAutomationTests(unittest.TestCase):
    def test_generate_improvement_proposal(self) -> None:
        automation = WorkflowAutomation()
        proposal = automation.generate_improvement_proposal()
        self.assertIn("risk", proposal.lower())

    def test_run_returns_structured_result(self) -> None:
        automation = WorkflowAutomation()
        result = automation.run(branch_name="test-workflow")
        self.assertIsInstance(result.tests_passed, bool)
        self.assertIsInstance(result.backtests_passed, bool)
        self.assertIn("risk", result.proposal.lower())


if __name__ == "__main__":
    unittest.main()
