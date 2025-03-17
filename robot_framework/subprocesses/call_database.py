"""This file contains functions with calls to SQL database"""

import pyodbc
import pandas as pd

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection


def connect_to_db(
    orchestrator_connection: OrchestratorConnection
):
    """Establish connection to sql database

    Returns:
        rpa_conn (pyodbc.Connection): The connection object to the SQL database.
    """
    rpa_conn_string = orchestrator_connection.get_constant(
        "DbConnectionString"
    ).value
    rpa_conn = pyodbc.connect(rpa_conn_string)
    return rpa_conn


def get_queue(
    orchestrator_connection: OrchestratorConnection,
    queue="solteqtand_ikke_meddelte_aftaler",
):
    """Function to get queue from database. Used to assert that queue is empty."""

    rpa_conn = connect_to_db(orchestrator_connection)
    cursor = rpa_conn.cursor()

    try:
        query = """
            SELECT *
            FROM [RPA].[dbo].[Queues]
            WHERE queue_name = ?
            AND status = 'NEW'
        """
        res = cursor.execute(query, (queue))
        # Get all rows from query
        rows = res.fetchall()

        return rows
    except pyodbc.Error as exc:
        print(exc)
    finally:
        rpa_conn.close()


def get_manual_list(
    orchestrator_connection: OrchestratorConnection,
    start_date: str,
    end_date: str
):
    """
    Function to get the manual list from the SQL database.

    Args:
        orcestrator_connection (OrchestratorConnection): OpenOrchestrator connection
        start_date (datetime): start date for current period handled
        end_date (datetime): end date for current period handled

    Returns:
        manual_list (pd.DataFrame): Dataframe with the manual list
    """
    rpa_conn = connect_to_db(orchestrator_connection)
    cursor = rpa_conn.cursor()

    try:
        query = """
            SELECT
                Name
                ,CPR
                ,AppointmentType
                ,Description
            FROM [RPA].[rpa].[MBU006IkkeMeddelteAftaler]
            WHERE Date BETWEEN ? AND ?
        """
        res = cursor.execute(query, (start_date, end_date))
        # Get all rows from query
        rows = res.fetchall()

        # Package in pandas
        manual_list = pd.DataFrame.from_records(
            rows,
            columns=[col[0] for col in res.description])
        return manual_list
    except pyodbc.Error as exc:
        print(exc)
    finally:
        rpa_conn.close()


def insert_manual_list(
    orchestrator_connection: OrchestratorConnection,
    sql_info: dict
):
    """
    Function to insert queue info into manual list due to business error.

    Args:
        orchestrator_connection (OrchestratorConnection): Open Orchestrator connection
        sql_info (dict): Dictionary with info to be inserted in sql database"""
    rpa_conn = connect_to_db(orchestrator_connection)
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
