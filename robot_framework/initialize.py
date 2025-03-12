"""This module defines any initial processes to run when the robot starts."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from robot_framework import reset
from robot_framework.subprocesses.generate_queue import generate_queue


def initialize(orchestrator_connection: OrchestratorConnection) -> None:
    """Do all custom startup initializations of the robot."""
    orchestrator_connection.log_trace("Initializing.")

    reset.reset(orchestrator_connection)

    app = orchestrator_connection.app

    # Opens SolteqTand and retrieves the patients that should be modified
    generate_queue(
        orchestrator_connection=orchestrator_connection,
        solteq_app=app
    )
