"""This module defines any finalizing processes to run when the robot ends."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from robot_framework.subprocesses.handle_manual_list import delete_temp_files, create_excel_sheet, send_manual_list
from robot_framework.exceptions import handle_error
from robot_framework.subprocesses.call_database import get_queue


class QueueNotEmptyError(Exception):
    """Exception to handle non-empty queue"""
    def __init__(self, message="Error wile creating manual list. Queue not empty."):
        super().__init__(message)


def finalize(
        orchestrator_connection: OrchestratorConnection
):
    """Function to finalize robot process by preparing and sending manual list as excel"""
    orchestrator_connection.log_trace("Finalizing.")
    try:
        queue = get_queue(
            orchestrator_connection=orchestrator_connection,
            queue='solteqtand_ikke_meddelte_aftaler'
        )
        if len(queue) != 0:
            raise QueueNotEmptyError(
                message=f"Køen var ikke tom da den manuelle liste skulle dannes men indeholdte {len(queue)} elementer."
            )

        delete_temp_files(
            orchestrator_connection=orchestrator_connection
        )

        filepath = create_excel_sheet(
            orchestrator_connection=orchestrator_connection
        )

        send_manual_list(
            orchestrator_connection=orchestrator_connection,
            filepath=filepath
        )

        delete_temp_files(
            orchestrator_connection=orchestrator_connection
        )

    except QueueNotEmptyError as e:
        handle_error(
            message="Manual list not sent.",
            error=e,
            queue_element=None,
            orchestrator_connection=orchestrator_connection
        )

    except Exception as e:
        handle_error(
            message="Error while sending manual list",
            error=e,
            queue_element=None,
            orchestrator_connection=orchestrator_connection
        )
