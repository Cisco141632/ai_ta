import os

import pandas as pd
from google.api_core import exceptions
from google.cloud import bigquery
from google.oauth2 import service_account

from .base import QueryExecutor

BQ_CREDENTIAL_PATH = os.environ.get("BQ_CREDENTIAL_PATH")


class BQQueryExecutor(QueryExecutor):
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            BQ_CREDENTIAL_PATH,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        project_id = credentials.project_id
        self.bq_client = bigquery.Client(
            project=project_id, credentials=credentials
        )

    def execute(self, query):
        df = self.query_bigquery(query)
        return df, query

    def query_bigquery(self, query):
        empty_df = pd.DataFrame()
        if not query:
            return empty_df
        try:
            query_job = self.bq_client.query(
                query,
                location="asia-south1",
                job_id_prefix="ai_analyst_",
            )
            result = query_job.result()
            df = result.to_dataframe()
            # df = self._reverse_column_names(df, col_name_mapping)
            return df
        except exceptions.BadRequest as e:
            print(f"BadRequest error: {e}")
            # Handle invalid query syntax or other bad request errors
            return empty_df
        except exceptions.Forbidden as e:
            print(f"Forbidden error: {e}")
            # Handle authentication or authorization errors
            return empty_df
        except exceptions.NotFound as e:
            print(f"NotFound error: {e}")
            # Handle cases where the specified dataset or table doesn't exist
            return empty_df
        except bigquery.BigQueryTimeoutError as e:
            print(f"BigQuery timeout error: {e}")
            # Handle query timeout errors
            return empty_df
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle any other unexpected errors
            return empty_df

    @staticmethod
    def _reverse_column_names(df, col_name_mapping):
        col_list = df.columns.tolist()
        rename_mapping = {
            col: col_name_mapping.get(col)
            for col in col_list
            if col in col_name_mapping
        }
        return df.rename(columns=rename_mapping)
