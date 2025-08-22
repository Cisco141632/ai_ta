import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

from data_sets.ecommerce.generate import DataGen


class BigQueryEcommerceUploader:
    def __init__(self, project_id, dataset_id, credentials_path):
        """
        Initialize BigQuery client with service account credentials

        Args:
            project_id (str): Google Cloud project ID
            dataset_id (str): BigQuery dataset ID
            credentials_path (str): Path to service account JSON file
        """
        self.project_id = project_id
        self.dataset_id = dataset_id

        # Initialize BigQuery client with service account
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.client = bigquery.Client(credentials=credentials, project=project_id)
        self.data_gen = DataGen()

        print(f"✅ Connected to BigQuery project: {project_id}")
        print(f"📊 Target dataset: {dataset_id}")

    def create_dataset_if_not_exists(self):
        """Create dataset if it doesn't exist"""
        dataset_ref = self.client.dataset(self.dataset_id)

        try:
            self.client.get_dataset(dataset_ref)
            print(f"✅ Dataset {self.dataset_id} already exists")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # Change as needed
            dataset.description = "E-commerce sample data for text-to-SQL testing"

            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"✅ Created dataset {self.dataset_id}")

    def define_table_schemas(self):
        """Define BigQuery table schemas"""
        schemas = {
            self.data_gen.user_table_name: [
                bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("last_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("registration_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("city", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_tier", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
            ],
            self.data_gen.category_table_name: [
                bigquery.SchemaField("category_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("category_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("parent_category_id", "INTEGER", mode="NULLABLE"),
            ],
            self.data_gen.product_table_name: [
                bigquery.SchemaField("product_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("product_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("category_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("price", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("cost_price", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("launch_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
                bigquery.SchemaField("average_rating", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("total_reviews", "INTEGER", mode="REQUIRED"),
            ],
            self.data_gen.order_table_name: [
                bigquery.SchemaField("order_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("order_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("order_status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("subtotal", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("tax_amount", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("shipping_cost", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("discount_amount", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("total_amount", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("payment_method", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("delivered_date", "DATE", mode="NULLABLE"),
            ],
            self.data_gen.order_items_table_name: [
                bigquery.SchemaField("order_item_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("order_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("product_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("quantity", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("unit_price", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("total_price", "FLOAT", mode="REQUIRED"),
            ],
            self.data_gen.review_table_name: [
                bigquery.SchemaField("review_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("product_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("order_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("rating", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("review_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("helpful_votes", "INTEGER", mode="REQUIRED"),
            ]
        }
        return schemas

    def fix_dataframe_dtypes(self, df, table_name):
        """
        Fix DataFrame data types for BigQuery compatibility

        Args:
            df (pd.DataFrame): Input DataFrame
            table_name (str): Name of the table

        Returns:
            pd.DataFrame: Fixed DataFrame
        """
        df_fixed = df.copy()

        print(f"   🔧 Fixing data types for {table_name}...")

        # Fix date columns
        date_columns = []
        if table_name == 'users':
            date_columns = ['registration_date']
        elif table_name == 'products':
            date_columns = ['launch_date']
        elif table_name == 'orders':
            date_columns = ['order_date', 'delivered_date']
        elif table_name == 'reviews':
            date_columns = ['review_date']

        for col in date_columns:
            if col in df_fixed.columns:
                try:
                    # Convert to datetime first, then let BigQuery handle the DATE conversion
                    df_fixed[col] = pd.to_datetime(df_fixed[col], errors='coerce')
                    print(f"      ✅ Fixed date column: {col}")
                except Exception as e:
                    print(f"      ⚠️ Could not fix {col}: {e}")

        # Add missing columns that schema expects
        if table_name == 'orders' and 'discount_amount' not in df_fixed.columns:
            print(f"   ➕ Adding missing discount_amount column...")
            df_fixed['discount_amount'] = 0.0

        # Fix boolean columns
        bool_columns = ['is_active'] if 'is_active' in df_fixed.columns else []
        for col in bool_columns:
            df_fixed[col] = df_fixed[col].astype(bool)
            print(f"      ✅ Fixed boolean column: {col}")

        # Fix numeric columns to ensure they're proper numeric types
        numeric_cols = ['price', 'cost_price', 'total_amount', 'subtotal', 'tax_amount',
                        'shipping_cost', 'unit_price', 'total_price', 'average_rating', 'discount_amount']
        for col in numeric_cols:
            if col in df_fixed.columns:
                df_fixed[col] = pd.to_numeric(df_fixed[col], errors='coerce')

        return df_fixed

    def upload_csv_to_bigquery(self, table_name, csv_path, schema):
        """Upload CSV file to BigQuery table"""
        table_ref = self.client.dataset(self.dataset_id).table(table_name)

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            skip_leading_rows=1,  # Skip header row
            source_format=bigquery.SourceFormat.CSV,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite table
        )

        print(f"⬆️  Uploading {csv_path} to {self.dataset_id}.{table_name}...")

        with open(csv_path, "rb") as source_file:
            job = self.client.load_table_from_file(source_file, table_ref, job_config=job_config)

        job.result()  # Wait for the job to complete

        # Get table info
        table = self.client.get_table(table_ref)
        print(f"✅ Loaded {table.num_rows:,} rows into {table_name}")

        return table

    def upload_dataframe_to_bigquery(self, table_name, dataframe, schema=None, if_exists='replace'):
        """
        Upload DataFrame to BigQuery table with automatic data type fixing

        Args:
            table_name (str): Name of the BigQuery table
            dataframe (pd.DataFrame): DataFrame to upload
            schema (List[bigquery.SchemaField], optional): BigQuery schema. If None, auto-detect
            if_exists (str): What to do if table exists ('replace', 'append', 'fail')

        Returns:
            bigquery.Table: The created/updated BigQuery table
        """
        print(f"⬆️  Uploading DataFrame to {self.dataset_id}.{table_name}...")
        print(f"    Original shape: {dataframe.shape}")
        print(f"    Mode: {if_exists}")

        try:
            # Step 1: Fix data types
            df_fixed = self.fix_dataframe_dtypes(dataframe, table_name)
            print(f"    Fixed shape: {df_fixed.shape}")

            # Step 2: Configure job
            table_ref = self.client.dataset(self.dataset_id).table(table_name)
            job_config = bigquery.LoadJobConfig()

            # Set write disposition based on if_exists parameter
            if if_exists == 'replace':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif if_exists == 'append':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            else:
                raise ValueError("if_exists must be 'replace' or 'append'")

            # Set schema if provided, otherwise auto-detect
            if schema:
                job_config.schema = schema
            else:
                job_config.autodetect = True

            # Step 3: Upload DataFrame
            job = self.client.load_table_from_dataframe(df_fixed, table_ref, job_config=job_config)
            job.result()  # Wait for the job to complete

            # Step 4: Get table info
            table = self.client.get_table(table_ref)
            print(f"✅ Loaded {table.num_rows:,} rows into {table_name}")

            return table

        except Exception as e:
            print(f"❌ Primary method failed: {str(e)}")
            print(f"   🔄 Trying alternative method...")

            # Alternative method: Use autodetect without explicit schema
            try:
                df_alt = self.fix_dataframe_dtypes(dataframe, table_name)

                table_ref = self.client.dataset(self.dataset_id).table(table_name)
                job_config = bigquery.LoadJobConfig()

                if if_exists == 'replace':
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                elif if_exists == 'append':
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

                # Force autodetect without explicit schema
                job_config.autodetect = True

                job = self.client.load_table_from_dataframe(df_alt, table_ref, job_config=job_config)
                job.result()

                table = self.client.get_table(table_ref)
                print(f"✅ Alternative method: Loaded {table.num_rows:,} rows into {table_name}")

                return table

            except Exception as e2:
                print(f"❌ Alternative method also failed: {str(e2)}")
                raise e

    def upload_all_data(self):
        """Complete workflow: generate data and upload to BigQuery"""
        print("🚀 Starting BigQuery upload process...")

        # Create dataset if needed
        self.create_dataset_if_not_exists()

        # Define schemas
        schemas = self.define_table_schemas()

        # Upload each table
        print(f"\n📤 Uploading tables to BigQuery...")
        uploaded_tables = {}
        data = self.data_gen.generate_data()

        for table_name in [
            self.data_gen.user_table_name,
            self.data_gen.category_table_name,
            self.data_gen.product_table_name,
            self.data_gen.order_table_name,
            self.data_gen.order_items_table_name,
            self.data_gen.review_table_name,
        ]:

            schema = schemas[table_name]
            table_df = data.get(table_name)

            try:
                table = self.upload_dataframe_to_bigquery(table_name, dataframe=table_df, schema=schema)
                uploaded_tables[table_name] = table
            except Exception as e:
                print(f"❌ Failed to upload {table_name}: {str(e)}")

        print(f"\n✅ Upload complete! {len(uploaded_tables)} tables created in {self.dataset_id}")

        # Print summary
        print("\n📊 Upload Summary:")
        total_rows = 0
        for table_name, table in uploaded_tables.items():
            print(f"   {table_name:<15} {table.num_rows:>8,} rows")
            total_rows += table.num_rows
        print(f"   {'TOTAL':<15} {total_rows:>8,} rows")

        return uploaded_tables

    def run_sample_queries(self):
        """Run sample queries to verify data"""
        print("\n🧪 Running sample verification queries...")

        test_queries = [
            ("Total users", "SELECT COUNT(*) as total_users FROM users"),
            ("Order statuses",
             "SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status ORDER BY count DESC"),
            ("Top categories", """
                SELECT c.category_name, COUNT(p.product_id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.category_id = p.category_id
                GROUP BY c.category_name
                ORDER BY product_count DESC
                LIMIT 5
            """),
            ("Revenue by month", """
                SELECT FORMAT_DATE('%Y-%m', order_date) as month,
                       SUM(total_amount) as revenue
                FROM orders
                WHERE order_status = 'delivered'
                GROUP BY FORMAT_DATE('%Y-%m', order_date)
                ORDER BY month DESC
                LIMIT 6
            """)
        ]

        for query_name, query in test_queries:
            try:
                # Prepend dataset reference to tables in query
                formatted_query = query
                for table in ['users', 'categories', 'products', 'orders', 'order_items', 'reviews']:
                    formatted_query = formatted_query.replace(f" {table} ",
                                                              f" `{self.project_id}.{self.dataset_id}.{table}` ")
                    formatted_query = formatted_query.replace(f" {table}\n",
                                                              f" `{self.project_id}.{self.dataset_id}.{table}`\n")
                    formatted_query = formatted_query.replace(f"FROM {table}",
                                                              f"FROM `{self.project_id}.{self.dataset_id}.{table}`")
                    formatted_query = formatted_query.replace(f"JOIN {table}",
                                                              f"JOIN `{self.project_id}.{self.dataset_id}.{table}`")

                results = self.client.query(formatted_query).result()
                print(f"\n✅ {query_name}:")
                for row in results:
                    print(f"   {dict(row)}")

            except Exception as e:
                print(f"❌ Error in {query_name}: {str(e)}")