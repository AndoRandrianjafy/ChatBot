import logging
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import openai

import agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialisation de l'application FLask
app = Flask(__name__)

# Chargement de l'API KEY
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

# Initialisation client
client = openai.api_key = OPENAI_API_KEY


# Recherche des données sur le web
def search_web_for_answer(question):
  search_url = f"https://www.mademoiselleai.com/search?q={question}"
  try:
    page = requests.get(search_url)
    print("URL Accessed: ", search_url)
    print("Page Status: ", page.status_code)
    soup = BeautifulSoup(page.content, "html.parser")
    answers = soup.find_all("div", class_="answer")
    if answers:
      return ' '.join([answer.get_text() for answer in answers])
    else:
      print("No answers found in page content.")
      return None
  except Exception as e:
    print("Error occurred: ", str(e))
    return None


# Fonction reponse OpenAI
def get_openai_response(message):
  try:
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role":
            "system",
            "content":
            "Répondez en français de manière concise, claire et polie."
        }, {
            "role": "user",
            "content": message
        }],
        temperature=0.7,
        max_tokens=500)
    return response.choices[0].message['content']
  except Exception as e:
    return str(e)


# retourner des images
def get_dalle_image(prompt):
  try:
    logger.info(f"Envoi de la requête à DALL·E avec le prompt: {prompt}")
    response = openai.Image.create(model="dall-e-3",
                                   prompt=prompt,
                                   n=1,
                                   size="1024x1024")
    # Log de la réponse
    logger.info(f"Réponse de DALL·E: {response}")

    # Extrayez l'URL de l'image de la réponse
    image_url = response['data'][0]['url']
    logger.info(f"URL de l'image générée: {image_url}")
    return image_url
  except Exception as e:
    # Log de l'erreur
    logger.error(f"Erreur lors de la génération de l'image avec DALL·E: {e}")
    return str(e)


@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  user_input = data.get('message', '')
  response_type = data.get('type', 'text')

  if not user_input:
    return jsonify({"error": "Pas de message"}), 400

  web_answer = search_web_for_answer(user_input)
  #response = web_answer if web_answer else get_openai_response(user_input)
  if response_type == 'image':
    # Générez une image avec DALL·E
    response = get_dalle_image(user_input)
    return jsonify({"response": response, "response_type": "image"})
  else:
    response = get_openai_response(user_input)
    return jsonify({"response": response})


# Run server
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
