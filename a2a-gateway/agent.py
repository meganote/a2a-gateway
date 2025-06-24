import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class AgentGateway:
    """Hello World Agent."""

    async def invoke(self) -> str:
        logger.debug(f"invoke...")
        return "Hello World"


class AgentGatewayExecutor(AgentExecutor):

    def __init__(self):
        self.agent = AgentGateway()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        print(f"AgentGateway...")
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")
