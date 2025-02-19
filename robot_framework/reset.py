"""This module handles resetting the state of the computer so the robot can work with a clean slate."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.solteqtand import app_handler
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

from robot_framework.config import APP_PATH
from robot_framework.mysecrets import SOLTEQTAND_USERNAME, SOLTEQTAND_PASSWORD


def reset(orchestrator_connection: OrchestratorConnection) -> None:
    """Clean up, close/kill all programs and start them again. """
    # orchestrator_connection.log_trace("Resetting.")

    clean_up(orchestrator_connection)
    close_all(orchestrator_connection)
    kill_all(orchestrator_connection)
    open_all(orchestrator_connection)


def clean_up(orchestrator_connection: OrchestratorConnection) -> None:
    """Do any cleanup needed to leave a blank slate."""
    # orchestrator_connection.log_trace("Doing cleanup.")
    pass


def close_all(orchestrator_connection: OrchestratorConnection) -> None:
    """Gracefully close all applications used by the robot."""
    # orchestrator_connection.log_trace("Closing all applications.")
    if hasattr(orchestrator_connection, "app"):
        if isinstance(orchestrator_connection.app, SolteqTandApp):
            orchestrator_connection.app.close_solteq_tand()
            print("Lukkede solteq")

def kill_all(orchestrator_connection: OrchestratorConnection,
             solteq_app: SolteqTandApp = None) -> None:
    """Forcefully close all applications used by the robot."""
    # orchestrator_connection.log_trace("Killing all applications.")


def open_all(orchestrator_connection: OrchestratorConnection) -> SolteqTandApp:
    """Open all programs used by the robot."""
    # orchestrator_connection.log_trace("Opening all applications.")
    solteq_app = SolteqTandApp(
        app_path=APP_PATH,
        username=SOLTEQTAND_USERNAME,
        password=SOLTEQTAND_PASSWORD
    )

    solteq_app.start_application()
    solteq_app.login()

    orchestrator_connection.app = solteq_app
