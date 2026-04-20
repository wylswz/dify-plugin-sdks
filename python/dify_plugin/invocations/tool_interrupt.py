from typing import Any

from pydantic import BaseModel

from dify_plugin.core.entities.invocation import InvokeType
from dify_plugin.core.runtime import BackwardsInvocation


class SubmitToolInterruptResultResponse(BaseModel):
    accepted: bool


class ToolInterruptSubmissionInvocation(BackwardsInvocation[SubmitToolInterruptResultResponse]):
    def submit_result(self, *, token: str, result: dict[str, Any]) -> SubmitToolInterruptResultResponse:
        """Resume a paused workflow run; Dify resolves the run from the interrupt token."""
        for item in self._backwards_invoke(
            InvokeType.SubmitToolInterruptResult,
            SubmitToolInterruptResultResponse,
            {
                "token": token,
                "result": result,
            },
        ):
            return item
        raise RuntimeError("submit_tool_interrupt_result returned no response")
