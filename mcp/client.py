# mcp/client.py

from typing import Any, Dict

import requests

from config.settings import settings


class MCPClient:
    """Client for ClaimGuard local MCP services."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

        self.endpoints = {
            "tariff": settings.MCP_TARIFF_URL,
            "icd10": settings.MCP_ICD10_URL,
            "calculation": settings.MCP_CALCULATION_URL,
        }

    def call(
        self,
        service: str,
        tool: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:

        if service not in self.endpoints:
            raise ValueError(
                f"Unknown MCP service: {service}"
            )

        url = f"{self.endpoints[service]}/tools/{tool}"

        response = requests.post(
            url,
            json=arguments,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def health_check(self, service: str) -> bool:

        if service not in self.endpoints:
            return False

        try:
            response = requests.get(
                f"{self.endpoints[service]}/health",
                timeout=self.timeout,
            )

            return response.ok

        except requests.RequestException:
            return False


mcp_client = MCPClient()