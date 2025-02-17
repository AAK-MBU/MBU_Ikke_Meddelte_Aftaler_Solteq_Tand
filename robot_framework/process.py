"""This module contains the main process of the robot."""

# import os
# import json
# import time

# import uiautomation as auto

import os
import pyodbc

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from robot_framework.exceptions import BusinessError

from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

import pandas as pd  # For structuring found appointments as data

from robot_framework.mysecrets import SSN


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
    process_arg = "handle_queue_elements"

    if process_arg == "get_queue_elements":
        # This process can possibly be handled through the Solteq SQL database,
        # though it's difficult to find the booking table that matches "Aftalebog" info from UI
        # Here the relevant ssn's are collected and uploaded as queue elements to OpenOrchestrator
        pass

    if process_arg == "handle_queue_elements":
        # This process runs in the application window
        # The functions to handle the application should be written as generally as possible
        # in mbu_dev_shared_components

        # Set queue variables for SQL
        name_var = queue_element.data['Name']
        cpr_var = queue_element.data['SSN']
        orchestrator_reference_var = queue_element.id
        appointment_type_var = ''
        description_var = ''

        solteq_app = app

        # Find the patient
        solteq_app.open_patient(SSN)
        patient_window = solteq_app.app_window

        # Check age and remove parents as message receivers, if above 18

        # Get list of appointments
        appointments = solteq_app.get_list_of_appointments()
        # Wrap code below in function appointments_as_df(self,sort: str | None = None)
        appointments_df = pd.DataFrame(appointments)  # As dataframe
        appointments_df['Starttid'] = pd.to_datetime(
            appointments_df['Starttid'],
            format='%d-%m-%Y %H:%M')  # Format as timestamps
        appointments_df.sort_values(
            by='Starttid',
            ascending=True,
            inplace=True  # Sort first to latest (to find first ikke-meddelt)
        )

        # Here to check if there is an "OR aftale meddelt".
        try:
            # If OR aftale meddelt: close and put on manual
            if "OR Aftale meddelt" in appointments["Status"]:
                print("Should not handle this person")
                description_var = '"OR Aftale meddelt" fundet'
                raise ManualProcessingRequiredError
            
            # If no OR aftale meddelt, attemp to change status and send message
            try:
                first_ikke_meddelt = appointments_df[
                    (
                        (appointments_df['Status'] == "Ikke meddelt aftale") &
                        (appointments_df['Klinik'] == "121"))
                ].index[0]
                appointment_control = appointments["controls"][first_ikke_meddelt]

                # If Ikke meddelt aftale found, change status of first, and send message
                if "Ikke meddelt aftale" in appointments["Status"]:
                    print("Handling this person")
                    try:
                        solteq_app.change_appointment_status(
                            appointment_control=appointment_control,
                            set_status='Aftale meddelt',
                            send_msg=True
                        )
                    # If status change fails: Put on manual list
                    except ManualProcessingRequiredError as exc:
                        description_var = 'Fejl ved ændring af status'
                        raise ManualProcessingRequiredError from exc
            # If no Ikke meddelt aftale found, put on manual list
            except IndexError as e:
                print("No 'Ikke meddelt aftale' found")
                description_var = 'Ingen "Ikke meddelt aftale" fundet'
                raise ManualProcessingRequiredError from e
            
        # Here we insert information to manual list, if some business exception is found
        except ManualProcessingRequiredError as e:
            # Connects to RPA sql
            rpa_conn_string = os.getenv('DbConnectionStringTest')
            rpa_conn = pyodbc.connect(rpa_conn_string)
            cursor = rpa_conn.cursor()

            # Inserts information in database
            try:
                query = """
                    USE [RPA]

                    INSERT INTO [rpa].[MBU006IkkeMeddelteAftaler]
                        (Name,
                         CPR,
                         AppointmentType,
                         Description,
                         OrchestratorTransactionNumber,
                         OrchestratorReference,
                         Date)
                    VALUES
                        (?, ?, ?, ?, ?, ?, GetDate())
                """
                cursor.execute(
                    query,
                    (
                        name_var,
                        cpr_var,
                        appointment_type_var,
                        description_var,
                        '',
                        orchestrator_reference_var
                    ))
                rpa_conn.commit()
            except pyodbc.Error as exc:
                print(exc)
            finally:
                rpa_conn.close()

            patient_window.SetFocus()
            solteq_app.close_patient_window()

            raise BusinessError from e

        # Close patient at the end of process
        print("Ready to close patient")
        solteq_app.close_patient_window()


if __name__ == "__main__":
    process(
        orchestrator_connection=None,
        queue_element=None
    )
