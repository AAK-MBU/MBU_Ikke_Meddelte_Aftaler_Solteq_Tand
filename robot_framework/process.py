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
    # orchestrator_connection.log_trace("Running process.")

    # connection_string = orchestrator_connection.get_constant('DbConnectionString').value
    # connection_string = os.getenv('DbConnectionString')  # For testing
    # oc_args_json = json.loads(orchestrator_connection.process_arguments)
    # process_arg = oc_args_json['process']

    # This process runs in the application window
    # The functions to handle the application should be written as generally as possible
    # in mbu_dev_shared_components

    # Set queue variables for SQL
    app = orchestrator_connection.app

    process_queue_element(
        orchestrator_connection=orchestrator_connection,
        queue_element=queue_element,
        solteq_app=app
    )
