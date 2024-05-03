import os
import logging
from scrapper import scrap_website_data

import replicate
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = os.environ.get('REPLICATE_API_TOKEN')
api = replicate.Client(api_token=API_KEY)

def get_data_from_plain_text(plain_text: str):
    try:
        output = api.run(
            "meta/meta-llama-3-70b-instruct",
            input= {"prompt":
                            f"""{plain_text}""" +
                            " Your task is to Extract the following information and show it to the user as a JSON object: VC name, contacts, industries that they invest in, investment rounds that they participate/lead." +
                            " please return only json object"
                    }
        )
        return ''.join(output)
    except Exception as e:
        logging.error(e)
        raise e

#TODO
async def convert_data_to_vector(data):
    try:
        output = api.run(
            "nateraw/bge-large-en-v1.5:9cf9f015a9cb9c61d1a2610659cdac4a4ca222f2d3707a68517b18c198a9add1",
            input={"texts": json.dumps([data]) }
        )
        return output
    except Exception as e:
        logging.error(e)
        raise e

async def compare_data_with_database_data(new_data, most_similars, similar_vc_names):
    try:
        output = api.run(
            "meta/meta-llama-3-70b-instruct",
            input={"prompt":
                        "our programm got this json data " +
                        f"""{new_data}""" +
                        " and for this data 3 most similar data from database collection is " +
                        f"""{most_similars}.""" + f"""Most similar data is by this sequence: {similar_vc_names}.""" +
                        "Please compare gathered data and this 3 data from collection(Please compare activities made by this companies), " +
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
async def get_data_from_website_and_vector_embedding(url):

    try:
        website_plain_text = scrap_website_data(url)
        vector = await convert_data_to_vector(website_plain_text)
        response = get_data_from_plain_text(website_plain_text)
        return response, vector
    except Exception as e:
        logging.error(e)
        raise e

async def compute_most_similar(input_vector, vectordb_data):
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
        similar_vc_names = await compute_most_similar(new_vector_data["vector"], vectordb_data)
        output += str(similar_vc_names) + "\n\n"

        vc_names_to_filter = [vc_name for vc_name, _ in similar_vc_names]
        filtered_data = filter_data_by_vc_names(db_data, vc_names_to_filter)
        conclusion = await compare_data_with_database_data(new_data, filtered_data, similar_vc_names)
        output += conclusion

        return output
    except Exception as e:
        logging.error(e)
        raise e