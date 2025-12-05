"""
Tests for the base agent.
"""

import pytest
from src.agents.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent implementation for testing."""
    
    async def execute(self, input_data):
        """Test implementation."""
        return {"result": "test"}


@pytest.mark.asyncio
async def test_base_agent_initialization():
    """Test base agent initialization."""
    agent = MockAgent("TestAgent")
    assert agent.name == "TestAgent"
    assert agent.config == {}


@pytest.mark.asyncio
async def test_base_agent_with_config():
    """Test base agent with configuration."""
    config = {"param1": "value1"}
    agent = MockAgent("TestAgent", config)
    assert agent.config == config


@pytest.mark.asyncio
async def test_validate_input_success():
    """Test successful input validation."""
    agent = MockAgent("TestAgent")
    input_data = {"field1": "value1", "field2": "value2"}
    assert agent.validate_input(input_data, ["field1", "field2"])


@pytest.mark.asyncio
async def test_validate_input_missing_field():
    """Test input validation with missing field."""
    agent = MockAgent("TestAgent")
    input_data = {"field1": "value1"}
    
    with pytest.raises(ValueError, match="Missing required fields"):
        agent.validate_input(input_data, ["field1", "field2"])


@pytest.mark.asyncio
async def test_execute():
    """Test agent execute method."""
    agent = MockAgent("TestAgent")
    result = await agent.execute({})
    assert result == {"result": "test"}
