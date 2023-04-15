import openai
from termcolor import colored
from shared import get_redis_connection
from database import get_redis_results
from prompts import *

# Set our default models and chunking size
import config
from config import COMPLETIONS_MODEL, CHAT_MODEL, INDEX_NAME, TEMPERATURE

# if you have declared an OPENAI_API_KEY in your config.py file, set it. Otherwise, it will use your environment variable if you have one set.
if config.OPENAI_API_KEY:
    openai.api_key = config.OPENAI_API_KEY

redis_client = get_redis_connection()


# A basic class to create a message as a dict for chat
class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def message(self):
        return {"role": self.role, "content": self.content}


# Assistant class to add a vector database call to its responses
class Assistant:
    def __init__(self):
        self.conversation_history = []

    # The function to retrieve OpenAI Chatbot responses
    def _get_assistant_response(self, prompt):
        try:
            completion = openai.ChatCompletion.create(
                model=CHAT_MODEL,
                messages=prompt,
                temperature=TEMPERATURE
            )
            response_message = Message(completion['choices'][0]['message']['role'], completion['choices'][0]['message']['content'])
            return response_message.message()

        except Exception as e:
            return f'Request failed with exception {e}'

    # The function to retrieve Redis search results
    def _get_search_results(self, prompt):
        latest_question = prompt
        search_content = get_redis_results(redis_client, latest_question, INDEX_NAME)['result'][0]
        return search_content

    # The function to ask the assistant a question
    def ask_assistant(self, next_user_prompt):
        [self.conversation_history.append(x) for x in next_user_prompt]
        assistant_response = self._get_assistant_response(self.conversation_history)

        # Answer normally unless the trigger sequence is used "searching_for_answers"
        if 'searching for answers' in assistant_response['content'].lower():
            question_extract = openai.Completion.create(model=COMPLETIONS_MODEL, prompt=extract_information_prompt % self.conversation_history)

            search_result = self._get_search_results(question_extract['choices'][0]['text'])

            # Insert an extra system prompt here to give fresh context to the Chatbot on how to use the Redis results
            # In this instance we add it to the conversation history, but in production it may be better to hide
            self.conversation_history.insert(-1, {"role": 'system', "content": context_system_prompt % search_result})

            assistant_response = self._get_assistant_response(self.conversation_history)

            self.conversation_history.append(assistant_response)
            return assistant_response

        # If the trigger sequence is not used, answer normally
        else:
            self.conversation_history.append(assistant_response)
            return assistant_response

    # A function to print the conversation history
    def pretty_print_conversation_history(self, colorize_assistant_replies=True):
        for entry in self.conversation_history:
            if entry['role'] == 'system':
                pass
            else:
                prefix = entry['role']
                content = entry['content']
                output = colored(prefix + ':\n' + content, 'green') if colorize_assistant_replies and entry['role'] == 'assistant' else prefix + ':\n' + content
                print(output)

    # A function to summarise a query
    def summary_of_query(self, query):
        result_df = get_redis_results(redis_client, query, index_name=INDEX_NAME)
        result_df.head(2)

        # Build a prompt to provide the original query, the result and ask to summarise for the user
        summary_prepped = summary_prompt.replace('SEARCH_QUERY_HERE', query).replace('SEARCH_RESULT_HERE', result_df['result'][0])

        # Call GPT-3 to summarise the result
        summary = openai.Completion.create(engine=COMPLETIONS_MODEL, prompt=summary_prepped, max_tokens=500)

        # Response provided by GPT-3
        return summary['choices'][0]['text']
