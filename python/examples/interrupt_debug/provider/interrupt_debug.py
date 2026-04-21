from typing import Any

from dify_plugin import ToolProvider


class InterruptDebugProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        _ = credentials.get("noop_note")
