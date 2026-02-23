from openai import OpenAI

def generate_insight(summary_data, api_key):
    client = OpenAI(api_key=api_key)

    total = summary_data.get("total",0)
    categories = summary_data.get("categories",{})
    highest_category = summary_data.get("highest_category",None)
    percentages = summary_data.get("percentages",{})
    risk_flags = summary_data.get("risk_flags",[])
    

    prompt = f"""
    You are a Financial Assistant.
    
    Total Spending: {total}
   
    Category breakdown:
    """
    for category, amount in categories.items():
        prompt += f"- {category}:{amount}\n"

    prompt += "\n Spending Percentage:\n"

    for category, percent in summary_data["percentages"].items():
        prompt += f"-{category}:{percent}%\n"

    prompt += f"\nHighest Spending Category:{summary_data['highest_category']}\n"

    prompt += f"\n Detected Risk Signals:\n"

    if risk_flags:
        for risk in risk_flags:
            prompt += f"- {risk}\n"
    else:
        prompt += f"- No Financial Risks Signals Detected \n"
    
    prompt += """
    Instructions:
    1.Identify the highest spending category.
    2.Mention if spending looks unbalanced.
    3.Suggest one actionable improvement
    4.keep response under 5 lines
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