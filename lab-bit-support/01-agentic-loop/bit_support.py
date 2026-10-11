"""
BitSupport Lab 1
================

Objetivo educativo:
mostrar manualmente el lifecycle de una client-executed tool:

Claude -> tool_use -> runtime -> tool_result -> Claude

No es código production-ready.
"""

from __future__ import annotations

import json
import os
from typing import Any

from anthropic import Anthropic


MAX_TURNS = 6

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def get_deployment_status(service: str, environment: str) -> dict[str, Any]:
    """Fake tool para mantener el lab autocontenido."""

    deployments = {
        ("payments-api", "qa"): {
            "status": "failed",
            "reason": "health check timeout",
        },
        ("payments-api", "prod"): {
            "status": "success",
            "reason": None,
        },
    }

    result = deployments.get((service, environment))

    if result is None:
        return {
            "found": False,
            "service": service,
            "environment": environment,
            "message": "No deployment information found.",
        }

    return {
        "found": True,
        "service": service,
        "environment": environment,
        **result,
    }


TOOLS = [
    {
        "name": "get_deployment_status",
        "description": (
            "Returns the latest known deployment status for one software service "
            "in one environment. Use it when the user asks whether a service "
            "deployment succeeded or failed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name, for example payments-api.",
                },
                "environment": {
                    "type": "string",
                    "enum": ["dev", "qa", "prod"],
                    "description": "Target environment.",
                },
            },
            "required": ["service", "environment"],
        },
    }
]


def execute_tool(name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Runtime dispatch: el model no ejecuta esta función."""

    if name == "get_deployment_status":
        return get_deployment_status(
            service=tool_input["service"],
            environment=tool_input["environment"],
        )

    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": (
                "¿Cuál fue el estado del último deploy de payments-api en QA? "
                "Usá las tools disponibles cuando sean necesarias."
            ),
        }
    ]

    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            tools=TOOLS,
            messages=messages,
        )

        print(f"\nTurn {turn}: stop_reason={response.stop_reason}")

        # Conservamos exactamente la respuesta del assistant para el próximo turn.
        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_calls = [
            block
            for block in response.content
            if block.type == "tool_use"
        ]

        if tool_calls:
            tool_results = []

            for tool_call in tool_calls:
                print(
                    f"Tool requested: {tool_call.name} "
                    f"{json.dumps(tool_call.input, ensure_ascii=False)}"
                )

                result = execute_tool(tool_call.name, tool_call.input)

                print(
                    "Tool result:",
                    json.dumps(result, ensure_ascii=False),
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": tool_results,
                }
            )

            continue

        if response.stop_reason == "end_turn":
            final_text = [
                block.text
                for block in response.content
                if block.type == "text"
            ]

            print("\nFinal answer:")
            print("\n".join(final_text))
            return

        raise RuntimeError(
            f"Unhandled stop_reason={response.stop_reason!r}. "
            "A production runtime should handle each relevant case explicitly."
        )

    raise RuntimeError(
        f"Turn budget exhausted after {MAX_TURNS} turns. "
        "A real system should stop or escalate here."
    )


if __name__ == "__main__":
    main()
