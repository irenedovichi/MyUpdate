import json
import os
import pickle
from pathlib import Path
from tempfile import NamedTemporaryFile

from llama_index.core import VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.readers.file import FlatReader

from rag_service.prompts import CHAT_PROMPT, KPI_PROMPT, REPORT_PROMPT
from rag_service.config import embed_model


class ChatMemory:
    """
    Enhanced memory for managing past interactions and reports.
    """
    def __init__(self, max_history=5):
        self.max_history = max_history
        self.history = []
        self.last_report = None  # Stores the last generated report

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
        Get the conversation history formatted as context for the next query.
        """
        conversation_context = "\n".join(
            f"User: {item['query']}\nAssistant: {item['response']}"
            for item in self.history
        )
        return conversation_context
    

def analyze_query(query):
    """
    Analyze the query to determine its intent.

    @param query: The user query (string).

    @return: The appropriate prompt for the query ('CHAT_PROMPT' or 'KPI_PROMPT').
    """
    kpi_keywords = {"create", "generate", "design", "suggest", "propose", "new kpi", "new kpis", "develop"}

    if any(keyword in query.lower() for keyword in kpi_keywords):
        return KPI_PROMPT
    
    return CHAT_PROMPT


def rag_interaction(data, query=None, memory=None, generate_report=False, index_file="vector_index.pkl"):
    """
    @param data list of documents to be ingested 
    @param query query to be answered
    @param memory an instance of ChatMemory to manage interaction history
    @param generate_report: If True, generates a report instead of answering a query
    @param index_file: Path to the precomputed vector index file (used only for chatbot mode)

    @return response to the query or generated report
    """
    llm = Ollama(model="llama3.2", request_timeout=180.0)

    # Generate a report (dynamic KB) or chat (use precomputed index)
    if generate_report:
        print("Generating report with dynamic KB...")
        # Simulate ingestion of dynamic documents based on the input data
        documents = []
        for response_data in data:
            file_type = response_data.get("type")
            content = response_data.get("content")

            if file_type == "json":  # JSON-like data
                with NamedTemporaryFile(mode='w+', suffix=".json", delete=True) as temp_file:
                    json.dump(content, temp_file)
                    temp_file.flush()
                    temp_path = Path(temp_file.name)
                    documents.extend(FlatReader().load_data(temp_path))
            elif file_type == "txt":  # Plain text data
                with NamedTemporaryFile(mode='w+', suffix=".txt", delete=True) as temp_file:
                    temp_file.write(content)
                    temp_file.flush()
                    temp_path = Path(temp_file.name)
                    documents.extend(FlatReader().load_data(temp_path))
            else:
                raise ValueError(f"Unsupported file type or invalid content.")

        # Create a temporary vector index for the report
        vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)
        query_engine = vector_index.as_query_engine(llm=llm, verbose=True, similarity_top_k=7)

        # Determine the prompt
        full_prompt = REPORT_PROMPT

    else:
        print("Using chatbot mode...")
        # Check if the index already exists for chatbot mode
        if os.path.exists(index_file):
            print("Loading precomputed vector index...")
            with open(index_file, "rb") as f:
                vector_index = pickle.load(f)
        else:
            print("Creating new vector index...")
            # Simulate ingestion of documents for chatbot
            documents = []
            for response_data in data:
                file_type = response_data.get("type")
                content = response_data.get("content")

                if file_type == "json":  # JSON-like data
                    with NamedTemporaryFile(mode='w+', suffix=".json", delete=True) as temp_file:
                        json.dump(content, temp_file)
                        temp_file.flush()
                        temp_path = Path(temp_file.name)
                        documents.extend(FlatReader().load_data(temp_path))
                elif file_type == "txt":  # Plain text data
                    with NamedTemporaryFile(mode='w+', suffix=".txt", delete=True) as temp_file:
                        temp_file.write(content)
                        temp_file.flush()
                        temp_path = Path(temp_file.name)
                        documents.extend(FlatReader().load_data(temp_path))
                else:
                    raise ValueError(f"Unsupported file type or invalid content.")

            vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)

            # Save the computed index to a file 
            with open(index_file, "wb") as f:
                pickle.dump(vector_index, f)

        query_engine = vector_index.as_query_engine(llm=llm, verbose=True, similarity_top_k=7)

        # Determine the prompt
        selected_prompt = analyze_query(query)
        conversation_context = memory.get_context() if memory else ""
        full_prompt = f"{conversation_context}\n{selected_prompt}\n{query}"

    response = query_engine.query(full_prompt)

    # Store the result
    if memory:
        memory.add_interaction(query, response)

    return response
