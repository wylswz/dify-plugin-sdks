import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.invocations.tool_interrupt import ToolInterruptSubmissionInvocation


class SubmitInterruptResultTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        token = (tool_parameters.get("token") or "").strip()
        if not token:
            yield self.create_text_message("error: token is required")
            return

        result: dict[str, Any] = {}
        text = (tool_parameters.get("result_text") or "").strip()
        if text:
            result["text"] = text

        raw_json = (tool_parameters.get("result_json") or "").strip()
        if raw_json:
            try:
                parsed = json.loads(raw_json)
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"error: result_json is not valid JSON: {e}")
                return
            if not isinstance(parsed, dict):
                yield self.create_text_message("error: result_json must be a JSON object")
                return
            result["json"] = parsed

        inv = ToolInterruptSubmissionInvocation(self.session)
        response = inv.submit_result(token=token, result=result)
        yield self.create_json_message({"accepted": response.accepted, "token": token})
