"""Skill registry and execution engine."""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import SkillDefinition, SkillResult, SkillParameter
from .enums import SkillStatus, SkillCategory
from .exceptions import SkillNotFoundError, SkillExecutionError, SkillConfigurationError

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for managing skill definitions and execution."""
    
    def __init__(self):
        """Initialize skill registry."""
        self._skills: Dict[str, SkillDefinition] = {}
        self._execution_history: List[SkillResult] = []
    
    def register(self, skill: SkillDefinition) -> None:
        """Register a skill definition."""
        if skill.skill_id in self._skills:
            raise SkillConfigurationError(
                f"Skill already registered: {skill.skill_id}",
                config_key=skill.skill_id
            )
        
        # Validate parameters
        for param in skill.parameters:
            if not param.name:
                raise SkillConfigurationError(f"Parameter name required for skill {skill.skill_id}")
        
        self._skills[skill.skill_id] = skill
        logger.info(f"Registered skill: {skill.skill_id} v{skill.version}")
    
    def get(self, skill_id: str) -> Optional[SkillDefinition]:
        """Get skill definition by ID."""
        return self._skills.get(skill_id)
    
    def get_or_fail(self, skill_id: str) -> SkillDefinition:
        """Get skill definition or raise error."""
        skill = self._skills.get(skill_id)
        if not skill:
            raise SkillNotFoundError(skill_id)
        return skill
    
    def list_all(self, category: SkillCategory = None, status: SkillStatus = None) -> List[SkillDefinition]:
        """List skills with optional filtering."""
        result = list(self._skills.values())
        
        if category:
            result = [s for s in result if s.category == category]
        
        if status:
            result = [s for s in result if s.status == status]
        
        return result
    
    def search(self, query: str) -> List[SkillDefinition]:
        """Search skills by name or description."""
        query_lower = query.lower()
        return [
            s for s in self._skills.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]
    
    async def execute(self, skill_id: str, **parameters) -> SkillResult:
        """Execute a skill with given parameters."""
        skill = self.get_or_fail(skill_id)
        
        if skill.status != SkillStatus.ACTIVE:
            raise SkillExecutionError(f"Skill is not active: {skill.status.value}", skill_id)
        
        # Validate parameters
        errors = skill.validate_parameters(**parameters)
        if errors:
            error_msg = "; ".join([f"{k}: {v}" for k, v in errors.items()])
            raise SkillExecutionError(f"Parameter validation failed: {error_msg}", skill_id)
        
        start_time = datetime.utcnow()
        
        try:
            # Execute skill handler
            if skill.handler:
                if asyncio.iscoroutinefunction(skill.handler):
                    output = await skill.handler(**parameters)
                else:
                    output = skill.handler(**parameters)
            else:
                output = None
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = SkillResult(
                skill_id=skill_id,
                success=True,
                output=output,
                duration_ms=duration_ms
            )
            
            self._execution_history.append(result)
            logger.info(f"Skill executed successfully: {skill_id} ({duration_ms:.1f}ms)")
            
            return result
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = SkillResult(
                skill_id=skill_id,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )
            
            self._execution_history.append(result)
            logger.error(f"Skill execution failed: {skill_id} - {e}")
            raise SkillExecutionError(str(e), skill_id)
    
    def update_skill(self, skill_id: str, **updates) -> None:
        """Update skill properties."""
        skill = self.get_or_fail(skill_id)
        
        # Update allowed fields
        if "status" in updates:
            skill.status = updates["status"]
        if "description" in updates:
            skill.description = updates["description"]
        if "custom_metadata" in updates:
            skill.custom_metadata.update(updates["custom_metadata"])
        
        skill.updated_at = datetime.utcnow()
        logger.debug(f"Updated skill: {skill_id}")
    
    def deregister(self, skill_id: str) -> bool:
        """Deregister a skill."""
        if skill_id in self._skills:
            del self._skills[skill_id]
            logger.info(f"Deregistered skill: {skill_id}")
            return True
        return False
    
    def get_execution_history(self, skill_id: str = None, limit: int = 100) -> List[SkillResult]:
        """Get execution history."""
        history = self._execution_history
        
        if skill_id:
            history = [r for r in history if r.skill_id == skill_id]
        
        return history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        skills_by_category = {}
        skills_by_status = {}
        
        for skill in self._skills.values():
            cat_key = skill.category.value
            skills_by_category[cat_key] = skills_by_category.get(cat_key, 0) + 1
            
            status_key = skill.status.value
            skills_by_status[status_key] = skills_by_status.get(status_key, 0) + 1
        
        # Execution statistics
        total_executions = len(self._execution_history)
        successful = sum(1 for r in self._execution_history if r.success)
        failed = total_executions - successful
        
        return {
            "total_skills": len(self._skills),
            "by_category": skills_by_category,
            "by_status": skills_by_status,
            "executions": {
                "total": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
            }
        }
