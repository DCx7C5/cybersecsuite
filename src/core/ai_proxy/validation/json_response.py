"""JSON Response Validation — t142 JSON validation for structured AI responses.

Referenz:
    plan.md t142 — JSON validation
    plan.md t143 — Token optimization
    plan.md t144 — Few-shot examples
    src/ai_proxy/routing/qwen_triage.py — Triage router
"""


import json
import logging
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, Field, ValidationError, field_validator

from utils.deduplication import deduplicate_messages

logger = logging.getLogger("ai_proxy.validation.json_response")

T = TypeVar("T", bound=BaseModel)


class ResponseFormat(str, Enum):
    """Supported response formats for AI providers."""

    json = "json"
    text = "text"
    markdown = "markdown"
    yaml = "yaml"


class JSONValidationError(Exception):
    """Raised when JSON validation fails."""

    pass


class FindingResponse(BaseModel):
    """Structured response model for security findings."""

    finding_id: str = Field(..., description="Unique finding identifier")
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    title: str = Field(..., max_length=256)
    description: str = Field(..., max_length=4096)
    affected_systems: list[str] = Field(default_factory=list)
    remediation: str | None = None
    tags: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level."""
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"Invalid severity: {v}")
        return v.upper()

    @field_validator("affected_systems")
    @classmethod
    def validate_systems(cls, v: list[str]) -> list[str]:
        """Validate affected systems list."""
        if len(v) > 100:
            raise ValueError("Too many affected systems (max 100)")
        return v


class ForensicAnalysisResponse(BaseModel):
    """Structured response for forensic analysis."""

    case_id: str = Field(..., description="Case identifier")
    timeline_events: list[dict[str, Any]] = Field(..., description="Chronological events")
    evidence_summary: str = Field(..., max_length=2000)
    findings: list[FindingResponse]
    chain_of_custody: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)

    @field_validator("timeline_events")
    @classmethod
    def validate_timeline(cls, v: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate timeline events are sorted chronologically."""
        for event in v:
            if "timestamp" not in event:
                raise ValueError("Timeline event missing timestamp")
        return sorted(v, key=lambda e: e.get("timestamp", ""))


class ThreatIntelligenceResponse(BaseModel):
    """Structured response for threat intelligence."""

    indicators: list[dict[str, str]] = Field(..., description="IOC indicators")
    threat_actors: list[str] = Field(default_factory=list)
    ttps: list[str] = Field(default_factory=list)  # Tactics, Techniques, Procedures
    severity_score: float = Field(..., ge=0.0, le=10.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    related_incidents: list[str] = Field(default_factory=list)


class ResponseValidator:
    """Validates and parses structured responses from AI providers."""

    def __init__(self) -> None:
        """Initialize validator."""
        self.logger = logger

    def validate_json_response(self, response: str, model: type[T]) -> T:
        """
        Validate and parse JSON response against model.

        Args:
            response: Raw response string from AI provider
            model: Pydantic model to validate against

        Returns:
            Validated model instance

        Raises:
            JSONValidationError: If validation fails
        """
        try:
            # Try to extract JSON from response
            json_str = self._extract_json(response)

            # Parse JSON
            data = json.loads(json_str)

            # Validate against model
            instance = model.model_validate(data)

            self.logger.debug(f"JSON response validated successfully: {model.__name__}")
            return instance

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise JSONValidationError(f"Invalid JSON: {e}") from e

        except ValidationError as e:
            self.logger.error(f"Pydantic validation failed: {e}")
            raise JSONValidationError(f"Validation error: {e}") from e

        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {e}")
            raise JSONValidationError(f"Unexpected error: {e}") from e

    def _extract_json(self, response: str) -> str:
        """
        Extract JSON from response (handle markdown code blocks).

        Args:
            response: Raw response string

        Returns:
            JSON string

        Raises:
            JSONValidationError: If no valid JSON found
        """
        # Try direct parsing first
        response = response.strip()

        # Handle markdown code blocks
        if response.startswith("```json"):
            json_str = response[7:]  # Skip ```json
            if "```" in json_str:
                json_str = json_str[: json_str.rfind("```")]
            return json_str.strip()

        if response.startswith("```"):
            json_str = response[3:]  # Skip ```
            if "```" in json_str:
                json_str = json_str[: json_str.rfind("```")]
            return json_str.strip()

        # Try to find JSON in response
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            return response[start:end]

        raise JSONValidationError("No valid JSON found in response")

    def validate_batch_responses(
        self, responses: list[str], model: type[T]
    ) -> tuple[list[T], list[str]]:
        """
        Validate multiple responses, collecting errors.

        Args:
            responses: List of response strings
            model: Pydantic model to validate against

        Returns:
            Tuple of (valid_instances, error_messages)
        """
        valid: list[T] = []
        errors: list[str] = []

        for i, response in enumerate(responses):
            try:
                instance = self.validate_json_response(response, model)
                valid.append(instance)
            except JSONValidationError as e:
                errors.append(f"Response {i}: {str(e)}")

        self.logger.info(f"Batch validation: {len(valid)} valid, {len(errors)} errors")
        return valid, errors

    def generate_validation_schema(self, model: type[BaseModel]) -> dict[str, Any]:
        """
        Generate JSON schema for validation.

        Args:
            model: Pydantic model

        Returns:
            JSON schema dict
        """
        return model.model_json_schema()


class TokenOptimizer:
    """t143: Token optimization for reduced API costs."""

    def __init__(self) -> None:
        """Initialize optimizer."""
        self.logger = logger

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Average 4 characters per token (varies by model)
        return max(1, len(text) // 4)

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated text
        """
        if self.estimate_tokens(text) <= max_tokens:
            return text

        # Rough estimate: 4 chars per token
        max_chars = max_tokens * 4
        return text[:max_chars].rsplit(" ", 1)[0] + "..."

    def compress_context(self, context: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Compress conversation context by removing redundant messages.

        Uses shared deduplication utility (utils.deduplication.deduplicate_messages)
        to remove duplicate or similar consecutive messages while preserving order.

        Args:
            context: Conversation history

        Returns:
            Compressed context
        """
        return deduplicate_messages(context)

    def optimize_system_prompt(self, prompt: str, target_tokens: int = 500) -> str:
        """
        Optimize system prompt to fit token limit.

        Args:
            prompt: System prompt
            target_tokens: Target token limit

        Returns:
            Optimized prompt
        """
        # Remove verbose explanations, keep instructions
        lines = prompt.split("\n")
        optimized = []

        for line in lines:
            line = line.strip()

            # Keep short instruction lines
            if 1 <= len(line) <= 200:
                optimized.append(line)

        result = "\n".join(optimized)

        if self.estimate_tokens(result) > target_tokens:
            result = self.truncate_to_tokens(result, target_tokens)

        return result


class FewShotExamples:
    """t144: Few-shot examples for improved response quality."""

    # Security findings few-shot examples
    FINDING_EXAMPLES = [
        {
            "input": "Detected suspicious process spawning behavior on server-01",
            "output": {
                "finding_id": "FIND-2024-001",
                "severity": "HIGH",
                "title": "Suspicious Process Spawning Detected",
                "description": "Process explorer.exe spawned by svchost.exe with unusual arguments",
                "affected_systems": ["server-01"],
                "remediation": "Investigate parent/child process relationship, check for malware",
                "tags": ["process-injection", "command-line-anomaly"],
                "evidence": {
                    "process": "explorer.exe",
                    "parent": "svchost.exe",
                    "command_line": "explorer.exe /x",
                },
            },
        },
        {
            "input": "Multiple failed login attempts from 192.168.1.100",
            "output": {
                "finding_id": "FIND-2024-002",
                "severity": "MEDIUM",
                "title": "Brute Force Login Attempts",
                "description": "50+ failed SSH login attempts over 10 minutes",
                "affected_systems": ["prod-db-01"],
                "remediation": "Block source IP, enforce rate limiting, enable MFA",
                "tags": ["brute-force", "authentication"],
                "evidence": {
                    "source_ip": "192.168.1.100",
                    "failed_attempts": 50,
                    "protocol": "SSH",
                    "time_window": "10 minutes",
                },
            },
        },
    ]

    # Forensic timeline few-shot examples
    TIMELINE_EXAMPLES = [
        {
            "input": "User login, file access, browser activity on workstation",
            "output": [
                {
                    "timestamp": "2024-04-15T08:30:00Z",
                    "event_type": "logon",
                    "description": "User jsmith logged in via RDP",
                    "source": "Security Event 4624",
                },
                {
                    "timestamp": "2024-04-15T08:35:00Z",
                    "event_type": "file_access",
                    "description": "C:\\Users\\jsmith\\Documents\\sensitive.docx accessed",
                    "source": "NTFS Journal",
                },
                {
                    "timestamp": "2024-04-15T08:40:00Z",
                    "event_type": "network",
                    "description": "Browser uploaded file to external domain",
                    "source": "Network PCAP",
                },
            ],
        },
    ]

    # Threat intelligence few-shot examples
    THREAT_INTEL_EXAMPLES = [
        {
            "input": "Analysis of APT28 targeting defense sector",
            "output": {
                "indicators": [
                    {
                        "type": "ipv4",
                        "value": "185.25.51.5",
                        "confidence": "high",
                    },
                    {
                        "type": "domain",
                        "value": "update-center.ru",
                        "confidence": "medium",
                    },
                    {
                        "type": "file_hash",
                        "value": "d131dd02c5e6eec4693d61a8d32a9f461fc0a62a",
                        "confidence": "high",
                    },
                ],
                "threat_actors": ["APT28", "Fancy Bear"],
                "ttps": [
                    "Initial Access: Spearphishing",
                    "Execution: Malware",
                    "Persistence: Registry Run Keys",
                ],
                "severity_score": 8.5,
                "confidence": 0.85,
                "sources": ["MITRE", "CrowdStrike", "Mandiant"],
                "related_incidents": ["INC-2024-0156", "INC-2024-0157"],
            },
        },
    ]

    @classmethod
    def get_finding_examples(cls, limit: int = 2) -> list[dict[str, Any]]:
        """Get few-shot examples for finding analysis."""
        return cls.FINDING_EXAMPLES[:limit]

    @classmethod
    def get_timeline_examples(cls, limit: int = 1) -> list[dict[str, Any]]:
        """Get few-shot examples for timeline construction."""
        return cls.TIMELINE_EXAMPLES[:limit]

    @classmethod
    def get_threat_intel_examples(cls, limit: int = 1) -> list[dict[str, Any]]:
        """Get few-shot examples for threat intelligence."""
        return cls.THREAT_INTEL_EXAMPLES[:limit]

    @classmethod
    def build_few_shot_prompt(
        cls, task_type: str, examples_count: int = 2
    ) -> str:
        """
        Build few-shot prompt with examples.

        Args:
            task_type: Type of task (finding, timeline, threat_intel)
            examples_count: Number of examples to include

        Returns:
            Formatted few-shot prompt
        """
        if task_type == "finding":
            examples = cls.get_finding_examples(examples_count)
            header = "## Security Finding Examples\n\n"
        elif task_type == "timeline":
            examples = cls.get_timeline_examples(examples_count)
            header = "## Timeline Construction Examples\n\n"
        elif task_type == "threat_intel":
            examples = cls.get_threat_intel_examples(examples_count)
            header = "## Threat Intelligence Analysis Examples\n\n"
        else:
            return ""

        prompt = header

        for i, example in enumerate(examples, 1):
            prompt += f"### Example {i}:\n"
            prompt += f"**Input:** {example['input']}\n\n"
            prompt += f"**Output:**\n```json\n{json.dumps(example['output'], indent=2)}\n```\n\n"

        return prompt
