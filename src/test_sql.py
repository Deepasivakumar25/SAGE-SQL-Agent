from graph import app

result = app.invoke({
    "question": "Select employees who have a salary greater than 80000",
    "sql_query": "",
    "sql_result": "",
    "retry_count": 0
})

print("Generated SQL:")
print(result["sql_query"])

if result["sql_result"]:
    print("\nSQL Result:")
    print(result["sql_result"])

print("\nStatus:")
print(result["status"])

if result["status"] == "Success":
    print("\nAnswer:")
    print(result["answer"])
else:
    print("\nReason:")
    print(result["error"])