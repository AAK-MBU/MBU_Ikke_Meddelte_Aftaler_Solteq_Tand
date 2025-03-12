"""This module contains the main process of the robot."""
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

from robot_framework.subprocesses.handle_queue import process_queue_element


# pylint: disable-next=unused-argument
def process(
        orchestrator_connection: OrchestratorConnection,
        queue_element: QueueElement | None = None,
        app: SolteqTandApp | None = None) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    # Set queue variables for SQL
    app = orchestrator_connection.app

    process_queue_element(
        orchestrator_connection=orchestrator_connection,
        queue_element=queue_element,
        solteq_app=app
    )
