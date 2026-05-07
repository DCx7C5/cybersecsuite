"""Agent management and coordination."""

import logging
from datetime import datetime

from .models import AgentConfig, AgentMetrics, AgentState, AgentMessage
from .enums import AgentStatus, AgentType
from .exceptions import AgentNotFoundError, AgentExecutionError, AgentConfigurationError

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing agent instances."""
    
    def __init__(self):
        """Initialize agent registry."""
        self._agents: dict[str, AgentState] = {}
        self._message_queue: dict[str, list[AgentMessage]] = {}
    
    def register(self, config: AgentConfig) -> AgentState:
        """Register a new agent."""
        try:
            if config.agent_id in self._agents:
                raise AgentConfigurationError(
                    f"Agent already registered: {config.agent_id}",
                    config_key=config.agent_id
                )
            
            # Create initial metrics
            metrics = AgentMetrics(agent_id=config.agent_id)
            
            # Create agent state
            state = AgentState(
                agent_id=config.agent_id,
                status=AgentStatus.IDLE,
                config=config,
                metrics=metrics
            )
            
            self._agents[config.agent_id] = state
            self._message_queue[config.agent_id] = []
            
            logger.info(f"Registered agent: {config.agent_id}")
            return state
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    def get(self, agent_id: str) -> AgentState | None:
        """Get agent by ID."""
        return self._agents.get(agent_id)
    
    def get_or_fail(self, agent_id: str) -> AgentState:
        """Get agent by ID or raise error."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        return agent
    
    def update_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update agent status."""
        agent = self.get_or_fail(agent_id)
        agent.status = status
        agent.last_updated = datetime.utcnow()
        logger.debug(f"Agent {agent_id} status updated: {status.value}")
    
    def record_execution(self, agent_id: str, duration_ms: float, success: bool, error: str = None) -> None:
        """Record agent execution metrics."""
        agent = self.get_or_fail(agent_id)
        metrics = agent.metrics
        
        metrics.total_executions += 1
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
            if error:
                metrics.errors.append(error)
        
        metrics.total_duration_ms += duration_ms
        metrics.last_execution_at = datetime.utcnow()
        
        logger.debug(f"Agent {agent_id} execution recorded: {duration_ms}ms, success={success}")
    
    def list_all(self, agent_type: AgentType = None, status: AgentStatus = None) -> list[AgentState]:
        """List agents with optional filtering."""
        result = list(self._agents.values())
        
        if agent_type:
            result = [a for a in result if a.config.agent_type == agent_type]
        
        if status:
            result = [a for a in result if a.status == status]
        
        return result
    
    def deregister(self, agent_id: str) -> bool:
        """Deregister an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._message_queue.pop(agent_id, None)
            logger.info(f"Deregistered agent: {agent_id}")
            return True
        return False
    
    def send_message(self, message: AgentMessage) -> None:
        """Send message from one agent to another."""
        if message.recipient_id not in self._message_queue:
            raise AgentNotFoundError(message.recipient_id)
        
        self._message_queue[message.recipient_id].append(message)
        logger.debug(f"Message sent from {message.sender_id} to {message.recipient_id}")
    
    def get_messages(self, agent_id: str, clear: bool = True) -> list[AgentMessage]:
        """Get pending messages for an agent."""
        if agent_id not in self._message_queue:
            raise AgentNotFoundError(agent_id)
        
        messages = self._message_queue[agent_id]
        if clear:
            self._message_queue[agent_id] = []
        
        return messages
    
    def get_stats(self) -> dict[str, any]:
        """Get registry statistics."""
        total = len(self._agents)
        by_status = {}
        by_type = {}
        
        for state in self._agents.values():
            status_key = state.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            type_key = state.config.agent_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
        
        return {
            "total_agents": total,
            "by_status": by_status,
            "by_type": by_type,
        }


class AgentExecutor:
    """Executes agents with proper error handling and metrics."""
    
    def __init__(self, registry: AgentRegistry):
        """Initialize executor with registry."""
        self.registry = registry
    
    async def execute(self, agent_id: str, *args, **kwargs) -> any:
        """Execute an agent with error handling."""
        agent = self.registry.get_or_fail(agent_id)
        
        if not agent.config.enabled:
            raise AgentExecutionError("Agent is disabled", agent_id)
        
        try:
            self.registry.update_status(agent_id, AgentStatus.RUNNING)
            
            # TODO: Actual execution logic here
            # - Call agent's execute method
            # - Handle timeouts
            # - Capture metrics
            
            result = None
            self.registry.record_execution(agent_id, 0, True)
            self.registry.update_status(agent_id, AgentStatus.IDLE)
            
            return result
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            agent.last_error = str(e)
            self.registry.record_execution(agent_id, 0, False, str(e))
            self.registry.update_status(agent_id, AgentStatus.ERROR)
            raise AgentExecutionError(str(e), agent_id)
