"""Generate queue"""
import os
import pyodbc

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError, NotMatchingError
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp


def generate_queue(
        orchestrator_connection: OrchestratorConnection,
        solteq_app: SolteqTandApp
):
    
    print(f"Henter ikke meddelte aftaler for {start_next_month} til {end_next_month}")