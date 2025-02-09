import json 
from pathlib import Path
from tempfile import NamedTemporaryFile

from llama_index.core import VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.readers.file import FlatReader

from rag_service.constants import CHAT_PROMPT, REPORT_PROMPT
from rag_service.config import embed_model


def rag_interaction(data, query=None):
    """
    @param vector_store vector store to be used for the RAG system
    @param documents list of documents to be ingested (each in json format)
    @param query query to be answered

    @return response to the query
    """

    llm = Ollama(model="llama3.2", request_timeout=180.0) 

    documents = []
    for response_data in data:

        with NamedTemporaryFile(mode='w+', suffix=".json", delete=True) as temp_file:
            json.dump(response_data, temp_file)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            documents.extend(FlatReader().load_data(temp_path))


    vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)

    query_engine = vector_index.as_query_engine(llm=llm, verbose=True, similarity_top_k=7)

    if query is None:
        response = query_engine.query(REPORT_PROMPT)
    else:
        response = query_engine.query(CHAT_PROMPT + "\n" + query)
    
    return response
