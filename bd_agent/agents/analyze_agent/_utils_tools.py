# analyze_agent/utils_tools.py
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ToolCallPart,
    ToolReturnPart,
)

# Din egen modell (du har redan denna i bd.bd_models)
from bd_agent.bd.models import (
    ToolCall,  # name: str, args: dict, output_preview: str|None, called_at: datetime|None
)


def extract_tools_metadata(
    result: AgentRunResult, known_tool_names: Set[str] | None = None
) -> Tuple[List[str], List[ToolCall]]:
    """
    Skannar meddelandehistoriken och returnerar:
      - tools_used: unika tool-namn i körningen (exkl. ev. output-tool)
      - tool_calls: detaljerad lista över tool-anrop (namn, args, output-preview, timestamp)
    """
    msgs: List[ModelMessage] = result.all_messages()
    tools_used: List[str] = []
    calls: List[ToolCall] = []

    # Koppla ihop call -> return via tool_call_id
    pending: Dict[str, ToolCall] = {}

    for msg in msgs:
        if isinstance(msg, ModelResponse):
            # Tool CALLs kommer från modellen
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    # Filtrera till dina riktiga funktionsverktyg om du vill
                    if known_tool_names and part.tool_name not in known_tool_names:
                        continue
                    tc = ToolCall(
                        name=part.tool_name,
                        args=part.args_as_dict(),  # robust parsning oavsett str/dict
                        output_preview=None,
                        called_at=getattr(msg, "timestamp", None),
                    )
                    calls.append(tc)
                    tools_used.append(part.tool_name)
                    pending[part.tool_call_id] = tc

        elif isinstance(msg, ModelRequest):
            # Tool RETURNs skickas från din app tillbaka till modellen
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    tc = pending.get(part.tool_call_id)
                    if tc:
                        # Gör en kort "preview" av tool-output (som text)
                        preview = (
                            part.model_response_str()
                        )  # konverterar till text på ett kompatibelt sätt
                        if preview and len(preview) > 300:
                            preview = preview[:300] + "…"
                        tc.output_preview = preview

    # Unika tool-namn i ordning
    seen = set()
    tools_used = [t for t in tools_used if not (t in seen or seen.add(t))]

    return tools_used, calls
