"""This module contains the main process of the robot."""

# import os
# import json
# import time

# import uiautomation as auto

import os
import pyodbc

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand import app_handler
from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError

import pandas as pd  # For structuring found appointments as data

from robot_framework.config import APP_PATH
from robot_framework.mysecrets import SOLTEQTAND_USERNAME, SOLTEQTAND_PASSWORD, SSN


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
        pass

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

        # Set queue variables for SQL
        nameVar = 'Name from queue element'
        cprVar = f'{SSN}'
        appointmentTypeVar = ''
        descriptionVar = ''

        # Find the patient
        solteq_app.open_patient(SSN)

        # Check age and remove parents as message receivers, if above 18

        # Get list of appointments
        appointments = solteq_app.get_list_of_appointments()
        appointments_df = pd.DataFrame(appointments)
        appointments_df['Starttid'] = pd.to_datetime(
            appointments_df['Starttid'],
            format='%d-%m-%Y %H:%M')
        appointments_df.sort_values(
            by='Starttid',
            ascending=True,
            inplace=True
        )

        print(appointments_df[['Starttid', 'Status', 'Klinik']])

        # Here to check if there is an "OR aftale meddelt".
        # if so: close and put on manuel list
        try:
            if "OR aftale meddelt" in appointments["Status"]:
                print("Should not handle this person")
                descriptionVar = '"OR aftale meddelt" fundet'
                raise ManualProcessingRequiredError
            try:
                first_ikke_meddelt = appointments_df[
                    (
                        (appointments_df['Status'] == "Ikke meddelt aftale") &
                        (appointments_df['Klinik'] == "121"))
                ].index[0]
                appointment_control = appointments["controls"][first_ikke_meddelt]

                if "Ikke meddelt aftale" in appointments["Status"]:
                    print("Handling this person")
                    try:
                        solteq_app.change_appointment_status(
                            appointment_control=appointment_control,
                            set_status='Afbud OK',
                            send_msg=True
                        )
                    except ManualProcessingRequiredError as exc:
                        descriptionVar = 'Fejl ved ændring af status'
                        raise ManualProcessingRequiredError from exc
            except IndexError as e:
                print(e)
                print("No 'Ikke meddelt aftale' found")
                descriptionVar = 'Ingen "Ikke meddelt aftale" fundet'
                raise ManualProcessingRequiredError from e
        except ManualProcessingRequiredError:
            print("[Todo: Add patient to manual list]")
            rpa_conn_string = os.getenv('DbConnectionStringTest')
            rpa_conn = pyodbc.connect(rpa_conn_string)
            cursor = rpa_conn.cursor()

            try:
                query = """
                    USE [RPA]

                    INSERT INTO [rpa].[MBU006IkkeMeddelteAftaler]
                        (Name,
                         CPR,
                         AppointmentType,
                         Description,
                         OrchestratorTransactionNumber,
                         OrchestratorReference)
                    VALUES
                        (?, ?, ?, ?, ?, ?)
                """
                cursor.execute(
                    query,
                    (
                        nameVar,
                        cprVar,
                        appointmentTypeVar,
                        descriptionVar,
                        '',
                        ''
                    ))
                rpa_conn.commit()
            except pyodbc.Error as e:
                print(e)
            finally:
                rpa_conn.close()
        print("")


if __name__ == "__main__":
    process(
        orchestrator_connection=None,
        queue_element=None
    )
