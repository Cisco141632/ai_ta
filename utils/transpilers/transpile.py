import re

from .bq_table_name_conversion import BigQueryTableNameConverterInteractor


def update_week_function_with_extract_week(sql):
    # Pattern to match 'WEEK(...)' but not when it is part of a larger function call
    pattern = r"WEEK\((\w+)\)(?!\))"
    replace_word = r"EXTRACT(WEEK FROM \1)"
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def update_month_function_with_extract_month(sql):
    # Pattern to match 'MONTH(...)' but not when it is part of a larger function call
    pattern = r"MONTH\((\w+)\)(?!\))"
    replace_word = r"EXTRACT(MONTH FROM \1)"
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def update_year_function_with_extract_year(sql):
    # Pattern to match 'YEAR(...)' but not when it is part of a larger function call
    pattern = r"YEAR\((\w+)\)(?!\))"
    replace_word = r"EXTRACT(YEAR FROM \1)"
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def convert_current_datetime_in_ist(sql):
    pattern = r"CURRENT_DATETIME\(\)"
    replace_word = r'CURRENT_DATETIME("Asia/Kolkata")'
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def convert_current_date_in_ist(sql):
    pattern = r"CURRENT_DATE\(\)"
    replace_word = r'CURRENT_DATE("Asia/Kolkata")'
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def convert_to_ist_datetime_from_current_timestamp(sql):
    pattern = r"CURRENT_TIMESTAMP\(\)"
    replace_word = r'CURRENT_DATETIME("Asia/Kolkata")'
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def replace_datetime_from_timestamp_function(sql):
    pattern = r"TIMESTAMP\("
    replace_word = r"DATETIME("
    modified_sql = re.sub(pattern, replace_word, sql, flags=re.IGNORECASE)
    return modified_sql


def convert_ai_generated_sql_to_bigquery_sql(
    sql: str,
) -> str:
    sql, _ = BigQueryTableNameConverterInteractor().get_converted_sql_query(sql)
    if not sql:
        return sql
    sql = update_week_function_with_extract_week(sql=sql)
    sql = update_month_function_with_extract_month(sql=sql)
    sql = update_year_function_with_extract_year(sql=sql)
    sql = convert_current_datetime_in_ist(sql=sql)
    sql = convert_current_date_in_ist(sql=sql)
    sql = convert_to_ist_datetime_from_current_timestamp(sql=sql)
    sql = replace_datetime_from_timestamp_function(sql=sql)
    return sql
