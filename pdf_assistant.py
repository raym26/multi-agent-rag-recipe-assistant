import os
import inspect

# Set environment variable for protobuf
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Monkeypatch for older libraries using deprecated inspect.getargspec
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

from typing import Optional, List
from phi.assistant import Assistant
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector2


class PDFAssistant:
    def __init__(self,
                 pdf_url: str,
                 collection_name: str,
                 db_url: str,
                 run_id: Optional[str] = None,
                 user_id: str = 'user'):
        """Initialize the PDF Assistant with necessary parameters."""
        self.pdf_url = pdf_url
        self.collection_name = collection_name
        self.db_url = db_url
        self.user_id = user_id
        self.run_id = run_id
        self.assistant = None
        self.storage = None
        self.knowledge_base = None

    def initialize_knowledge_base(self):
        """Load the knowledge base from the PDF URL."""
        print(f"Attempting to load PDF from: {self.pdf_url}")
        print(f"Database URL: {self.db_url}")
        print(f"Collection name: {self.collection_name}")

        # Create knowledge base with vector DB (using default OpenAI embeddings)
        self.knowledge_base = PDFUrlKnowledgeBase(
            urls=[self.pdf_url],
            vector_db=PgVector2(collection=self.collection_name, db_url=self.db_url)
        )

        try:
            print("Loading knowledge base...")
            self.knowledge_base.load()
            print("Knowledge base loaded successfully")
            print(f"Number of documents: {self.knowledge_base.num_documents}")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            import traceback
            traceback.print_exc()
            raise

        return self.knowledge_base

    def initialize_storage(self):
        """Initialize the assistant storage."""
        self.storage = PgAssistantStorage(table_name='pdf_assistant', db_url=self.db_url)
        return self.storage

    def get_existing_run_ids(self):
        """Get all existing run IDs for the current user."""
        if not self.storage:
            self.initialize_storage()
        return self.storage.get_all_run_ids(self.user_id)

    def initialize_assistant(self):
        """Initialize the assistant with the knowledge base and storage."""
        if not self.knowledge_base:
            self.initialize_knowledge_base()

        if not self.storage:
            self.initialize_storage()

        self.assistant = Assistant(
            run_id=self.run_id,
            user_id=self.user_id,
            knowledge_base=self.knowledge_base,
            storage=self.storage,
            show_tool_calls=False,  # Temporarily enable to debug
            search_knowledge=True,  # Enable vector search
            read_chat_history=True,
            # Add instructions to help the assistant understand its role
            instructions=[
                f"You are a helpful assistant that answers questions about a cookbook PDF document loaded from: {self.pdf_url}",
                f"The PDF content is stored in the '{self.collection_name}' collection.",
                "Always search the knowledge base first when answering questions about the document content.",
                "When prompted about listing recipes, search thoroughly and provide ALL recipes found in the document.",
                "If you find relevant information in the knowledge base, use it to provide detailed answers.",
                "If the user asks about recipes, ingredients, or cooking instructions, search for this information in the PDF.",
                "Be specific about which document you're referencing and include the PDF source information."
            ]
        )

        self.run_id = self.assistant.run_id
        return self.assistant

    def chat(self, message: str):
        """Send a message to the assistant and get a response."""
        if not self.assistant:
            self.initialize_assistant()

        response = self.assistant.chat(message)

        # Handle generator response
        if hasattr(response, '__iter__') and not isinstance(response, str):
            return "".join(str(chunk) for chunk in response)
        else:
            return str(response)

    def get_chat_history(self):
        """Get the chat history for the current session."""
        # Note: Chat history is managed by the storage backend
        # The assistant will automatically load previous conversations
        # when initialized with the same run_id
        if not self.assistant:
            self.initialize_assistant()
        return []  # Return empty list for now, as history is managed internally