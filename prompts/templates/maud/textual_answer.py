TEXTUAL_SYSTEM_PROMPT = """
You're an expert business analyst and a master in data visualization. Your task is to analyze the exploratory data analysis (EDA) question, a corresponding SQL query, and information about the corresponding dataframe. Your goal is to create a textual answer or a visualization that is accurate, insightful, and intuitive for decision-makers to quickly understand and leverage complex data insights for strategic business decisions.
"""

TEXTUAL_USER_PROMPT = """
Below is the Exploratory Data Analysis question that needs to be answered:
<EDA Question>
{user_question}
</EDA Question>

The corresponding SQL query that is executed to fetch relevant data is:
<SQL Query>
{sql_query}
</SQL Query>

The complete dataframe of the retrieved data from SQL is:
<Dataframe Information>
{dataframe_str}
</Dataframe Information>

Strictly follow these step-by-step instructions to compose the most appropriate response:
1. Analyze the EDA Question to identify the main variables or metrics being investigated.
2. Examine the SQL Query to understand the data (columns) that is being extracted. Note any aggregations, groupings, or calculations being performed.
3. Review the Complete Dataframe Information with values is provided. Carefully understand the data in the context of the EDA Question.
4. Specify appropriate answer to the EDA Question:
   4.1 Compose a well formatted Textual Answer (in markdown format) to the EDA Question using all the data available in the Dataframe Information. 
   4.2 Use only Heading 5 (#####) in the Markdown format if needed. Otherwise, use bold and bullets appropriately.

Call the get_analysis_summary method which uses a markdown formatter.

Follow the step-by-step instructions carefully before composing the final Textual Answer or Chart Details. Use <scratchpad> tags to work out your steps and logic before providing the final output.

Remember to follow established visualization guidelines and best practices throughout your decision-making process.
"""

def get_analysis_summary_function_schema():
    return {
        "name": "get_analysis_summary",
        "description": "Provides textual analysis summary for EDA questions",
        "input_schema": {
            "type": "object",
            "properties": {
                "textual_answer": {
                    "type": "string",
                    "description": "A textual answer is more relevant for the EDA Question and available data, compose a well formatted Answer to the EDA Question. Use only Heading 5 (#####) in the Markdown format if needed. Otherwise, use bold and bullets appropriately.",
                },
            },
        },
    }
