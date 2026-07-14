RAG_INSTRUCTIONS = """
Answer the user's question based only on the provided context.
If the answer is not present in the context, say that you don't know.
""".strip()


def search(index, query, num_results=5):
    results = index.search(
        query,
        num_results=num_results
    )

    return results


def build_context(results):
    context = ""

    for document in results:
        context += f"""
        
        Filename: {document["filename"]}

        Content: {document["content"]}
        """

    return context.strip()


def build_prompt(question, context):
    prompt = f"""
    Question: {question}
    Context: {context}
    """.strip()

    return prompt


def rag(client, index, question, model="gpt-5.4-mini"):
    results = search(
        index,
        question,
        num_results=5
    )

    context = build_context(results)
    prompt = build_prompt(question, context)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "developer", "content": RAG_INSTRUCTIONS},
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer": response.output_text,
        "input_tokens": response.usage.input_tokens,
        "results": results
    }