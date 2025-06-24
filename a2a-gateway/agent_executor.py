import logging
import traceback
from typing import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    FilePart,
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from a2a.utils.errors import ServerError

from .agent import AppIdAgent

logger = logging.getLogger(__name__)


class AppIdAgentExecutor(AgentExecutor):
    SUPPORTED_INPUT_TYPES = [
        "text/plain",
        "application/pdf",
        "application/msword",
        "image/png",
        "image/jpeg",
    ]
    SUPPORTED_OUTPUT_TYPES = ["text", "text/plain"]

    def __init__(self, app_id: str):
        self.agent = AppIdAgent(app_id)

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        context_id = context.context_id
        task_id = context.task_id
        try:
            logger.info(f"Starting new session {context_id}")

            updater = TaskUpdater(event_queue, task_id, context_id)
            await updater.submit()

            async for event in self.agent.stream(query, context_id):
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(event["content"], context_id, task_id),
                )

            await updater.add_artifact(
                [Part(root=TextPart(text="TEXT_PART"))],
                name="final_answer",
            )

            await updater.complete()

        except Exception as e:
            logger.error(f"An error occurred while streaming the response: {e}")
            logger.error(traceback.format_exc())
            raise ServerError(
                error=InternalError(
                    message=f"An error occurred while streaming the response: {e}"
                )
            )

        # query = context.get_user_input()
        # task = context.current_task

        # if not context.message:
        #     raise Exception("No message provided")

        # if not task:
        #     task = new_task(context.message)
        #     await event_queue.enqueue_event(task)

        # # stream agent
        # async for event in self.agent.stream(query, task.contextId):
        #     if event["is_task_complete"]:
        #         await event_queue.enqueue_event(
        #             TaskArtifactUpdateEvent(
        #                 append=False,
        #                 contextId=task.contextId,
        #                 taskId=task.id,
        #                 lastChunk=True,
        #                 artifact=new_text_artifact(
        #                     name="final_answer",
        #                     description="Result of request to agent",
        #                     text=event["content"],
        #                 ),
        #             )
        #         )
        #         await event_queue.enqueue_event(
        #             TaskStatusUpdateEvent(
        #                 status=TaskStatus(state=TaskState.completed),
        #                 final=True,
        #                 contextId=task.contextId,
        #                 taskId=task.id,
        #             )
        #         )
        #     elif event["require_user_input"]:
        #         await event_queue.enqueue_event(
        #             TaskStatusUpdateEvent(
        #                 status=TaskStatus(
        #                     state=TaskState.input_required,
        #                     message=new_agent_text_message(
        #                         event["content"],
        #                         task.contextId,
        #                         task.id,
        #                     ),
        #                 ),
        #                 final=True,
        #                 contextId=task.contextId,
        #                 taskId=task.id,
        #             )
        #         )
        #     else:
        #         await event_queue.enqueue_event(
        #             TaskStatusUpdateEvent(
        #                 status=TaskStatus(
        #                     state=TaskState.working,
        #                     message=new_agent_text_message(
        #                         event["content"],
        #                         task.contextId,
        #                         task.id,
        #                     ),
        #                 ),
        #                 final=False,
        #                 contextId=task.contextId,
        #                 taskId=task.id,
        #             )
        #         )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")

    # def _validate_request(self, context: RequestContext) -> bool:
    #     """True means invalid, false is valid."""
    #     invalidOutput = self._validate_output_modes(
    #         context, self.SUPPORTED_OUTPUT_TYPES
    #     )
    #     return invalidOutput or self._validate_push_config(context)

    # def _get_input_event(self, context: RequestContext) -> InputEvent:
    #     """Extract file attachment if present in the message parts."""
    #     file_data = None
    #     file_name = None
    #     text_parts = []
    #     for p in context.message.parts:
    #         part = p.root
    #         if isinstance(part, FilePart):
    #             file_data = part.file.bytes
    #             file_name = part.file.name
    #             if file_data is None:
    #                 raise ValueError("File data is missing!")
    #         elif isinstance(part, TextPart):
    #             text_parts.append(part.text)
    #         else:
    #             raise ValueError(f"Unsupported part type: {type(part)}")

    #     return InputEvent(
    #         msg="\n".join(text_parts),
    #         attachment=file_data,
    #         file_name=file_name,
    #     )

    # def _validate_output_modes(
    #     self,
    #     context: RequestContext,
    #     supportedTypes: list[str],
    # ) -> bool:
    #     acceptedOutputModes = (
    #         context.configuration.acceptedOutputModes if context.configuration else []
    #     )
    #     if not are_modalities_compatible(
    #         acceptedOutputModes,
    #         supportedTypes,
    #     ):
    #         logger.warning(
    #             "Unsupported output mode. Received %s, Support %s",
    #             acceptedOutputModes,
    #             supportedTypes,
    #         )
    #         return True
    #     return False

    # def _validate_push_config(
    #     self,
    #     context: RequestContext,
    # ) -> bool:
    #     pushNotificationConfig = (
    #         context.configuration.pushNotificationConfig
    #         if context.configuration
    #         else None
    #     )
    #     if pushNotificationConfig and not pushNotificationConfig.url:
    #         logger.warning("Push notification URL is missing")
    #         return True

    #     return False
