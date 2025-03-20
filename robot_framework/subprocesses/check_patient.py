"""
Runs checks on patient, to if person should be handled or not
"""
import pandas as pd

import uiautomation as auto

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError, SolteqTandApp


class NoAppointmentFoundError(Exception):
    """Custom exception"""
    def __init__(self, message="Error occurred while finding appointment."):
        super().__init__(message)


class ORAppointmentFoundError(Exception):
    """Custom exception"""
    def __init__(self, message="Error occurred while finding appointment."):
        super().__init__(message)


def check_patient(
        orchestrator_connection: OrchestratorConnection,
        solteq_app: SolteqTandApp,
        SSN: str
) -> auto.Control:
    """Function to check different requirements for patient before patient is handled.

    Args:
        orchestrator_connection (OrchestratorConnection): The connection to OpenOrchestrator
        solteq_app (SolteqTandApp): The SolteqTand application instance
        SSN (str): CPR number of the current patient

    returns:
        appointment_control (auto.Control): Control of the appointment to handle
    """
    appointment_control = None
    appointments = check_or_aftale_meddelt(
        orchestrator_connection=orchestrator_connection,
        solteq_app=solteq_app,
        return_dict=True)
    orchestrator_connection.log_trace("Ingen 'OR aftale meddelt' fundet")
    # Find first ikke_meddelt_aftale
    appointment_control = select_first_appointment(
        orchestrator_connection=orchestrator_connection,
        appointments=appointments,
        appointment_to_select="Ikke meddelt aftale"
    )

    if appointment_control:
        return appointment_control

    raise ManualProcessingRequiredError


def select_first_appointment(
        orchestrator_connection: OrchestratorConnection,
        appointments: dict,
        appointment_to_select: str
):
    """
    Searches for appointment in sorted dataframe.
    Raises NoAppointmentFoundError if appointment type cannot be found"""
    try:
        appointments_df = appointments['dataframe']
        first_ikke_meddelt = appointments_df[
            (
                (appointments_df['Status'] == appointment_to_select) &
                (appointments_df['Klinik'] == "121"))
        ].index[0]
        appointment_control = appointments["controls"][first_ikke_meddelt]

        return appointment_control
    except IndexError as e:
        orchestrator_connection.log_error(f"Ingen {appointment_to_select} found")
        raise NoAppointmentFoundError from e


def check_or_aftale_meddelt(
        orchestrator_connection: OrchestratorConnection,
        solteq_app: SolteqTandApp,
        return_dict: bool = False
):
    # Get list of appointments
    orchestrator_connection.log_trace("Tjekker om der er en OR aftale meddelt")
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
    appointments['dataframe'] = appointments_df

    if "OR Aftale meddelt" in appointments["Status"]:
        orchestrator_connection.log_trace("'OR aftale meddelt' fundet")
        raise ORAppointmentFoundError

    if return_dict:
        return appointments


def check_age_under_18(
        SSN: str
) -> bool:
    """
    Function to check whether patient is under 18

    Args:
        SSN (str): CPR number in format DDMMYYxxxx

    Returns:
        is_under_18 (bool): Boolean indicating whether person is under 18
    """
    # Extract birthdate from cpr
    birthdate = SSN[:6]
    # Get datetime for birth and today
    born = pd.to_datetime(birthdate, format="%d%m%y")
    today = pd.to_datetime("today")
    # Compute difference in years, extract one if no birthday yet in current year
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    is_under_18 = age < 18
    return is_under_18
