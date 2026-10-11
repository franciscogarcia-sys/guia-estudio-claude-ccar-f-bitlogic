"""
Lab educativo: agentic loop mínimo con un client tool.

Requiere:
    pip install anthropic
    export ANTHROPIC_API_KEY=...

El ejemplo evita esconder el loop para que sea visible:
model -> tool_use -> runtime -> tool_result -> model.
"""

from __future__ import annotations

import os
from anthropic import Anthropic


MAX_TURNS = 6

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def get_inventory(sku: str) -> dict:
    """Fake business tool used only for the lab."""
    inventory = {
        "ABC-123": 7,
        "XYZ-999": 0,
    }
    return {
        "sku": sku,
        "stock": inventory.get(sku, 0),
    }


TOOLS = [
    {
        "name": "get_inventory",
        "description": (
            "Returns the current inventory count for one product SKU. "
            "Use it when the user asks whether a product is currently in stock."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Product SKU to look up.",
                }
            },
            "required": ["sku"],
        },
    }
]


def execute_tool(name: str, tool_input: dict) -> dict:
    if name == "get_inventory":
        return get_inventory(tool_input["sku"])
    raise ValueError(f"Unknown tool: {name}")


def run() -> None:
    messages = [
        {
            "role": "user",
            "content": (
                "¿Hay stock del producto ABC-123? "
                "Usá la herramienta disponible si la necesitás."
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

        print(f"Turn {turn}: stop_reason={response.stop_reason}")

        # Preserve the assistant response in conversation state.
        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_uses = [block for block in response.content if block.type == "tool_use"]

        if tool_uses:
            tool_results = []

            for tool_call in tool_uses:
                result = execute_tool(tool_call.name, tool_call.input)
                print(f"  Tool: {tool_call.name}({tool_call.input}) -> {result}")

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": str(result),
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
            text_blocks = [
                block.text for block in response.content if block.type == "text"
            ]
            print("\nFinal answer:")
            print("\n".join(text_blocks))
            return

        raise RuntimeError(
            f"Unhandled stop_reason: {response.stop_reason}. "
            "A production runtime should handle this explicitly."
        )

    raise RuntimeError(
        f"Turn budget exhausted ({MAX_TURNS}). "
        "A production system should stop or escalate here."
    )


if __name__ == "__main__":
    run()
