"""Handles queue elements"""
import os
import pyodbc

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError, NotMatchingError
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

from robot_framework.exceptions import BusinessError
from robot_framework.mysecrets import SSN
from robot_framework.subprocesses.check_patient import check_patient, ORAppointmentFoundError, NoAppointmentFoundError

import pandas as pd  # For structuring found appointments as data


def process_queue_element(
        orcestrator_connection: OrchestratorConnection,
        queue_element: QueueElement,
        solteq_app: SolteqTandApp
):
    """
    Function to process queue elements in Ikke meddelte aftaler.
    Process changes status of appointments and sends out messages to patient.
    If any business error, queue element is added to a manual list in an SQL database.
    """
    name_var = queue_element.data['Name']
    cpr_var = queue_element.data['SSN']
    orchestrator_reference_var = queue_element.id
    appointment_type_var = ''
    description_var = ''

    # Find the patient
    print("Indtaster CPR og laver opslag")
    try:
        solteq_app.open_patient(SSN)
        # solteq_app.open_tab("Stamkort")
        print("Patientjournalen blev åbnet")
    except Exception as e:
        print("Der skete en fejl da stamkortvinduet ikke blev åbner som forventet")
        raise SystemError from e
    patient_window = solteq_app.app_window

    # Here to check that patient fulfills criteria.
    try:
        try:
            # If OR aftale meddelt: close and put on manual
            appointment_control = check_patient(
                solteq_app=solteq_app,
                SSN=SSN
            )
            solteq_app.change_appointment_status(
                appointment_control=appointment_control,
                set_status='Aftale meddelt',
                send_msg=True
            )
        except ORAppointmentFoundError as e:
            description_var = "'OR aftale meddelt' fundet"
            raise ManualProcessingRequiredError from e
        except NoAppointmentFoundError as e:
            description_var = "Ingen 'Ikke meddelt aftale' fundet"
            raise ManualProcessingRequiredError from e
        except ManualProcessingRequiredError as e:
            description_var = "Advarsel da aftale gemtes"
            raise ManualProcessingRequiredError from e

    # Here we insert information to manual list, if some business exception is found
    except ManualProcessingRequiredError as e:
        # Connects to RPA sql
        print("Tilføjer person til manuel liste")
        rpa_conn_string = os.getenv('DbConnectionStringTest')
        #rpa_conn_string = orchestrator_connection.get_constant()
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

        print("Lukker patientvindue")
        solteq_app.app_window = patient_window
        solteq_app.close_patient_window()

        raise BusinessError from e

    # Close patient at the end of process
    print("Status ændret")
    print("Lukker patientvindue")
    solteq_app.app_window = patient_window
    solteq_app.close_patient_window()
