"""Wrapper to apply retry orchestration to any API service client."""

from collections.abc import AsyncIterator

from css.core.types import (
    BaseApiServiceClient,
    BaseMessage,
    LLMResponse,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    Tool,
)

from .orchestrator import RetryOrchestrator


class RetryWrappedApiService:
    def __init__(
        self,
        service: BaseApiServiceClient,
        orchestrator: RetryOrchestrator | None = None,
    ):
        self.service = service
        self.orchestrator = orchestrator or RetryOrchestrator()

    async def get_models(self) -> list[ModelMetadata]:
        result = await self.orchestrator.execute_with_retry(
            api_call=self.service.get_models,
            provider_id=self.service.provider_id,
        )
        if result.success and result.result is not None:
            return result.result
        if result.error is not None:
            raise result.error
        raise RuntimeError("get_models failed without explicit error")

    async def call_llm(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
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
        if result.success and result.result is not None:
            return result.result
        if result.error is not None:
            raise result.error
        raise RuntimeError("call_llm failed without explicit error")

    @property
    def provider_id(self) -> ProviderType:
        return self.service.provider_id
