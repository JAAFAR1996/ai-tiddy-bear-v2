from __future__ import annotations

if TYPE_CHECKING:
    from .chaos_orchestrator import ChaosOrchestrator


class ChaosReporter:
    def __init__(self, orchestrator: ChaosOrchestrator) -> None:
        self.orchestrator = orchestrator

    def get_experiment_report(self, experiment_id: str) -> dict[str, any]:
        """Generate comprehensive experiment report."""
        metrics = next(
            (
                m
                for m in self.orchestrator.experiment_history
                if m.experiment_id == experiment_id
            ),
            None,
        )

        if not metrics:
            return {"error": f"Experiment {experiment_id} not found"}

        duration = (
            (metrics.end_time - metrics.start_time).total_seconds()
            if metrics.end_time
            else 0
        )

        return {
            "experiment_id": experiment_id,
            "duration_seconds": duration,
            "failures_injected": metrics.failures_injected,
            "failures_detected": metrics.failures_detected,
            "recovery_time_seconds": metrics.recovery_time_seconds,
            "safety_violations": metrics.safety_violations,
            "success_rate": metrics.success_rate,
            "performance_impact": metrics.performance_impact,
            "overall_status": (
                "PASS"
                if metrics.safety_violations == 0 and metrics.success_rate > 0.8
                else "FAIL"
            ),
        }

    def get_system_resilience_score(self) -> dict[str, any]:
        """Calculate overall system resilience score."""
        if not self.orchestrator.experiment_history:
            return {"resilience_score": 0.0, "experiments_count": 0}

        total_experiments = len(self.orchestrator.experiment_history)
        successful_experiments = sum(
            1
            for m in self.orchestrator.experiment_history
            if m.safety_violations == 0 and m.success_rate > 0.8
        )

        avg_recovery_time = (
            sum(m.recovery_time_seconds for m in self.orchestrator.experiment_history)
            / total_experiments
        )

        avg_success_rate = (
            sum(m.success_rate for m in self.orchestrator.experiment_history)
            / total_experiments
        )

        total_safety_violations = sum(
            m.safety_violations for m in self.orchestrator.experiment_history
        )

        resilience_score = (
            successful_experiments / total_experiments * 40
            + min(avg_success_rate, 1.0) * 30
            + max(0, (60 - avg_recovery_time) / 60) * 20
            + max(0, (10 - total_safety_violations) / 10) * 10
        )

        return {
            "resilience_score": round(resilience_score, 2),
            "experiments_count": total_experiments,
            "successful_experiments": successful_experiments,
            "average_recovery_time": round(avg_recovery_time, 2),
            "average_success_rate": round(avg_success_rate, 2),
            "total_safety_violations": total_safety_violations,
            "grade": self._get_resilience_grade(resilience_score),
        }

    def _get_resilience_grade(self, score: float) -> str:
        """Get resilience grade based on score."""
        if score >= 90:
            return "A+ (Excellent)"
        if score >= 80:
            return "A (Very Good)"
        if score >= 70:
            return "B (Good)"
        if score >= 60:
            return "C (Fair)"
        if score >= 50:
            return "D (Poor)"
        return "F (Fail)"
