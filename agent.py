import json
import os


def creer_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("ID assistant existe déja.")
  else:
    file = client.files.create(file=open("mademoiselleai.docx", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(instructions="""
          Répondez en français de manière concise, claire et polie. L'assistant est destiné à :
            - Fournir des informations spécifiques aux chefs d'entreprises sur l'optimisation des opérations commerciales par l'IA.
            - Guider les entrepreneurs numériques dans le lancement de projets utilisant l'IA.
            - Offrir des conseils personnalisés pour générer des revenus en ligne.

          """,
           model="gpt-4-1106-preview",
           tools=[{
           "type": "retrieval"
           }],
           file_ids=[file.id])

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Creer le nouvel assistant et enregistrer ID.")

    assistant_id = assistant.id

  return assistant_id
