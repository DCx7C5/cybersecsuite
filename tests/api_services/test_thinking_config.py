"""Tests for ThinkingConfig struct."""

import pytest
import msgspec
from css.core.sdks.thinking import ThinkingConfig


class TestThinkingConfigConstruction:
    """Test ThinkingConfig creation and validation."""
    
    def test_thinking_config_default(self):
        """ThinkingConfig can be created with no arguments."""
        config = ThinkingConfig()
        assert config.budget_tokens is None
        assert config.effort is None
    
    def test_thinking_config_with_budget_tokens(self):
        """ThinkingConfig accepts budget_tokens."""
        config = ThinkingConfig(budget_tokens=10000)
        assert config.budget_tokens == 10000
        assert config.effort is None
    
    def test_thinking_config_with_effort(self):
        """ThinkingConfig accepts effort level."""
        for effort in ["low", "medium", "high"]:
            config = ThinkingConfig(effort=effort)
            assert config.effort == effort
    
    def test_thinking_config_with_both_params(self):
        """ThinkingConfig accepts budget_tokens and effort."""
        config = ThinkingConfig(budget_tokens=5000, effort="high")
        assert config.budget_tokens == 5000
        assert config.effort == "high"
    
    def test_thinking_config_invalid_budget_zero(self):
        """ThinkingConfig rejects zero budget_tokens."""
        with pytest.raises(ValueError) as exc_info:
            ThinkingConfig(budget_tokens=0)
        assert "positive" in str(exc_info.value).lower()
    
    def test_thinking_config_invalid_budget_negative(self):
        """ThinkingConfig rejects negative budget_tokens."""
        with pytest.raises(ValueError) as exc_info:
            ThinkingConfig(budget_tokens=-100)
        assert "positive" in str(exc_info.value).lower()
    
    def test_thinking_config_invalid_effort(self):
        """ThinkingConfig rejects invalid effort values."""
        with pytest.raises((TypeError, ValueError)):
            ThinkingConfig(effort="very_high")  # type: ignore
    
    def test_thinking_config_frozen(self):
        """ThinkingConfig is frozen and immutable."""
        config = ThinkingConfig(budget_tokens=1000)
        with pytest.raises((msgspec.ValidationError, AttributeError, TypeError)):
            config.budget_tokens = 2000  # type: ignore


class TestThinkingConfigSerialization:
    """Test ThinkingConfig serialization."""
    
    def test_thinking_config_msgspec_serialize(self):
        """ThinkingConfig serializes with msgspec."""
        config = ThinkingConfig(budget_tokens=5000, effort="medium")
        
        # Encode
        encoded = msgspec.json.encode(config)
        assert b'"budget_tokens"' in encoded
        assert b'5000' in encoded
        assert b'"effort"' in encoded
        assert b'"medium"' in encoded
    
    def test_thinking_config_msgspec_deserialize(self):
        """ThinkingConfig deserializes with msgspec."""
        json_data = b'{"budget_tokens": 7500, "effort": "high"}'
        config = msgspec.json.decode(json_data, type=ThinkingConfig)
        
        assert config.budget_tokens == 7500
        assert config.effort == "high"
    
    def test_thinking_config_none_values_serialize(self):
        """ThinkingConfig with None values serializes correctly."""
        config = ThinkingConfig()
        encoded = msgspec.json.encode(config)
        
        # Should still decode properly
        decoded = msgspec.json.decode(encoded, type=ThinkingConfig)
        assert decoded.budget_tokens is None
        assert decoded.effort is None


class TestThinkingConfigUsage:
    """Test typical usage patterns."""
    
    def test_anthropic_thinking_config(self):
        """Anthropic extended thinking configuration."""
        # Anthropic uses budget_tokens
        config = ThinkingConfig(budget_tokens=10000)
        assert config.budget_tokens == 10000
    
    def test_openai_thinking_config(self):
        """OpenAI reasoning configuration."""
        # OpenAI uses budget_tokens and/or effort
        config = ThinkingConfig(budget_tokens=5000, effort="high")
        assert config.budget_tokens == 5000
        assert config.effort == "high"
    
    def test_low_effort_reasoning(self):
        """Low-effort reasoning without budget limit."""
        config = ThinkingConfig(effort="low")
        assert config.budget_tokens is None
        assert config.effort == "low"
    
    def test_max_effort_thinking(self):
        """Maximum effort thinking with specific budget."""
        config = ThinkingConfig(budget_tokens=32000, effort="high")
        assert config.budget_tokens == 32000
        assert config.effort == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
