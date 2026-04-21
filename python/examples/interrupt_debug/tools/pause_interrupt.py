import uuid
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PauseInterruptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        preface = (tool_parameters.get("preface") or "").strip()
        if preface:
            yield self.create_text_message(preface)

        raw_token = tool_parameters.get("token")
        token = (raw_token or "").strip() or uuid.uuid4().hex
        yield self.create_interrupt_message(token)
