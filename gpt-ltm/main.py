# Main file to run the assistant

# imports
import sys
from prompts import *
sys.path.append('')
from memory import Assistant, Message

# # index pdf files into the redis database for testing
# from shared import text_from_pdf
# index_pdf_files(os.path.join(os.curdir, 'data'))


def TestChatBot():
    # a simple chatbot to test the assistant
    system_prompt = f1_system_prompt

    assistant = None

    while True:
        question = input("What do you want to know: ")
        if question:

            # Initialization
            if assistant is None:
                assistant = Assistant()
                messages = []
                system_message = Message('system', system_prompt)
                messages.append(system_message.message())
            else:
                messages = []

            user_message = Message('user', question)
            messages.append(user_message.message())

            response = assistant.ask_assistant(messages)

            # Debugging step to print the whole response
            assistant.pretty_print_conversation_history()


# Run the test chatbot
TestChatBot()
