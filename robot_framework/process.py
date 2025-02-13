"""This module contains the main process of the robot."""

# import os
# import json
# import time

# import uiautomation as auto

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand import app_handler, db_handler

from robot_framework.config import APP_PATH
from robot_framework.secrets import SOLTEQTAND_USERNAME, SOLTEQTAND_PASSWORD, SSN


# pylint: disable-next=unused-argument
def process(orchestrator_connection: OrchestratorConnection, queue_element: QueueElement | None = None) -> None:
    """Do the primary process of the robot."""
    # orchestrator_connection.log_trace("Running process.")

    # connection_string = orchestrator_connection.get_constant('DbConnectionString').value
    # connection_string = os.getenv('DbConnectionString')  # For testing
    # oc_args_json = json.loads(orchestrator_connection.process_arguments)
    # process_arg = oc_args_json['process']
    process_arg = "handle_queue_elements"

    if process_arg == "get_queue_elements":
        # This process can possibly be handled through the Solteq SQL database
        # Here the relevant ssn's are collected and uploaded as queue elements to OpenOrchestrator
        solteq_db = db_handler.SolteqTandDatabase(
            conn_str='',
            ssn=None  # Getting the initial list of patients with "ikke meddelte aftaler" has no specific SSN
        )
        solteq_db
        # raw_list = solteq_db.check_if_booking_exists(

        # )  # Test this on remote desktop

    if process_arg == "handle_queue_elements":
        # This process runs in the application window
        # The functions to handle the application should be written as generally as possible
        # in mbu_dev_shared_components
        solteq_app = app_handler.SolteqTandApp(
            app_path=APP_PATH,
            username=SOLTEQTAND_USERNAME,
            password=SOLTEQTAND_PASSWORD
        )

        # Open Solteq Tand # Should be in initialization.py
        solteq_app.start_application()

        # Login to Solteq Tand
        solteq_app.login()

        # Find the patient
        solteq_app.open_patient(SSN)

        # Check age and remove parents as message receivers, if above 18

        # Get list of appointments
        appointments = solteq_app.get_list_of_appointments()

        # Here to check if there is an "OR aftale meddelt".
        # if so: close and put on manuel list

        solteq_app.change_appointment_status(
            appointment_control=appointments['controls'][0],
            set_status='Afbud OK'
        )

        print("")

        if "OR aftale meddelt" in appointments["Status"]:
            print("Should not handle this person")
        else:
            if "Aftale ikke meddelt" in appointments["Status"]:
                print("Should handle this person")


if __name__ == "__main__":
    process(
        orchestrator_connection=None,
        queue_element=None
    )
