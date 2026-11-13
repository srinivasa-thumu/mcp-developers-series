"""End-to-end tests against the existing Part 6 server process."""

import asyncio

import pytest

from client import interact, parse_args


def test_default_customer_id_is_101() -> None:
    assert parse_args([]).customer_id == 101


def test_invalid_customer_id_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse_args(["not-a-number"])
    with pytest.raises(SystemExit):
        parse_args(["0"])


def test_mcp_discovers_tool_and_returns_john() -> None:
    tools, result = asyncio.run(interact(101))

    assert any(tool.name == "get_customer" for tool in tools)
    assert result.isError is False
    assert result.structuredContent == {
        "name": "John",
        "email": "john@example.com",
        "city": "Hyderabad",
    }


def test_mcp_returns_sarah() -> None:
    _, result = asyncio.run(interact(102))

    assert result.isError is False
    assert result.structuredContent == {
        "name": "Sarah",
        "email": "sarah@example.com",
        "city": "Bangalore",
    }


def test_unknown_customer_is_a_tool_error() -> None:
    _, result = asyncio.run(interact(999))

    assert result.isError is True
    assert any(
        "Customer with ID 999 was not found." in block.text
        for block in result.content
        if hasattr(block, "text")
    )
