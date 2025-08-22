from data_sets.ecommerce.bigquery import BigQueryEcommerceUploader

if __name__=="__main__":
    bq_uploader = BigQueryEcommerceUploader(
        project_id="hybrid-dominion-469805-m4",
        dataset_id="ecommerce",
        credentials_path="/home/dw-dev-009/Downloads/hybrid-dominion-469805-m4-5f3a10493537.json"
    )
    bq_uploader.upload_all_data()