from openai import OpenAI

def generate_insight(summary_data, api_key):
    client = OpenAI(api_key=api_key)

    total = summary_data["total"]
    categories = summary_data["categories"]

    prompt = f"""
    You are a Financial Assistant.
    Total Spending: {total}
    Category breakdown: {categories}

    Give a short actionable financial insight.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content