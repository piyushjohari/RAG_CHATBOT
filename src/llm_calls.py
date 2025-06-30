from openai import OpenAI
import os
from dotenv import load_dotenv
from src.prompts import TABLE_DATA_PARSING_PROMPT, TABLE_DATA_TUNING_PROMPT

load_dotenv()
model = os.environ.get("MODEL")
client = OpenAI()

def structure_table_data(data, text, file_name, as_markdown=True):

    output = structure_only_table_data(data, file_name, as_markdown)
    # Thought of using a combination of text and table data to find exact table structure.
    # structured_data = structure_table_data_using_text(output, text)
    return output

def structure_only_table_data(data, file_name, as_markdown):
    # Format the dataframe
    if as_markdown:
        table = data.to_markdown(index=False)
    else:
        table = data.to_csv(index=False)

    query = f"""
        Input Table Data: \n ---- {table} \n ----
        filename: {file_name}
    """
    messages = [
        {"role": "system", "content": TABLE_DATA_PARSING_PROMPT},
        {"role": "user", "content": query}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content.strip()


def structure_table_data_using_text(data, text):

    query = f"""
        Input Text: \n ---- {text} \n ---- \n
        Input Table Data: \n ---- {data} \n ----

    """
    messages = [
        {"role": "system", "content": TABLE_DATA_TUNING_PROMPT},
        {"role": "user", "content": query}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content.strip()


def get_llm_answer(user_query, search_results):
    prompt = f"""
        You are an expert assistant for a chatbot. Here are the instructions:

        - If the user's input is a general greeting or salutation (such as 'hi', 'hello', 'good morning', 'good evening', 'good afternoon', 'hey', etc.), respond with an appropriate friendly greeting in return. Do NOT bring up any context for such greetings.
        - If the user's question asks for specific information, you MUST answer using ONLY the supplied ranked context below. 
        - Be a smart assistant, You have to be flexible enough to handle any question that has even slight resembelance to any of the context provided to you, or in case it is framed in not exact but similar language.
        - You have to carefully analyse if the questions can be answered
        - otherwise do not use any external information beyond the context. 
        - HIf the answer is not contained in the context, respond with "I don't know based on the provided information."

        Context: (retrieved results, ordered by relevance: Rank 1 is most relevant)
        {search_results}

        User's question:
        {user_query}

        Additional Context:
        Following are some insurace plans:
        1. 2500 Gold SOB
        2. 5000 HSA SOB
        3. 5000 Bronze SOB
        4. 7350 Copper SOB
        You will find this information in the filename given with context, If the user talks about then you may have to talk about those specific plans based on the context provided.
        But do not quote the filename as such.

    """
    
    messages = [
            {"role": "system", "content": "You are a helpful assistant. You will answer accuratly ONLY based on the provided information."},
            {"role": "user", "content": prompt}
        ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    result = response.choices[0].message.content
    return result
