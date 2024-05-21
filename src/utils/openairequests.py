from openai import OpenAI
import base64
import requests

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
client = OpenAI(api_key=api_key)
import requests
import base64

import time

def safe_api_call(call_func, *args, **kwargs):
    for i in range(5):  # Attempt a few retries
        try:
            return call_func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            print(f"Request failed, retry {i+1}/5")
            time.sleep((i + 1) * 2)  # Exponential back-off
    return None

def encode_image(image_path):
    """Encode an image file into a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_text_from_image(image_path):
    return safe_api_call(get_text_from_imageprocess, image_path)
def get_text_from_imageprocess(image_path):
    """Retrieve text description from an image using an external API."""
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "name all objects with their colors and material. write 5 words that describe the room. don't format it, just write it as you see it."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.
        response_data = response.json()  # Attempt to decode JSON
        return str(response_data["choices"][0]["message"]["content"])
    except requests.exceptions.HTTPError as http_err:
        # Specific errors related to the HTTP request
        print(f"HTTP error occurred: {http_err}")
        print(f"Status code: {response.status_code}")
    except requests.exceptions.RequestException as req_err:
        # Broad request exceptions
        print(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        # Specific errors related to JSON decoding
        print(f"JSON decode error: {json_err}")
    except (KeyError, TypeError, IndexError) as parse_err:
        # Errors related to accessing parts of the response
        print(f"Error parsing response: {parse_err}")
        print("Response content may be malformed or unexpected:", response.text)
    return None  # Return None if any error occurs


def get_openai_embeddings(text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
            "model": "text-embedding-ada-002",
        "input": text
    }

    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload)
    #print(response.json()["data"][0]["embedding"])
    try:
        return response.json()["data"][0]["embedding"]
    except (KeyError, TypeError, IndexError) as e:
        print(f"Error parsing response: {e}")
        print("Response content:", response.json())
        return None

def evaluate_prompt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            #{"role": "system", "content": "You are a food specialist but also a data scientist who is evaluating a dish. You get an entry of a dataset and you should add 3 more columns to the row the first is the type of cooking cuisine (cultural origin) and the second is the course type into one these categories {starter, main, dessert,side,beverage} and the third is the dietary classification into one of these categroies {vegan, vegetarian, omnivorous}.give it back in the format without contextual information: [cuisine,course type,dietary classification]"},
            {
                "role": "system",
                "content": """You are a food specialist and a data scientist tasked with evaluating a dish from a dataset entry. Your objective is to:
                1. Extract only the ingredients with their measurements listed in for a recipe name from the input in a list it is important that all ingredients which are in the list from the data are in the list.
                2. Convert the measurements in the list of these ingredients to either grams(g) or milliliters(ml).
                3. Format the output as a list of lists, where each inner list contains the 'Recipe Name', an 'Ingredient', its 'Amount' (only use one point floating precision. no arithmetic operations), 'Unit'(always only use 'g' or 'ml'), its 'food category' (for example pasta, meat, vegetable, fruit,...) and the 'Basic Taste' of the ingredient. Ensure the output contains no extra text, contextual explanations, newline characters, or unnecessary symbols.Format the output strictly as follows:[[\"Recipe Name\",\"Ingredient1\", \"Amount\", \"Unit\", \"Food Category\",\"Basic Taste\"], [\"Recipe Name\",\"Ingredient2\", \"Amount\", \"Unit\", \"Food Category\",\"Basic Taste\"], [\"Recipe Name\",\"Ingredient3\", \"Amount\", \"Unit\", \"Food Category\",\"Basic Taste\"],...]"""},
            {"role": "user", "content": prompt}
        ],temperature=0
    )
    return response.choices[0].message.content
