import json
import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, APIKeySecurityScheme
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette_context import plugins
from starlette_context.middleware import ContextMiddleware

from .agent_executor import AppIdAgentExecutor

logger = logging.getLogger(__name__)
load_dotenv()


def create_app(app_id: str) -> A2AStarletteApplication:
    print(f"--- {app_id} ---")
    base_url = f"http://localhost:9999/{app_id}/"
    # api_key_scheme = APIKeySecurityScheme(in_="header", name="authentication")

    # get app info
    skill = AgentSkill(
        id="hello_world",
        name="Returns hello world",
        description="just returns hello world",
        tags=["hello world"],
        examples=["hi", "hello world"],
    )

    public_agent_card = AgentCard(
        name=app_id,
        description="Just a hello world agent",
        url=base_url,
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],  # Only the basic skill for the public card
        supportsAuthenticatedExtendedCard=False,
        # securitySchemes={"api_key": api_key_scheme},
    )

    request_handler = DefaultRequestHandler(
        agent_executor=AppIdAgentExecutor(app_id=app_id),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    app.build(
        agent_card_url=f"/{app_id}/.well-known/agent.json",
        rpc_url=f"/{app_id}",
        extended_agent_card_url=f"/{app_id}/agent/authenticatedExtendedCard",
    )
    return app


if __name__ == "__main__":
    middleware = [
        Middleware(
            ContextMiddleware,
            plugins=(plugins.ApiKeyPlugin(),),
        )
    ]
    server = Starlette(middleware=middleware)

    app_ids = json.loads(os.getenv("APP_IDS", "[]"))
    for app_id in app_ids:
        app = create_app(app_id=app_id)
        print(f"--- Mount: {app_id} ---")
        server.routes.append(Mount(f"/{app_id}", routes=app.routes()))

    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(server, host="0.0.0.0", port=9999, log_level="debug")
