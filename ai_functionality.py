import openai
from openai import OpenAI
from openai import AsyncOpenAI
from datetime import datetime

import logging
from scrapper import scrap_website_data

#TODO

client = OpenAI(
    api_key = "sk-proj-3CQe7YOS1tgWNxPfLQ2OT3BlbkFJd8iJkCeSZBtGDTtxvWAm"

)

def prompt_to_openai_api(messages: list, model: str = 'text-davinci-003'):
    try:
        print('Prompt start time:', datetime.now())
        print(messages)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            n=1,
            temperature=0,
            max_tokens=1000
        )
        print('Prompt end time:', datetime.now())
        return response.choices[0].text.strip()
    except Exception as e:
        print("Exception:", e)
        return None



def get_vc_data(plain_text: str):
    openai_messages = [{"role": "system", "content":
                                                    "Your task is to Extract the following information and show it to the user as a JSON object: VC name, contacts, industries that they invest in, investment rounds that they participate/lead." +
                                                    " please return only json object"
                        },
                    {"role": "user", "content": f"""{plain_text}"""}
                    ]
    response = prompt_to_openai_api(openai_messages, 'gpt-3.5-turbo')
    print(response)
    return response

def compare_data_with_database_data(data, db_data):
    openai_messages = [{"role": "system", "content":
                                                    "Please analyze this data's" +
                                                    "and get 3 most similar vc companies"
                        },
                    {"role": "user", "content": f"""data is {str(data)}, and database data is {str(db_data)}"""}
                    ]
    response = prompt_to_openai_api(openai_messages, 'gpt-3.5-turbo')
    print(response)
    return response

def convert_data_to_vector(data):
    pass


"""AI assistant part"""
async def get_data_from_website(url):

    try:
        website_plain_text = scrap_website_data(url)

        #response = get_vc_data(website_plain_text)

        return website_plain_text
    except Exception as e:
        logging.error(e)
        raise e

async def return_conclusion(new_data, db_data):

    try:
        return 0
    except Exception as e:
        logging.error(e)
        raise e