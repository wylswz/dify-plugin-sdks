from typing import Any

import httpx
from pydantic import BaseModel
from yarl import URL

from dify_plugin.core.runtime import BackwardsInvocation, Session

# POST /v2/invoke/backwards-invocation/submit-tool-interrupt-result (X-Api-Key = DIFY_PLUGIN_SERVER_KEY)
_OUT_OF_SESSION_PATH = "v2/invoke/backwards-invocation/submit-tool-interrupt-result"


class SubmitToolInterruptResultResponse(BaseModel):
    accepted: bool


class ToolInterruptSubmissionInvocation(BackwardsInvocation[SubmitToolInterruptResultResponse]):
    @staticmethod
    def _require_out_of_session_context(session: Session | None) -> None:
        s = session
        missing: list[str] = []
        if not s:
            raise RuntimeError(
                "submit_tool_interrupt_result requires a session; session is missing"
            )
        if not s.dify_plugin_daemon_url:
            missing.append("DIFY_PLUGIN_DAEMON_URL")
        if not s.dify_plugin_server_key:
            missing.append("DIFY_PLUGIN_SERVER_KEY (same as daemon SERVER_KEY for /v2/invoke/...)")
        if missing:
            raise RuntimeError(
                "submit_tool_interrupt_result: HTTP to plugin daemon; missing: " + ", ".join(missing)
            )

    def _submit_out_of_session(
        self, *, token: str, result: dict[str, Any]
    ) -> SubmitToolInterruptResultResponse:
        s = self.session
        assert s is not None
        base = s.dify_plugin_daemon_url.rstrip("/")
        url = str(URL(base) / _OUT_OF_SESSION_PATH)
        headers = {
            "X-Api-Key": s.dify_plugin_server_key or "",
            "Content-Type": "application/json",
        }
        body = {
            "token": token,
            "result": result,
        }
        with httpx.Client() as client:
            resp = client.post(
                url,
                json=body,
                headers=headers,
                timeout=float(s.max_invocation_timeout),
            )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            detail = e.response.text
            raise Exception(f"submit_tool_interrupt_out_of_session failed: {e!s}; body={detail!r}") from e
        return SubmitToolInterruptResultResponse.model_validate(resp.json())

    def submit_result(self, *, token: str, result: dict[str, Any]) -> SubmitToolInterruptResultResponse:
        """Resume a paused workflow run; Dify resolves the run from the interrupt token.

        Always uses POST .../v2/invoke/dispatch/backwards-invocation/submit-tool-interrupt-result on
        the daemon (does not use the invoke duplex stream). Call from a background thread after
        the tool invoke has ended is supported.
        """
        self._require_out_of_session_context(self.session)
        return self._submit_out_of_session(token=token, result=result)
