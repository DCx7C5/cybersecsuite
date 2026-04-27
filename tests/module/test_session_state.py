"""
Tests for t367: Worker Session State Save/Restore.

Tests context persistence, execution history, bookmarks, and integrity verification.
"""
import pytest
from datetime import datetime

from db.models.worker import WorkerSession
from db.managers.session_manager import (
    WorkerSessionManager,
    ExecutionHistoryManager,
    BookmarkManager,
    IntegrityCheckError,
    SessionNotFoundError,
)


@pytest.mark.asyncio
class TestWorkerSessionManager:
    """Test worker session save/restore (t367)."""
    
    async def test_save_session_creates_new_session(
        self,
        test_project
    ) -> None:
        """Test saving a new worker session."""
        manager = WorkerSessionManager(
            worker_id="worker-save-1",
            project_id=test_project.id
        )
        
        context = {"state": "processing", "count": 42}
        history = [
            {"action": "start", "status": "success", "timestamp": datetime.utcnow().isoformat()}
        ]
        bookmarks = {"checkpoint-1": {"line": 100}}
        
        session = await manager.save_session(context, history, bookmarks)
        
        assert session.worker_id == "worker-save-1"
        assert session.context_data == context
        assert len(session.execution_history) == 1
        assert session.bookmarks == bookmarks
        assert session.steps_executed == 1
    
    async def test_save_session_updates_existing_session(
        self,
        test_project
    ) -> None:
        """Test updating an existing session."""
        manager = WorkerSessionManager(
            worker_id="worker-save-2",
            project_id=test_project.id
        )
        
        # First save
        context1 = {"count": 1}
        history1 = [{"action": "init"}]
        bookmarks1 = {}
        
        session1 = await manager.save_session(context1, history1, bookmarks1)
        session_id = session1.id
        
        # Second save
        context2 = {"count": 2}
        history2 = [{"action": "init"}, {"action": "process"}]
        bookmarks2 = {"mark1": {"pos": 1}}
        
        session2 = await manager.save_session(context2, history2, bookmarks2)
        
        # Should update same session
        assert session2.id == session_id
        assert session2.context_data == context2
        assert len(session2.execution_history) == 2
        assert session2.steps_executed == 2
    
    async def test_restore_session_succeeds(
        self,
        test_project
    ) -> None:
        """Test restoring a saved session."""
        manager = WorkerSessionManager(
            worker_id="worker-restore-1",
            project_id=test_project.id
        )
        
        # Save session
        context = {"data": "test"}
        history = [{"action": "work"}]
        bookmarks = {"bm": {"pos": 5}}
        
        await manager.save_session(context, history, bookmarks)
        
        # Restore session
        restored = await manager.restore_session(verify_integrity=False)
        
        assert restored.worker_id == "worker-restore-1"
        assert restored.context_data == context
        assert restored.execution_history == history
        assert restored.bookmarks == bookmarks
    
    async def test_restore_nonexistent_session_raises_error(
        self,
        test_project
    ) -> None:
        """Test restoring a session that doesn't exist."""
        manager = WorkerSessionManager(
            worker_id="nonexistent-worker",
            project_id=test_project.id
        )
        
        with pytest.raises(SessionNotFoundError):
            await manager.restore_session()
    
    async def test_integrity_verification_passes_for_valid_data(
        self,
        test_project
    ) -> None:
        """Test integrity verification passes for valid saved data."""
        manager = WorkerSessionManager(
            worker_id="worker-integrity-1",
            project_id=test_project.id
        )
        
        context = {"state": "valid"}
        history = [{"action": "test"}]
        bookmarks = {"mark": {"data": 123}}
        
        await manager.save_session(context, history, bookmarks)
        
        # Restore with integrity check
        restored = await manager.restore_session(verify_integrity=True)
        
        assert restored is not None
        assert restored.context_data == context
    
    async def test_integrity_verification_detects_tampering(
        self,
        test_project
    ) -> None:
        """Test integrity verification detects modified data (t367)."""
        manager = WorkerSessionManager(
            worker_id="worker-integrity-2",
            project_id=test_project.id
        )
        
        context = {"original": "data"}
        history = []
        bookmarks = {}
        
        session = await manager.save_session(context, history, bookmarks)
        
        # Simulate tampering by modifying context without updating hash
        session.context_data["tampered"] = "yes"
        await session.save()
        
        # Restore should detect tampering
        with pytest.raises(IntegrityCheckError):
            await manager.restore_session(verify_integrity=True)
    
    async def test_integrity_verification_detects_history_tampering(
        self,
        test_project
    ) -> None:
        """Test integrity verification detects tampering with history."""
        manager = WorkerSessionManager(
            worker_id="worker-integrity-3",
            project_id=test_project.id
        )
        
        context = {}
        history = [{"action": "original"}]
        bookmarks = {}
        
        session = await manager.save_session(context, history, bookmarks)
        
        # Tamper with history
        session.execution_history.append({"action": "injected"})
        await session.save()
        
        # Restore should detect tampering
        with pytest.raises(IntegrityCheckError):
            await manager.restore_session(verify_integrity=True)
    
    async def test_integrity_verification_detects_bookmarks_tampering(
        self,
        test_project
    ) -> None:
        """Test integrity verification detects tampering with bookmarks."""
        manager = WorkerSessionManager(
            worker_id="worker-integrity-4",
            project_id=test_project.id
        )
        
        context = {}
        history = []
        bookmarks = {"mark1": {"pos": 1}}
        
        session = await manager.save_session(context, history, bookmarks)
        
        # Tamper with bookmarks
        session.bookmarks["mark2"] = {"pos": 2}
        await session.save()
        
        # Restore should detect tampering
        with pytest.raises(IntegrityCheckError):
            await manager.restore_session(verify_integrity=True)
    
    async def test_clear_session_removes_data(
        self,
        test_project
    ) -> None:
        """Test clearing a session."""
        manager = WorkerSessionManager(
            worker_id="worker-clear-1",
            project_id=test_project.id
        )
        
        await manager.save_session({"data": "test"}, [], {})
        
        # Verify session exists
        session = await WorkerSession.get_or_none(worker_id="worker-clear-1")
        assert session is not None
        
        # Clear it
        await manager.clear_session()
        
        # Verify it's gone
        session = await WorkerSession.get_or_none(worker_id="worker-clear-1")
        assert session is None


@pytest.mark.asyncio
class TestExecutionHistoryManager:
    """Test execution history management (t367)."""
    
    async def test_append_step_creates_session_if_needed(
        self,
        test_project
    ) -> None:
        """Test appending step to execution history."""
        # Create initial session
        mgr = WorkerSessionManager("worker-hist-1", test_project.id)
        await mgr.save_session({}, [], {})
        
        # Append steps
        hist_mgr = ExecutionHistoryManager("worker-hist-1")
        await hist_mgr.append_step("fetch", "success", {"count": 10})
        await hist_mgr.append_step("analyze", "success", {"result": "ok"})
        
        # Verify history
        session = await WorkerSession.get(worker_id="worker-hist-1")
        assert len(session.execution_history) == 2
        assert session.execution_history[0]["action"] == "fetch"
        assert session.execution_history[1]["action"] == "analyze"
    
    async def test_append_step_with_error(
        self,
        test_project
    ) -> None:
        """Test appending failed step to history."""
        mgr = WorkerSessionManager("worker-hist-2", test_project.id)
        await mgr.save_session({}, [], {})
        
        hist_mgr = ExecutionHistoryManager("worker-hist-2")
        await hist_mgr.append_step(
            "process",
            "failure",
            error="Database connection failed"
        )
        
        session = await WorkerSession.get(worker_id="worker-hist-2")
        assert session.execution_history[0]["status"] == "failure"
        assert session.execution_history[0]["error"] == "Database connection failed"
    
    async def test_get_history_returns_all_steps(
        self,
        test_project
    ) -> None:
        """Test retrieving full execution history."""
        mgr = WorkerSessionManager("worker-hist-3", test_project.id)
        await mgr.save_session({}, [], {})
        
        hist_mgr = ExecutionHistoryManager("worker-hist-3")
        for i in range(5):
            await hist_mgr.append_step(f"action-{i}", "success")
        
        history = await hist_mgr.get_history()
        assert len(history) == 5
    
    async def test_get_history_with_limit(
        self,
        test_project
    ) -> None:
        """Test retrieving limited history."""
        mgr = WorkerSessionManager("worker-hist-4", test_project.id)
        await mgr.save_session({}, [], {})
        
        hist_mgr = ExecutionHistoryManager("worker-hist-4")
        for i in range(10):
            await hist_mgr.append_step(f"action-{i}", "success")
        
        history = await hist_mgr.get_history(limit=3)
        assert len(history) == 3
        # Should get last 3
        assert history[-1]["action"] == "action-9"
    
    async def test_clear_history(
        self,
        test_project
    ) -> None:
        """Test clearing execution history."""
        mgr = WorkerSessionManager("worker-hist-5", test_project.id)
        await mgr.save_session({}, [{"action": "init"}], {})
        
        hist_mgr = ExecutionHistoryManager("worker-hist-5")
        await hist_mgr.clear_history()
        
        session = await WorkerSession.get(worker_id="worker-hist-5")
        assert len(session.execution_history) == 0


@pytest.mark.asyncio
class TestBookmarkManager:
    """Test bookmark management (t367)."""
    
    async def test_set_bookmark_creates_bookmark(
        self,
        test_project
    ) -> None:
        """Test setting a bookmark."""
        mgr = WorkerSessionManager("worker-bm-1", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-1")
        await bm_mgr.set_bookmark(
            "checkpoint-1",
            line=100,
            position=1050,
            state={"progress": 50}
        )
        
        session = await WorkerSession.get(worker_id="worker-bm-1")
        assert "checkpoint-1" in session.bookmarks
        assert session.bookmarks["checkpoint-1"]["line"] == 100
        assert session.bookmarks["checkpoint-1"]["position"] == 1050
    
    async def test_get_bookmark_retrieves_bookmark(
        self,
        test_project
    ) -> None:
        """Test retrieving a bookmark."""
        mgr = WorkerSessionManager("worker-bm-2", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-2")
        await bm_mgr.set_bookmark(
            "mark-1",
            line=50,
            state={"status": "running"}
        )
        
        bookmark = await bm_mgr.get_bookmark("mark-1")
        assert bookmark is not None
        assert bookmark["line"] == 50
        assert bookmark["state"]["status"] == "running"
    
    async def test_get_nonexistent_bookmark_returns_none(
        self,
        test_project
    ) -> None:
        """Test retrieving non-existent bookmark."""
        mgr = WorkerSessionManager("worker-bm-3", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-3")
        bookmark = await bm_mgr.get_bookmark("nonexistent")
        assert bookmark is None
    
    async def test_delete_bookmark_removes_bookmark(
        self,
        test_project
    ) -> None:
        """Test deleting a bookmark."""
        mgr = WorkerSessionManager("worker-bm-4", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-4")
        await bm_mgr.set_bookmark("mark-1", line=1)
        await bm_mgr.set_bookmark("mark-2", line=2)
        
        await bm_mgr.delete_bookmark("mark-1")
        
        session = await WorkerSession.get(worker_id="worker-bm-4")
        assert "mark-1" not in session.bookmarks
        assert "mark-2" in session.bookmarks
    
    async def test_list_bookmarks_returns_all_bookmarks(
        self,
        test_project
    ) -> None:
        """Test listing all bookmarks."""
        mgr = WorkerSessionManager("worker-bm-5", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-5")
        for i in range(3):
            await bm_mgr.set_bookmark(f"mark-{i}", line=i*10)
        
        bookmarks = await bm_mgr.list_bookmarks()
        assert len(bookmarks) == 3
        assert "mark-0" in bookmarks
        assert "mark-1" in bookmarks
        assert "mark-2" in bookmarks
    
    async def test_clear_bookmarks_removes_all(
        self,
        test_project
    ) -> None:
        """Test clearing all bookmarks."""
        mgr = WorkerSessionManager("worker-bm-6", test_project.id)
        await mgr.save_session({}, [], {})
        
        bm_mgr = BookmarkManager("worker-bm-6")
        await bm_mgr.set_bookmark("mark-1")
        await bm_mgr.set_bookmark("mark-2")
        
        await bm_mgr.clear_bookmarks()
        
        bookmarks = await bm_mgr.list_bookmarks()
        assert len(bookmarks) == 0


@pytest.mark.asyncio
class TestIntegrityVerification:
    """Test BLAKE2b integrity verification (t367)."""
    
    async def test_blake2b_hash_consistency(
        self,
        test_project
    ) -> None:
        """Test that same data produces same hash."""
        data = {"test": "data", "number": 42}
        
        hash1 = WorkerSession._compute_hash(data)
        hash2 = WorkerSession._compute_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # BLAKE2b-256 = 32 bytes = 64 hex chars
    
    async def test_blake2b_hash_differs_for_different_data(
        self,
        test_project
    ) -> None:
        """Test that different data produces different hashes."""
        data1 = {"value": 1}
        data2 = {"value": 2}
        
        hash1 = WorkerSession._compute_hash(data1)
        hash2 = WorkerSession._compute_hash(data2)
        
        assert hash1 != hash2
    
    async def test_verify_integrity_method_checks_all_hashes(
        self,
        test_project
    ) -> None:
        """Test verify_integrity method checks all components."""
        mgr = WorkerSessionManager("worker-verify-1", test_project.id)
        await mgr.save_session(
            {"data": "test"},
            [{"action": "test"}],
            {"mark": {"pos": 1}}
        )
        
        session = await WorkerSession.get(worker_id="worker-verify-1")
        is_valid, failures = await session.verify_integrity()
        
        assert is_valid is True
        assert len(failures) == 0
