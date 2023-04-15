import pandas as pd
import numpy as np
import openai
import os
import requests
from typing import Iterator
import tiktoken
from numpy import array, average

# redis imports
from redis import Redis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import (IndexDefinition, IndexType)
from redis.commands.search.field import (TextField, NumericField, VectorField)
from transformers import handle_file_string

# local imports
from config import PREFIX, COMPLETIONS_MODEL, EMBEDDINGS_MODEL, CHAT_MODEL, TEXT_EMBEDDING_CHUNK_SIZE, VECTOR_FIELD_NAME, VECTOR_DIM, DISTANCE_METRIC, INDEX_NAME, TEMPERATURE
from shared import get_redis_connection, text_from_pdf

# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ImportWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
#%%

# Set pandas display options
pd.set_option('display.max_colwidth', 0)


redis_client = get_redis_connection()

# Create a Redis index to hold our data
def create_hnsw_index(redis_conn, vector_field_name, vector_dimensions=1536, distance_metric='COSINE'):
    redis_conn.ft().create_index([
        VectorField(vector_field_name, "HNSW", {"TYPE": "FLOAT32", "DIM": vector_dimensions, "DISTANCE_METRIC": distance_metric}),
        TextField("filename"),
        TextField("text_chunk"),
        NumericField("file_chunk_index")
    ])


# Make query to Redis
def query_redis(redis_conn, query, index_name, top_k=2):
    # Creates embedding vector from user query
    embedded_query = np.array(openai.Embedding.create(
        input=query,
        model=EMBEDDINGS_MODEL,
    )["data"][0]['embedding'], dtype=np.float32).tobytes()

    # prepare the query
    q = Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]').sort_by('vector_score').paging(0, top_k).return_fields('vector_score', 'filename', 'text_chunk', 'text_chunk_index').dialect(2)
    params_dict = {"vec_param": embedded_query}

    # Execute the query
    results = redis_conn.ft(index_name).search(q, query_params=params_dict)

    return results


# Get mapped documents from Weaviate results
def get_redis_results(redis_conn, query, index_name):
    # Get most relevant documents from Redis
    query_result = query_redis(redis_conn, query, index_name)

    # Extract info into a list
    query_result_list = []
    for i, result in enumerate(query_result.docs):
        result_order = i
        text = result.text_chunk
        score = result.vector_score
        query_result_list.append((result_order, text, score))

    # Display result as a DataFrame for ease of us
    result_df = pd.DataFrame(query_result_list)
    result_df.columns = ['id', 'result', 'certainty']
    return result_df


# The function to retrieve Redis search results
def _get_search_results(self, prompt):
    latest_question = prompt
    search_content = get_redis_results(redis_client, latest_question, INDEX_NAME)['result'][0]
    return search_content


def index_pdf_files(data_dir, INDEX_NAME=INDEX_NAME, VECTOR_FIELD_NAME=VECTOR_FIELD_NAME):
    pdf_files = sorted([x for x in os.listdir(data_dir) if 'DS_Store' not in x])
    # Define RediSearch fields for each of the columns in the dataset
    # This is where you should add any additional metadata you want to capture
    filename = TextField("filename")
    text_chunk = TextField("text_chunk")
    file_chunk_index = NumericField("file_chunk_index")

    # define RediSearch vector fields to use HNSW index
    text_embedding = VectorField(VECTOR_FIELD_NAME,
                                 "HNSW", {
                                     "TYPE": "FLOAT32",
                                     "DIM": VECTOR_DIM,
                                     "DISTANCE_METRIC": DISTANCE_METRIC
                                 })
    # Add all our field objects to a list to be created as an index
    fields = [filename, text_chunk, file_chunk_index, text_embedding]
    redis_client.ping()

    # Check if index exists
    try:
        redis_client.ft(INDEX_NAME).info()
        print("Index already exists")
    except Exception as e:
        print(e)
        # Create RediSearch Index
        print('Not there yet. Creating')
        redis_client.ft(INDEX_NAME).create_index(
            fields=fields,
            definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
        )

    # Initialise tokenizer
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Process each PDF file and prepare for embedding
    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_dir, pdf_file)
        print(f"Processing {pdf_file}...")
        text = text_from_pdf(pdf_path)

        # Chunk each document, embed the contents and load to Redis
        handle_file_string((pdf_file, text), tokenizer, redis_client, VECTOR_FIELD_NAME, INDEX_NAME)

    # Check that our docs have been inserted
    print("Number of documents in index:", redis_client.ft(INDEX_NAME).info()['num_docs'])

