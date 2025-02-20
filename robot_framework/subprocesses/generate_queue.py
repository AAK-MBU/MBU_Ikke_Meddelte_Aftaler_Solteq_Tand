"""Generate queue"""

from datetime import datetime, timedelta
import calendar

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueElement

from mbu_dev_shared_components.solteqtand.app_handler import (
    ManualProcessingRequiredError,
    NotMatchingError,
)
from mbu_dev_shared_components.solteqtand.app_handler import SolteqTandApp


def generate_queue(
    orchestrator_connection: OrchestratorConnection, solteq_app: SolteqTandApp
):
    """Generate queue of 'Ikke meddelte aftaler'"""

    orchestrator_connection.log_trace("Åbner aftalebog")
    solteq_app.open_from_main_menu(menu_item="Aftalebog")

    solteq_app.open_tab("Oversigt")

    orchestrator_connection.log_trace("Sætter dato")
    start_date, end_date = get_start_end_dates()
    start_date += timedelta(days=30)
    end_date += timedelta(days=30)
    print(f"Should select from {start_date} to {end_date}")

    solteq_app.set_date_in_aftalebog(
        from_date=start_date,
        to_date=end_date)

    orchestrator_connection.log_trace("Datoer er sat korrekt")

    solteq_app.pick_appointment_types_aftalebog(appointment_types="Ikke meddelt aftale")
    
    orchestrator_connection.log_trace("'Ikke meddelt aftale' valgt")

    solteq_app.pick_clinic_aftalebog(clinic='Aarhus Tandregulering')
    print("wait")

def get_start_end_dates() -> tuple[datetime, datetime]:
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
