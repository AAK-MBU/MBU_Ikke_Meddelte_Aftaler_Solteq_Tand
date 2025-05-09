"""Handles queue elements"""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand.app_handler import (
    ManualProcessingRequiredError,
    NotMatchingError,
    PatientNotFoundError,
)
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp

from robot_framework.exceptions import BusinessError
from robot_framework.subprocesses.check_patient import (
    check_patient,
    ORAppointmentFoundError,
    NoAppointmentFoundError,
)
from robot_framework.subprocesses.call_database import insert_manual_list
from robot_framework.subprocesses.generate_queue import get_start_end_dates


def get_sql_info(queue_element):
    """Function to get SQL info for manual list from queue element"""
    import json
    queue_element.data = json.loads(queue_element.data)
    sql_info = {
        "name_var": queue_element.data["Navn"],
        "cpr_var": queue_element.data["Cpr"],
        "orchestrator_reference_var": queue_element.id,
        "appointment_type_var": queue_element.data["Aftaletype"],
        "description_var": "",
    }
    return sql_info


def process_queue_element(
    orchestrator_connection: OrchestratorConnection,
    queue_element: QueueElement,
    solteq_app: SolteqTandApp,
):
    """
    Function to process queue elements in Ikke meddelte aftaler.
    Process changes status of appointments and sends out messages to patient.
    If any business error, queue element is added to a manual list in an SQL database.
    """
    sql_info = get_sql_info(queue_element)

    # Find the patient
    SSN = queue_element.data["Cpr"].replace("-", "")
    orchestrator_connection.log_trace("Indtaster CPR og laver opslag")
    try:
        solteq_app.open_patient(SSN)
        # solteq_app.open_tab("Stamkort")
        orchestrator_connection.log_trace("Patientjournalen blev åbnet")
    except (NotMatchingError, PatientNotFoundError) as e:
        orchestrator_connection.log_error(str(e))
        raise BusinessError from e
    except Exception as e:
        orchestrator_connection.log_error(
            "Der skete en fejl da stamkortvinduet ikke blev åbnet som forventet"
        )
        raise SystemError from e
    patient_window = solteq_app.app_window

    # Here to check that patient fulfills criteria.
    try:
        try:
            # If OR aftale meddelt: close and put on manual
            appointment_control = check_patient(
                orchestrator_connection=orchestrator_connection,
                solteq_app=solteq_app,
                SSN=SSN,
            )
            solteq_app.change_appointment_status(
                appointment_control=appointment_control,
                set_status='OR Aftale meddelt',
                send_msg=True
            )
        except NotMatchingError as e:
            sql_info["description_var"] = (
                "Indtastet CPR matcher ikke CPR fra den åbnede journal."
            )
            raise ManualProcessingRequiredError from e
        except ORAppointmentFoundError as e:
            sql_info["description_var"] = "'OR aftale meddelt' fundet"
            raise ManualProcessingRequiredError from e
        except NoAppointmentFoundError as e:
            sql_info["description_var"] = "Ingen 'Ikke meddelt aftale' fundet"
            raise ManualProcessingRequiredError from e
        except ManualProcessingRequiredError as e:
            sql_info["description_var"] = "Advarsel da aftale gemtes"
            raise ManualProcessingRequiredError from e

    # Here we insert information to manual list, if some business exception is found
    except ManualProcessingRequiredError as e:
        # Connects to RPA sql
        orchestrator_connection.log_trace("Tilføjer person til manuel liste")

        start_date, _ = get_start_end_dates()

        insert_manual_list(
            orchestrator_connection=orchestrator_connection, sql_info=sql_info, date=start_date
        )

        orchestrator_connection.log_trace("Lukker patientvindue")
        solteq_app.app_window = patient_window
        solteq_app.close_patient_window()

        raise BusinessError from e

    # Close patient at the end of process
    orchestrator_connection.log_trace("Status ændret")
    orchestrator_connection.log_trace("Lukker patientvindue")
    solteq_app.app_window = patient_window
    solteq_app.close_patient_window()
