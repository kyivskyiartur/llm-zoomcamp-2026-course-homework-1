import json


AGENT_INSTRUCTIONS = """
You're a course teaching assistant.
Answer the student's question using the search tool.
Make multiple searches with different keywords before answering.
""".strip()


SEARCH_TOOL = {
    "type": "function",
    "name": "search",
    "description": "Search the course lesson chunks for information matching the given query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for finding relevant course lesson content."
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }
}


def search(index, query, num_results=5):
    results = index.search(
        query,
        num_results=num_results
    )

    return results


def make_call(call, index):
    arguments = json.loads(call.arguments)

    if call.name == "search":
        result = search(
            index,
            **arguments
        )

    result_json = json.dumps(
        result,
        indent=2
    )

    return {
        "type": "function_call_output",
        "call_id": call.call_id,
        "output": result_json
    }


def agent_loop(client, index, question, model="gpt-5.4-mini"):
    messages = [
        {"role": "developer", "content": AGENT_INSTRUCTIONS},
        {"role": "user", "content": question}
    ]

    iteration = 1
    search_calls = 0

    while True:
        print(f"Iteration #{iteration}")

        has_function_calls = False

        response = client.responses.create(
            model=model,
            input=messages,
            tools=[SEARCH_TOOL]
        )

        messages.extend(response.output)

        for item in response.output:
            if item.type == "function_call":
                print(
                    "Function call:",
                    item.name,
                    item.arguments
                )

                call_output = make_call(
                    item,
                    index
                )

                messages.append(call_output)
                has_function_calls = True
                search_calls += 1

            elif item.type == "message":
                last_answer = item.content[0].text

        iteration = iteration + 1

        if has_function_calls == False:
            break

    return {
        "answer": last_answer,
        "search_calls": search_calls,
        "messages": messages
    }