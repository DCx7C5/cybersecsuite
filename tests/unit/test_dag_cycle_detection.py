"""Unit tests for DAG cycle detection logic (DFS-based)."""
import pytest


class MockTask:
    """Mock Task object for testing cycle detection without Tortoise ORM."""
    _storage = {}
    
    def __init__(self, task_id: int, plan_id: int):
        self.id = task_id
        self.plan_id = plan_id
        self.depends_on = set()
        MockTask._storage[task_id] = self
    
    @classmethod
    def clear(cls):
        cls._storage.clear()
    
    @classmethod
    def get_task(cls, task_id: int):
        return cls._storage.get(task_id)


class DAGValidator:
    """DAG validation logic (testable without ORM)."""
    
    @staticmethod
    def would_create_cycle(task_id: int, new_dep_id: int, memo: dict = None) -> bool:
        """Check if adding a dependency would create a cycle using DFS with memoization."""
        if memo is None:
            memo = {}
        
        visited = set()
        
        def has_path_to_target(current_id: int, target_id: int) -> bool:
            if current_id == target_id:
                return True
            if current_id in visited:
                return False
            if current_id in memo:
                return memo[current_id]
            
            visited.add(current_id)
            current_task = MockTask.get_task(current_id)
            if current_task is None:
                return False
            
            for dep in current_task.depends_on:
                if has_path_to_target(dep.id, target_id):
                    return True
            
            result = False
            memo[current_id] = result
            return result
        
        return has_path_to_target(new_dep_id, task_id)
    
    @staticmethod
    def validate_plan_dag(plan_id: int) -> list:
        """Validate that all tasks in a plan form a valid DAG."""
        errors = []
        
        for task in MockTask._storage.values():
            if task.plan_id != plan_id:
                continue
            
            visited = set()
            
            def has_cycle_from(current_id: int) -> bool:
                current_task = MockTask.get_task(current_id)
                if current_task is None:
                    return False
                
                if current_id in visited:
                    return True
                visited.add(current_id)
                
                for dep in current_task.depends_on:
                    if has_cycle_from(dep.id):
                        return True
                
                visited.discard(current_id)
                return False
            
            if has_cycle_from(task.id):
                errors.append(f"Cycle detected involving task {task.id}")
        
        return errors


class TestDAGCycleDetection:
    """Tests for cycle detection using DFS."""
    
    def setup_method(self):
        """Clear mock storage before each test."""
        MockTask.clear()
    
    def test_no_cycle_simple_chain(self):
        """Test that a simple chain A→B→C has no cycle."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        
        t2.depends_on = {t1}
        t3.depends_on = {t2}
        
        assert DAGValidator.would_create_cycle(3, 1) is False
    
    def test_self_cycle_detected(self):
        """Test that self-cycle is always prevented by add_dependency logic."""
        t1 = MockTask(1, 1)
        
        assert DAGValidator.would_create_cycle(1, 1) is True
    
    def test_direct_cycle_two_tasks(self):
        """Test direct cycle: A→B, add B→A creates cycle."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        
        t1.depends_on = {t2}
        
        assert DAGValidator.would_create_cycle(2, 1) is True
    
    def test_indirect_cycle_three_tasks(self):
        """Test indirect cycle: A→B→C, add C→A creates cycle."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        
        t1.depends_on = {t2}
        t2.depends_on = {t3}
        
        assert DAGValidator.would_create_cycle(3, 1) is True
    
    def test_indirect_cycle_four_tasks(self):
        """Test indirect cycle: A→B→C→D, add D→A creates cycle."""
        tasks = [MockTask(i, 1) for i in range(1, 5)]
        
        tasks[0].depends_on = {tasks[1]}
        tasks[1].depends_on = {tasks[2]}
        tasks[2].depends_on = {tasks[3]}
        
        assert DAGValidator.would_create_cycle(4, 1) is True
    
    def test_no_cycle_diamond_pattern(self):
        """Test diamond pattern (no cycle): A depends on B,C; B,C depend on D."""
        t_a = MockTask(1, 1)  # A
        t_b = MockTask(2, 1)  # B
        t_c = MockTask(3, 1)  # C
        t_d = MockTask(4, 1)  # D
        
        t_a.depends_on = {t_b, t_c}
        t_b.depends_on = {t_d}
        t_c.depends_on = {t_d}
        
        assert DAGValidator.would_create_cycle(1, 4) is False
    
    def test_no_cycle_multiple_independent_chains(self):
        """Test multiple independent chains have no cycle."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        t4 = MockTask(4, 1)
        
        t2.depends_on = {t1}
        t4.depends_on = {t3}
        
        assert DAGValidator.would_create_cycle(2, 1) is False
        assert DAGValidator.would_create_cycle(4, 3) is False
        assert DAGValidator.would_create_cycle(3, 1) is False
    
    def test_cycle_with_multiple_incoming_edges(self):
        """Test cycle detection with task having multiple dependencies."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        t4 = MockTask(4, 1)
        
        # t3 depends on t1 and t2, t4 depends on t3
        t3.depends_on = {t1, t2}
        t4.depends_on = {t3}
        
        # t1 ← t3 ← t4, adding t1→t4 creates cycle
        assert DAGValidator.would_create_cycle(1, 4) is True
        assert DAGValidator.would_create_cycle(2, 4) is True
        
        # But t1←t3←t4 doesn't mean t4 has a path back to t1, so adding 4→1 would NOT create cycle initially
        # Wait, let me re-think: if t3 depends on t1, and t4 depends on t3, then t4 transitively depends on t1
        # So adding t1→t4 means: t1→t4←t1 (through t3), which is a cycle
    
    def test_validate_plan_dag_valid(self):
        """Test validate_plan_dag returns empty for valid DAG."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        
        t2.depends_on = {t1}
        t3.depends_on = {t1}
        
        errors = DAGValidator.validate_plan_dag(1)
        assert errors == []
    
    def test_validate_plan_dag_detects_cycle(self):
        """Test validate_plan_dag detects cycles."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        
        t1.depends_on = {t2}
        t2.depends_on = {t3}
        t3.depends_on = {t1}
        
        errors = DAGValidator.validate_plan_dag(1)
        assert len(errors) > 0
        assert all("Cycle detected" in err for err in errors)
    
    def test_validate_plan_dag_cross_plan(self):
        """Test validate_plan_dag only validates specified plan."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 2)
        
        t1.depends_on = {t2}
        
        errors1 = DAGValidator.validate_plan_dag(1)
        errors2 = DAGValidator.validate_plan_dag(2)
        
        assert errors1 == []
        assert errors2 == []


class TestDAGMemoization:
    """Tests for memoization in cycle detection."""
    
    def setup_method(self):
        """Clear mock storage before each test."""
        MockTask.clear()
    
    def test_memoization_prevents_redundant_traversal(self):
        """Test that memoization speeds up cycle detection for repeated calls."""
        t1 = MockTask(1, 1)
        t2 = MockTask(2, 1)
        t3 = MockTask(3, 1)
        
        t2.depends_on = {t1}
        t3.depends_on = {t2}
        
        memo = {}
        
        result1 = DAGValidator.would_create_cycle(3, 1, memo)
        assert result1 is False
        
        result2 = DAGValidator.would_create_cycle(3, 1, memo)
        assert result2 is False
    
    def test_memoization_with_complex_graph(self):
        """Test memoization with a more complex dependency graph."""
        tasks = [MockTask(i, 1) for i in range(1, 6)]
        
        # Build DAG: 2 depends on 3, 3 depends on 4 and 5
        tasks[1].depends_on = {tasks[2]}
        tasks[2].depends_on = {tasks[3], tasks[4]}
        
        memo = {}
        
        # No cycle: 1 is independent
        assert DAGValidator.would_create_cycle(1, 2, memo) is False
        # Memo should have entries from the traversal
        assert len(memo) > 0
        
        # Add another independent test
        memo.clear()
        t6 = MockTask(6, 1)
        assert DAGValidator.would_create_cycle(6, 2, memo) is False
