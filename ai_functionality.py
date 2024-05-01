#import openai
#from openai import OpenAI
#from openai import AsyncOpenAI
#from datetime import datetime

import logging
from scrapper import scrap_website_data

#TODO

#client = OpenAI(
#    api_key = "sk-proj-3CQe7YOS1tgWNxPfLQ2OT3BlbkFJd8iJkCeSZBtGDTtxvWAm"
#
#)
#
#def prompt_to_openai_api(messages: list, model: str = 'text-davinci-003'):
#    try:
#        print('Prompt start time:', datetime.now())
#        print(messages)
#        response = client.chat.completions.create(
#            model=model,
#            messages=messages,
#            n=1,
#            temperature=0,
#            max_tokens=1000
#        )
#        print('Prompt end time:', datetime.now())
#        return response.choices[0].text.strip()
#    except Exception as e:
#        print("Exception:", e)
#        return None
#
#
#
#def get_vc_data(plain_text: str):
#    openai_messages = [{"role": "system", "content":
#                                                    "Your task is to Extract the following information and show it to the user as a JSON object: VC name, contacts, industries that they invest in, investment rounds that they participate/lead." +
#                                                    " please return only json object"
#                        },
#                    {"role": "user", "content": f"""{plain_text}"""}
#                    ]
#    response = prompt_to_openai_api(openai_messages, 'gpt-3.5-turbo')
#    print(response)
#    return response
#
#def compare_data_with_database_data(data, db_data):
#    openai_messages = [{"role": "system", "content":
#                                                    "Please analyze this data's" +
#                                                    "and get 3 most similar vc companies"
#                        },
#                    {"role": "user", "content": f"""data is {str(data)}, and database data is {str(db_data)}"""}
#                    ]
#    response = prompt_to_openai_api(openai_messages, 'gpt-3.5-turbo')
#    print(response)
#    return response




import replicate
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_data_from_plain_text(plain_text: str):
    api = replicate.Client(api_token="r8_SDXinLdJV987RK41F2gV29Gvb6Qle6Q0poeqE")
    output = api.run(
        "meta/meta-llama-3-70b-instruct",
        input= {"prompt":
                        f"""{plain_text}""" +
                        " Your task is to Extract the following information and show it to the user as a JSON object: VC name, contacts, industries that they invest in, investment rounds that they participate/lead." +
                        " please return only json object"
                }
    )
    return ''.join(output)

async def convert_data_to_vector(data):
    try:
        api = replicate.Client(api_token="r8_SDXinLdJV987RK41F2gV29Gvb6Qle6Q0poeqE")
        output = api.run(
            "nateraw/bge-large-en-v1.5:9cf9f015a9cb9c61d1a2610659cdac4a4ca222f2d3707a68517b18c198a9add1",
            input={"texts": json.dumps(data)}
        )
        return output
    except Exception as e:
        logging.error(e)
        raise e

async def compare_data_with_database_data(new_data, most_similars):
    try:
        api = replicate.Client(api_token="r8_SDXinLdJV987RK41F2gV29Gvb6Qle6Q0poeqE")
        output = api.run(
            "meta/meta-llama-3-70b-instruct",
            input={"prompt":
                        "our programm got this json data " +
                        f"""{new_data}""" +
                        " and for this data 3 most similar data's from database collection is " +
                        f"""{most_similars}""" +
                        ", compare gathered data and this 3 datas from collection, " +
                        "please compare and analyze only with values and other relationships, not with keys, " +
                        "and return some simple conclusion, " +
                        "and extract as much information as you can from all data that you have"
                   }
        )
        return ''.join(output)
    except Exception as e:
        logging.error(e)
        raise e

"""AI assistant part"""
async def get_data_from_website(url):

    try:
        website_plain_text = scrap_website_data(url)
        response = get_data_from_plain_text(website_plain_text)
        return response
    except Exception as e:
        logging.error(e)
        raise e

async def compute_most_similar(input_vc_name, input_vector, vectordb_data):
    # Retrieve the input vector from the database collection
    input_vector = np.array(input_vector).reshape(1, -1)  # Reshape to ensure it's 2D

    # Calculate cosine similarity between input vector and all vectors in the collection
    similarities = {}
    for data in vectordb_data:
        vc_name = data['vc name']
        vector = np.array(data['vector']).reshape(1, -1)  # Reshape to ensure it's 2D
        similarity = cosine_similarity(input_vector, vector)[0][0]
        similarities[vc_name] = similarity

    # Sort the similarities dictionary by values in descending order
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Extract the top three most similar VC_names
    top_three = sorted_similarities[:3]

    return top_three


# Function to filter data list based on VC_names
def filter_data_by_vc_names(data_list, vc_names):
    return [data for data in data_list if data['vc name'] in vc_names]

async def return_conclusion(new_data, db_data, new_vector_data, vectordb_data):

    try:
        output = "Most similar VC Companies` "
        similar_vc_names = await compute_most_similar(new_vector_data["vc name"], new_vector_data["vector"], vectordb_data)
        output += str(similar_vc_names) + "\n"

        vc_names_to_filter = [vc_name for vc_name, _ in similar_vc_names]
        filtered_data = filter_data_by_vc_names(db_data, vc_names_to_filter)
        conclusion = await compare_data_with_database_data(new_data, filtered_data)
        output += conclusion

        return output
    except Exception as e:
        logging.error(e)
        raise e