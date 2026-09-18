from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from tools import execute_sql
from llm import llm


class SQLAgentState(TypedDict):
    question: str
    sql_query: str
    sql_result: str
    is_valid: bool
    error: str
    status: str
    answer: str
    retry_count: int

def generate_sql(state: SQLAgentState):

    prompt = f"""
You are a PostgreSQL SQL expert.

Convert the user's question into a SQL query.

Database tables:
- employees(employee_id, employee_name, email, department_id, salary, hire_date)
- departments(department_id, department_name, location)
- customers(customer_id, customer_name, email, city, registration_date)
- orders(order_id, customer_id, order_date, status)
- order_items(order_item_id, order_id, product_id, quantity, unit_price)
- products(product_id, product_name, category, price, stock_quantity)

User question:
{state["question"]}

Previous SQL error: {state["error"]}

Return only the SQL query.
"""

    response = llm.invoke(prompt)

    sql_query = response.content.strip()

    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")
    sql_query = sql_query.strip()

    return {
        "sql_query": sql_query
    }

def validate_sql(state: SQLAgentState):

    sql_query = state["sql_query"].strip().lower()

    if not sql_query.startswith("select"):
       return {"is_valid": False, "error":"Only SELECT queries are allowed","status":"Rejected"}
        
    return {"is_valid": True,"error":"","status":"Success"}

def route_after_execution(state: SQLAgentState):
    if state["status"] == "Success":
       return "generate_answer"

    if state["retry_count"] < 3:
       return "generate_sql"
    return "end"

def route_after_validation(state: SQLAgentState):
   if state["is_valid"]:
      return "execute_query"
   return "end"

def execute_query(state: SQLAgentState):
    try:
        result = execute_sql(state["sql_query"])
        return {
        "sql_result": str(result),
        "error": "",
        "status": "Success"
        }

    except Exception as e:
         return {
        "sql_result": "",
        "error": str(e),
        "status": "SQL Error",
        "retry_count": state["retry_count"] + 1
        }


def generate_answer(state: SQLAgentState):

    prompt = f"""

    You are a helpful database assistant.

    User question: {state["question"]}

    SQL query: {state["sql_query"]}

    Database result: {state["sql_result"]}

    Give a simple, clear answer to the user's question.

    Do not mention SQL unless necessary.

    """

    response = llm.invoke(prompt)

    return {"answer": response.content.strip()}


graph = StateGraph(SQLAgentState)

graph.add_node("generate_sql", generate_sql)
graph.add_node("validate_sql", validate_sql)
graph.add_node("execute_query", execute_query)
graph.add_node("generate_answer",generate_answer)


graph.add_edge(START, "generate_sql")
graph.add_edge("generate_sql", "validate_sql")
graph.add_conditional_edges(
"validate_sql",
route_after_validation,
{
"execute_query": "execute_query",
"end": END,
}
)
graph.add_conditional_edges(
"execute_query",
 route_after_execution,
{
"generate_answer": "generate_answer",
"generate_sql": "generate_sql",
"end": END
}
)
graph.add_edge("generate_answer", END)

app = graph.compile()