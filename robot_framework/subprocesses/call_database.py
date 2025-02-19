"""This file contains functions with calls to SQL database"""

import pyodbc

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection


def insert_manual_list(
        orchestrator_connection: OrchestratorConnection,
        sql_info: dict
):
    """
    Function to insert queue info into manual list due to business error.

    Args:
        orchestrator_connection (OrchestratorConnection): Open Orchestrator connection
        sql_info (dict): Dictionary with info to be inserted in sql database"""
    rpa_conn_string = orchestrator_connection.get_constant(
        "rpa_db_connstr"
    ).value  # Test constant. For prod use: "DbConnectionString"
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
                (?, 
                ?, 
                ?, 
                ?, 
                ?, 
                ?, 
                GetDate())
        """
        cursor.execute(
            query,
            (
                sql_info["name_var"],
                sql_info["cpr_var"],
                sql_info["appointment_type_var"],
                sql_info["description_var"],
                "",
                sql_info["orchestrator_reference_var"]
            ))
        rpa_conn.commit()
    except pyodbc.Error as exc:
        print(exc)
    finally:
        rpa_conn.close()
