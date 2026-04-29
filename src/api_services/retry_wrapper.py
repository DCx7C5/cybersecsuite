"""Wrapper to add retry logic to any API service."""

import logging
from typing import AsyncIterator, Optional

from core.types import (
    BaseApiServiceClient,
    Message,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ProviderType,
)
from core.retry import RetryOrchestrator, RetryConfig

logger = logging.getLogger(__name__)


class RetryWrappedApiService:
    """
    Wraps any BaseApiServiceClient with retry logic.
    
    Automatically detects whether provider has built-in retry:
    - If yes: passes through (no double-retry)
    - If no: wraps calls with exponential backoff + jitter
    """
    
    def __init__(
        self,
        service: BaseApiServiceClient,
        orchestrator: Optional[RetryOrchestrator] = None
    ):
        """
        Initialize wrapper.
        
        Args:
            service: BaseApiServiceClient instance to wrap
            orchestrator: RetryOrchestrator instance (creates default if None)
        """
        self.service = service
        self.orchestrator = orchestrator or RetryOrchestrator()
        logger.debug(f"Wrapped {service.provider_id} with retry orchestrator")
    
    async def get_models(self) -> list[ModelMetadata]:
        """
        Get available models with retry.
        
        Returns:
            List of ModelMetadata
        """
        result = await self.orchestrator.execute_with_retry(
            api_call=self.service.get_models,
            provider_id=self.service.provider_id,
        )
        
        if result.success:
            return result.result
        else:
            raise result.error
    
    async def call_llm(
        self,
        model_id: str,
        messages: list[Message],
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
        """
        Call LLM with retry.
        
        Returns AsyncIterator[StreamChunk] if streaming, else LLMResponse.
        """
        result = await self.orchestrator.execute_with_retry(
            api_call=self.service.call_llm,
            provider_id=self.service.provider_id,
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            streaming=streaming,
            **kwargs,
        )
        
        if result.success:
            return result.result
        else:
            raise result.error
    
    @property
    def provider_id(self) -> ProviderType:
        """Proxy to underlying service provider_id."""
        return self.service.provider_id
