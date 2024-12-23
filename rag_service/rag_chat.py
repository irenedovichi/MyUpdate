import json 
from pathlib import Path
from tempfile import NamedTemporaryFile

from llama_index.core import VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.readers.file import FlatReader

from rag_service.constants import CHAT_PROMPT, REPORT_PROMPT
from rag_service.config import embed_model


class ChatMemory:
    """
    A simple memory implementation for storing and managing past interactions.
    """
    def __init__(self, max_history=5):
        self.max_history = max_history
        self.history = []

    def add_interaction(self, query, response):
        """
        Add a new interaction to memory.
        """
        self.history.append({"query": query, "response": response})
        # Limit memory size
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self):
        """
        Get the history formatted as context for the next query.
        """
        return "\n".join(f"User: {item['query']}\nAssistant: {item['response']}" for item in self.history)


def rag_interaction(data, query=None, memory=None):
    """
    @param vector_store vector store to be used for the RAG system
    @param documents list of documents to be ingested (each in json format)
    @param query query to be answered
    @param memory an instance of ChatMemory to manage interaction history

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

    # Include memory context
    context = memory.get_context() if memory else ""
    full_prompt = f"{context}\n{CHAT_PROMPT}\n{query}" if query else REPORT_PROMPT

    response = query_engine.query(full_prompt)

    # Store the interaction in memory
    if memory and query:
        memory.add_interaction(query, response)

    return response
