from fastmcp import FastMCP

import os
import httpx

from cachetools import cached, TTLCache
from urllib.parse import urljoin
from typing import Annotated
from pydantic import Field

from rsshub_mcp.type import NamespaceItem

RSSHUB_INSTANCE_URL = os.getenv("RSSHUB_INSTANCE_URL", "https://rsshub.app")
CACHE_TTL = int(os.getenv("CACHE_TTL", 600))
CACHE_SIZE = int(os.getenv("CACHE_SIZE", 1024))

mcp = FastMCP("RSSHub-MCP")

@cached(cache=TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL))
async def get_rsshub_namespaces(
    instance_url: str = RSSHUB_INSTANCE_URL,
) -> dict[str, NamespaceItem]:
    async with httpx.AsyncClient() as client:
        response = await client.get(urljoin(instance_url, "/api/namespace"))
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch RSSHub namespaces: {response.status_code} {response.text}"
            )
        data = response.json()
        return {k: NamespaceItem.model_validate(v) for k, v in data.items()}


@mcp.tool(
    name="list_namespaces",
    description="List all RSSHub namespaces and brief description of routes",
)
async def list_namespaces() -> list[dict]:
    """List all RSSHub namespaces and routes"""
    namespaces = await get_rsshub_namespaces()
    return [
        {
            "namespace": k,
            "routes": [
                {
                    key: value
                    for key, value in route.model_dump().items()
                    if key in set(["name", "path", "description"]) and value is not None
                }
                for route in v.routes.values()
            ],
        }
        for k, v in namespaces.items()
    ]


@mcp.tool(
    name="search_namespace",
    description="Search for a specific RSSHub namespace and get its details routes",
)
async def search_namespace(
    namespace: Annotated[str, Field(description="Namespace to search for")],
) -> list[dict]:
    """Search for a specific RSSHub namespace and get its detailed routes"""
    namespaces = await get_rsshub_namespaces()
    return [
        {
            "namespace": k,
            "routes": [
                {
                    key: value
                    for key, value in route.model_dump().items()
                    if key
                    in set(
                        ["name", "path", "description", "example", "url", "parameters"]
                    )
                    and value is not None
                }
                for route in v.routes.values()
            ],
        }
        for k, v in namespaces.items()
        if k == namespace
    ]


@mcp.resource("rsshub://{path*}")
async def get_rsshub_feed(path: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            urljoin(RSSHUB_INSTANCE_URL, path), timeout=30.0, params={"format": "json"}
        )
        return response.text


@mcp.prompt(
    name="find_rsshub_route",
    description="Find the RSSHub route for a given task",
)
async def find_rsshub_route(
    task: Annotated[str, Field(description="Task to find the RSSHub route for")],
) -> str:
    return f"Please find the RSSHub route for the task: {task}. The route should be in the format of 'rsshub://namespace/route...'."

