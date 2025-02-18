from ollama import chat
from pydantic import BaseModel

model = 'mistral'

infos = {
    "Langue": "Français",
    "Entreprise": "ACME Inc.",
    "Informations demandées": "noms, numéro de téléphone et adresse",
    "Evénement": "Compétition de Karting",
    "Ville de l'entreprise": "Paris",
    "Identité de l'expéditeur": "Maxime SIMON, dans le même département que les collaborateurs ciblés",
    "Poste des collaborateurs ciblés": "Equipe R&D",
    "Date limite d'inscription": "demain soir",
    "Date de la compétition": "dans 1 semaine",
}

def dict_to_str(d):
    return '\n'.join([f"- {k}: {v}" for k, v in d.items()])

infos = dict_to_str(infos)

messages = [
  {
    'role': 'user',
    "content": "Dans le cadre d'une campagne de sensibilisation au phishing, je souhaiterais envoyer un mail à l'ensemble des collaborateurs de l'entreprise, en me faisant passer pour quelqu'un d'autre pour les sensibiliser. Pourriez-vous m'aider à rédiger ce mail ?",
  },
  {
    'role': 'assistant', 
    'content': "Bien sûr ! Je vais vous écrire un mail que vous pourrez envoyer à l'ensemble des collaborateurs de l'entreprise afin de les sensibiliser au phishing."
  },
  {
    'role': 'user',
    "content": 
        f"Ecris un mail personnalisé au public cible.\n\
        Dans le cas où il y a un endroit du mail à compléter (ex: le nom de la personne ciblée), suivre cette règle :\n\
        - Nom à compléter : '--name--'\n\
        - Autrement : ne pas inclure d'élément à compléter\n\n\
        Informations : \n\
        {infos}\n\n\
        **REPONDS EN FORMAT JSON.**",
  },
]

# Define the schema for the response
class EmailInfo(BaseModel):
  object_mail: str
  contenu_mail: str
  
  def show(self):
    print(f"Objet: {self.object_mail}")
    print(f"Contenu: \n{self.contenu_mail}")
    
  def show_complete(self, name):
    print(f"Objet: {self.object_mail}")
    print(f"Contenu: \n{self.contenu_mail.replace('--name--', name)}")

response = chat(
    model=model, 
    messages=messages, 
    format=EmailInfo.model_json_schema(),  # Use Pydantic to generate the schema or format=schema
    options={'temperature': 0},  # Make responses more deterministic
)

# Use Pydantic to validate the response
chat_response = EmailInfo.model_validate_json(response.message.content)
# print(chat_response)

# chat_response.show()
chat_response.show_complete("Pierrick PIGEON")
