# tests/state_manager.py
"""
State manager to track test step status
"""
import time
class TestStateManager:
    def __init__(self):
        self.steps = {}
        self.context = {}
        self.errors = []
        
    def record_step(self, step_name, status, error=None, data=None):
        """Record a step's execution status"""
        self.steps[step_name] = {
            "status": status,
            "error": str(error) if error else None,
            "data": data,
            "timestamp": time.time()
        }
        
        if error:
            self.errors.append(f"{step_name}: {error}")
    
    def get_step_status(self, step_name):
        """Get status of a specific step"""
        return self.steps.get(step_name, {}).get("status")
    
    def get_failed_steps(self):
        """Get all failed steps"""
        return {k: v for k, v in self.steps.items() if v.get("status") == "failed"}
    
    def get_summary(self):
        """Get test execution summary"""
        total = len(self.steps)
        passed = sum(1 for s in self.steps.values() if s.get("status") == "passed")
        failed = total - passed
        
        return {
            "total_steps": total,
            "passed_steps": passed,
            "failed_steps": failed,
            "failed_step_names": list(self.get_failed_steps().keys()),
            "errors": self.errors,
            "context_data": self.context
        }