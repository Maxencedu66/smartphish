from ollama import chat
from ollama import ChatResponse

model = 'mistral'

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  }
]

response: ChatResponse = chat(model=model, messages=messages)

# print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)


while True:
  user_input = input('Chat with history: ')
  response = chat(
    model=model,
    messages=messages
    + [
      {'role': 'user', 'content': user_input},
    ],
  )

  # Add the response to the messages to maintain the history
  messages += [
    {'role': 'user', 'content': user_input},
    {'role': 'assistant', 'content': response.message.content},
  ]
  print(response.message.content + '\n')