"""This module handles resetting the state of the computer so the robot can work with a clean slate."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.solteqtand import app_handler
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

from robot_framework.config import APP_PATH
from robot_framework.mysecrets import SOLTEQTAND_USERNAME, SOLTEQTAND_PASSWORD

def reset(orchestrator_connection: OrchestratorConnection, solteq_app: SolteqTandApp = None) -> None:
    """Clean up, close/kill all programs and start them again. """
    # orchestrator_connection.log_trace("Resetting.")

    clean_up(orchestrator_connection, solteq_app)
    close_all(orchestrator_connection, solteq_app)
    kill_all(orchestrator_connection)
    solteq_app = open_all(orchestrator_connection)
    return solteq_app


def clean_up(orchestrator_connection: OrchestratorConnection,
             solteq_app: SolteqTandApp = None) -> None:
    """Do any cleanup needed to leave a blank slate."""
    # orchestrator_connection.log_trace("Doing cleanup.")
    # if solteq_app:
    #     try:
    #         print("Trying to close patient window")
    #         solteq_app.close_patient_window()
    #         print("Patient window might be closed")
    #         import time
    #         time.sleep(2)
    #     except Exception as e:
    #         print(e)
    #         pass


def close_all(orchestrator_connection: OrchestratorConnection,
             solteq_app: SolteqTandApp = None) -> None:
    """Gracefully close all applications used by the robot."""
    # orchestrator_connection.log_trace("Closing all applications.")
    # if solteq_app:
    #     try:
    #         print("Trying to close app")
    #         solteq_app.close_solteq_tand()
    #         print("App might be closed")
    #         import time
    #         time.sleep(2)
    #     except Exception as e:
    #         print(e)
    #         pass


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

    return solteq_app
