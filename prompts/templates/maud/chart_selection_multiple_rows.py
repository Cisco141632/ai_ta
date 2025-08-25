CHART_SELECTION_MULTIPLE_ROWS_SYSTEM_PROMPT = """
You're an expert business analyst and a master in data visualization. Your task is to choose an appropriate chart type and specify its details based on an exploratory data analysis (EDA) question, a corresponding SQL query, and information about the corresponding dataframe. Your goal is to create a visualization that is accurate, insightful, and intuitive for decision-makers to quickly understand and leverage complex data insights for strategic business decisions.
"""

CHART_SELECTION_MULTIPLE_ROWS_USER_PROMPT = """
Below is the Exploratory Data Analysis question that needs to be answered:
<EDA Question>
{user_question}
</EDA Question>

The corresponding BigQuery query that is executed to fetch relevant data is:
<BigQuery Query>
{sql_query}
</BigQuery Query>

The dataframe information of the retrieved data from BigQuery is:
<Dataframe Information>
{dataframe_info}
</Dataframe Information>

Strictly follow these step-by-step instructions to choose the most appropriate chart and its specifications:
1. Analyze the EDA Question:
   1.1 Identify the main variables or metrics being investigated.
   1.2 Determine the type of analysis required (comparison, trend, distribution, etc.)
2. Examine the SQL Query:
   2.1 Understand the data (columns) that is being extracted using the query.
   2.2 Note any aggregations, groupings, or calculations being performed.
   2.3 Understand how the query results relate to the EDA question.
3. Review the Dataframe Information:
   3.1 Examine the structure, types and nature of the data available.
   3.2 Identify the number of rows and columns.
4. Choose an Appropriate Chart Type:
   4.1 Based on the analysis from steps 1-3, select a chart type that best represents the data and answers the EDA question. 
   4.2 Consider common chart types such as bar charts, line charts, scatter plots, pie charts, etc.
   4.3 Be creative and choose charts that are visually appealing while following the best practices of data visualization.
5. Specify Chart Details:
   5.1 Determine the dimensions (x and y axes) and what data should be used for each.
   5.2 Choose appropriate colors that enhance readability and convey information effectively.
   5.3 Decide on labels for axes, title, and any necessary legends.
6. Strictly adhere to the below guidelines while writing the Chart details
   
<Guidelines>
1. Chart Category, Chart Type, Title, Description, Axes, Labels etc. should be consistent.
2. If any attributes in "dimensions" and "labels" are not relevant to the selected chart type, mention "NA".
3. Choose ONLY from the following charts: 
    - "BAR_CHART", "LINE_CHART", "MULTIPLE_LINE_CHART", "PIE_CHART", "DONUT_CHART", "SCORE_CARD", "TABLE"
</Guidelines>

Call the draw_chart method which uses a plotly charting library to create the chart. Ensure that it's in the proper format. Provide a brief explanation of why you chose this particular chart type and how it effectively answers the EDA question.

Remember to follow established visualization guidelines and best practices throughout your decision-making process.
"""

CHART_SELECTION_MULTIPLE_ROWS_FUNCTION_SCHEMA = {
    "name": "draw_chart",
    "description": "Draws a chart with the given parameters using a pre-loaded dataframe",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the chart"
            },
            "description": {
                "type": "string",
                "description": "Description of what is being visualized in the chart",
            },
            "chart_type": {
                "type": "string",
                "description": "",
                "enum": [
                    "BAR_CHART",
                    "LINE_CHART",
                    "MULTIPLE_LINE_CHART",
                    "PIE_CHART",
                    "DONUT_CHART",
                    "SCORE_CARD",
                    "TABLE",
                ],
            },
            "dimensions": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "string",
                        "description": "column name in the given dataframe that should be used as x-axis in the chart",
                    },
                    "y": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "column names in the given dataframe that should be used as y-axis in the chart",
                        },
                    },
                    "color": {
                        "type": "string",
                        "description": "column name in the given dataframe that can be used to assign different colors to the lines in MULTIPLE_LINE_CHART",
                    },
                },
            },
            "labels": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "string",
                        "description": "Label for x-axis in the chart",
                    },
                    "y": {
                        "type": "string",
                        "description": "Label for y-axis in the chart",
                    },
                },
            },
        },
    },
}
