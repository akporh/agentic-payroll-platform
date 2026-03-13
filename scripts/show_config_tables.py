from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import os
import sys
import pandas as pd
from tabulate import tabulate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

workspace_id = sys.argv[1]

engine = create_engine(DATABASE_URL)


def table_has_workspace(inspector, table):
    cols = inspector.get_columns(table)
    return any(c["name"] == "workspace_id" for c in cols)


def main():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.connect() as conn:
        for table in tables:

            print(f"\n\n===== {table} =====\n")

            try:

                if table_has_workspace(inspector, table):

                    query = text(
                        f"""
                        SELECT *
                        FROM {table}
                        WHERE workspace_id = :workspace_id
                        LIMIT 10
                        """
                    )

                    df = pd.read_sql(query, conn, params={"workspace_id": workspace_id})

                else:
                    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", conn)

                if df.empty:
                    print("(empty)")
                    continue

                print(tabulate(df, headers="keys", tablefmt="psql"))

            except Exception as e:
                print(f"Error reading {table}: {e}")


if __name__ == "__main__":
    main()