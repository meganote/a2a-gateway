import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class AppIdAgent:
    def __init__(self, app_id: str):
        self._app_id = app_id

    async def invoke(self) -> str:
        return f"--- {self._app_id} --- Hello World"


class AppIdAgentExecutor(AgentExecutor):

    def __init__(self, app_id: str):
        self.agent = AppIdAgent(app_id)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
