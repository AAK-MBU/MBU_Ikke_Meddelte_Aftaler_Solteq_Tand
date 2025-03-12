"""This module contains functions related to handling the list of patients to be handled manually"""

import os
import json
from datetime import datetime
from io import BytesIO
import openpyxl

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.smtp import smtp_util

from robot_framework.subprocesses.generate_queue import get_start_end_dates
from robot_framework.subprocesses.call_database import get_manual_list


def delete_temp_files(
        orchestrator_connection: OrchestratorConnection,
        path=os.path.join("C:\\", "tmp", "IkkeMeddelteAftaler")
):
    """Function to delete temp files if any exists"""
    # Check path exists
    if os.path.exists(path):
        # List files in path
        tmp_files = os.listdir(path)
        # Delete all files in path
        if len(tmp_files) > 0:
            orchestrator_connection.log_trace(f"Temp-folderen er ikke tom. {len(tmp_files)} fil(er) i mappen slettes")
            for tmp_file in tmp_files:
                orchestrator_connection.log_trace(
                    f"Sletter filen: {tmp_file}"
                )
                os.remove(os.path.join(path, tmp_file))


def create_excel_sheet(
    orchestrator_connection: OrchestratorConnection,
    path=os.path.join("C:\\", "tmp", "IkkeMeddelteAftaler"),
):
    """Function to create excel sheet from sql table"""
    start_date, end_date = get_start_end_dates()
    start_date = datetime(year=2025, month=3, day=1)
    end_date = datetime(year=2025, month=3, day=31)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    orchestrator_connection.log_trace(f"Periode: {start_date_str} - {end_date_str}")
    manual_list = get_manual_list(
        orchestrator_connection=orchestrator_connection,
        start_date=start_date,
        end_date=end_date
    )

    filename = f"Ikke meddelte aftaler - Manuelliste {start_date_str}_{end_date_str}.xlsx"
    filepath = os.path.join(path, filename)
    if not os.path.exists(path):
        os.mkdir(path)
    # Remove cell border fix
    manual_list = manual_list.T.reset_index().T
    manual_list.to_excel(filepath, header=False, index=False)

    orchestrator_connection.log_trace("Manuel liste dannet.")

    return filepath


def send_manual_list(
        orchestrator_connection: OrchestratorConnection,
        filepath: str
):
    """Function to send email with manual list"""
    filename = filepath.split("\\")[-1]

    start_date, end_date = get_start_end_dates()
    start_date = start_date.strftime("%d.%m.%Y")
    end_date = end_date.strftime("%d.%m.%Y")

    # Read excel file into BytesIO object
    wb = openpyxl.load_workbook(filepath)
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    proc_args = json.loads(orchestrator_connection.process_arguments)

    email_recipient = proc_args["email_recipient"]
    email_sender = orchestrator_connection.get_constant("e-mail_noreply").value
    email_subject = f"Manuel liste for perioden {start_date}-{end_date}"
    email_body = proc_args["email_body"]
    attachments = [smtp_util.EmailAttachment(
        file=excel_buffer, file_name=filename
    )]
    smtp_util.send_email(
        receiver=email_recipient,
        sender=email_sender,
        subject=email_subject,
        body=email_body,
        html_body=True,
        smtp_server=orchestrator_connection.get_constant("smtp_server").value,
        smtp_port=orchestrator_connection.get_constant("smtp_port").value,
        attachments=attachments if attachments else None
    )
