from redis import Redis
import numpy as np
from config import *
import pdfplumber


def text_from_pdf(pdf_path):
    # text = textract.process(pdf_path, method='pdfminer')
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Get a Redis connection
def get_redis_connection(host=REDIS_HOST, port=REDIS_PORT, db=0):
    r = Redis(host=host, port=port, db=db, decode_responses=False)
    return r


# Create a Redis pipeline to load all the vectors and their metadata
def load_vectors(client: Redis, input_list, vector_field_name):
    p = client.pipeline(transaction=False)
    for text in input_list:
        key = f"{PREFIX}:{text['id']}"
        item_metadata = text['metadata']
        item_keywords_vector = np.array(text['vector'], dtype='float32').tobytes()
        item_metadata[vector_field_name] = item_keywords_vector
        p.hset(key, mapping=item_metadata)
    p.execute()
