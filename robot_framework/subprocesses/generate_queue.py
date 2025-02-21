"""Generate queue"""

from datetime import datetime, timedelta
import calendar

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp


def generate_queue(
    orchestrator_connection: OrchestratorConnection, solteq_app: SolteqTandApp
):
    """Generate queue of 'Ikke meddelte aftaler'"""

    # Open view with list of appointments
    orchestrator_connection.log_trace("Åbner aftalebog")
    solteq_app.open_from_main_menu(menu_item="Aftalebog")

    solteq_app.open_tab("Oversigt")

    # Set dates, clinic and status to get correct appointments
    orchestrator_connection.log_trace("Sætter dato")
    start_date, end_date = get_start_end_dates()
    orchestrator_connection.log_trace(f"{start_date.strftime("%d/%m-%Y")}-{end_date.strftime("%d/%m-%Y")}")

    solteq_app.set_date_in_aftalebog(
        from_date=start_date,
        to_date=end_date)

    orchestrator_connection.log_trace("Datoer er sat korrekt")

    solteq_app.pick_appointment_types_aftalebog(appointment_types="Ikke meddelt aftale")

    orchestrator_connection.log_trace("'Ikke meddelt aftale' valgt")

    solteq_app.pick_clinic_aftalebog(clinic='Aarhus Tandregulering')

    # Retrieve appointments in view
    orchestrator_connection.log_trace("Henter aftaler")

    appointments = solteq_app.get_appointments_aftalebog(
        close_after=True,
        headers_to_keep=['Navn', 'Cpr'])

    orchestrator_connection.log_trace("Aftaler hentet")

    # Set references
    references = [
        (
            "ikke_meddelte_aftaler_"
            + f"{start_date.strftime(format="%d%m%y")}_"
            + f"{end_date.strftime(format="%d%m%y")}_"
            + f"{j}"
        ) for j, appointment in enumerate(appointments)
    ]

    # Upload to queue
    orchestrator_connection.bulk_create_queue_elements(
        queue_name="dev_ikke_meddelte_aftaler",
        references=references,
        data=appointments,
        created_by="dev_ahss"
    )

    orchestrator_connection.log_trace("Aftaler sendt til orchestrator kø")


def get_start_end_dates() -> tuple[datetime, datetime]:
    """Function to get start and end dates for period to handle.
    If today is between the 1st and 15th, then 1st to 15th of next month is selected.
    If today is after the 15th, then 16th to end of next month is selected"""
    # Get the current date
    current_date = datetime.now()

    # Check if the current day of the month is between 1 and 15 (inclusive)
    if 1 <= current_date.day <= 15:
        # Set start_date to 1st of next month
        start_date = current_date.replace(day=1) + timedelta(
            days=calendar.monthrange(current_date.year, current_date.month)[1]
        )
        # Set end_date to 15th of next month
        end_date = start_date.replace(day=15)
    else:
        # Set start_date to 16th of next month
        start_date = current_date.replace(day=16) + timedelta(
            days=calendar.monthrange(current_date.year, current_date.month)[1]
        )
        # Set end_date to end of next month
        end_date = start_date.replace(
            day=calendar.monthrange(start_date.year, start_date.month)[1]
        )

    return start_date, end_date
