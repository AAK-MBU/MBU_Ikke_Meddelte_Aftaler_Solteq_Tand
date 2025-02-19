"""
Runs checks on patient, to if person should be handled or not
"""
import pandas as pd

import uiautomation as auto

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.solteqtand.app_handler import ManualProcessingRequiredError, NotMatchingError, SolteqTandApp


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
    appointment_control = None
    appointments = check_or_aftale_meddelt(
        orchestrator_connection=orchestrator_connection,
        solteq_app=solteq_app,
        return_dict=True)
    orchestrator_connection.log_trace("Ingen 'OR aftale meddelt' fundet")
    if not check_age_under_18(
        orchestrator_connection=orchestrator_connection,
        SSN=SSN
    ):
        orchestrator_connection.log_trace("Patienten er over 18. Fjerner ekstra modtagere af beskeder")
        solteq_app.set_extra_recipients(False)
    # Find first ikke_meddelt_aftale
    appointment_control = select_first_appointment(
        orchestrator_connection=orchestrator_connection,
        appointments=appointments,
        appointment_to_select="Ikke meddelt aftale"
    )

    if appointment_control:
        return appointment_control
    else:
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
        orchestrator_connection: OrchestratorConnection,        
        SSN: str):
    """Function to check age of inputted SSN. Return true if under 18"""
    orchestrator_connection.log_trace("Tjekker om patienten er under 18")
    # Extract the birthdate part (DDMMYY) from the input string (first 6 characters)
    birthdate = SSN[:6]
    
    # Get the current year
    current_year = pd.to_datetime('today').year
    
    # Extract the last 2 digits of the year (YY)
    year_suffix = int(birthdate[4:6])
    
    # Determine the full year by checking if the year_suffix is within a reasonable range
    if year_suffix > current_year % 100:
        # Assume birth year is in the 1900s (19YY)
        year = 1900 + year_suffix
    else:
        # Assume birth year is in the 2000s (20YY)
        year = 2000 + year_suffix

    # Create the full birthdate string by combining DDMM with the calculated year
    full_birthdate_str = f"{birthdate[:2]}-{birthdate[2:4]}-{year}"
    
    # Convert the birthdate to a pandas datetime object
    birthdate_obj = pd.to_datetime(full_birthdate_str, format='%d-%m-%Y')
    
    # Get today's date
    today = pd.to_datetime('today')
    
    # Calculate age in years
    age = (today - birthdate_obj).days // 365
    
    # Check if age is above or equal to 18
    return age < 18
    # return age < 10
