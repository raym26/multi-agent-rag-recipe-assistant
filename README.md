# 📚 Recipe PDF Assistant

A powerful Streamlit application that transforms cookbook PDFs into an interactive AI assistant. Load any cookbook PDF via URL and chat with an AI to discover recipes, ingredients, cooking techniques, and more!

## ✨ Features

- **📖 PDF Processing**: Load cookbook PDFs directly from URLs
- **🤖 AI-Powered Chat**: Interactive assistant that understands cookbook content
- **🔍 Smart Search**: Vector-based search through recipe content
- **💬 Persistent Sessions**: Chat history maintained across sessions
- **🎯 Quick Start**: Pre-built example queries to get you started
- **📱 Clean UI**: Above-the-fold design optimized for ease of use
- **🔄 Session Management**: Resume previous conversations or start fresh

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database with pgvector extension
- GROQ API key for AI functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd recipe-pdf-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   DB_URL=postgresql+psycopg://username:password@localhost:5432/database_name
   ```

4. **Set up PostgreSQL with pgvector**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your GROQ API key for AI functionality | Required |
| `DB_URL` | PostgreSQL connection string with pgvector support | `postgresql+psycopg://ai:ai@localhost:5532/ai` |

### Database Setup

The application uses PostgreSQL with the pgvector extension for storing:
- Vectorized document embeddings
- Chat history and sessions
- Assistant configurations

## 📖 Usage

### Loading a Cookbook

1. **Enter PDF URL**: Paste a direct link to a cookbook PDF in the sidebar
2. **Click "Load PDF"**: The system will process and vectorize the document
3. **Start Chatting**: Use the chat interface or quick start buttons

### Example Queries

- "What kinds of recipes are in the cookbook?"
- "Please list all the recipes in the cookbook."
- "Show me recipes with chicken"
- "What's the cooking time for [recipe name]?"
- "Can you modify this recipe for 4 people?"

### Advanced Features

- **Force Reload**: Clear existing data and reload the PDF fresh
- **Session Management**: Resume previous conversations automatically
- **Clear Database**: Remove all stored data and start over

## 🏗️ Architecture

### Core Components

- **`app.py`**: Main Streamlit application with UI logic
- **`pdf_assistant.py`**: AI assistant wrapper using Phi framework
- **`utils.py`**: Utility functions for environment setup and PDF processing

### Technology Stack

- **Frontend**: Streamlit for web interface
- **AI/ML**: Phi framework with GROQ API integration
- **Vector Database**: PostgreSQL + pgvector for semantic search
- **PDF Processing**: PyMuPDF for document analysis
- **Storage**: PostgreSQL for persistent chat sessions

### Data Flow

1. **PDF Ingestion**: URL → PDF download → Text extraction → Vectorization
2. **Query Processing**: User input → Vector search → AI reasoning → Response
3. **Session Management**: Chat history stored in PostgreSQL with run IDs

## 🎨 UI Design

The interface follows a clean, above-the-fold design philosophy:

- **Compact Sidebar**: All controls accessible without scrolling
- **Smart Layout**: Responsive design that works on different screen sizes
- **Quick Actions**: Example queries prominently displayed
- **Status Indicators**: Clear feedback on loading and processing states

## 🔧 Customization

### Adding New Example Queries

Edit the `get_example_queries()` function in `utils.py`:

```python
def get_example_queries():
    return [
        "Your custom query here",
        "Another example query",
        # Add more queries...
    ]
```

### Modifying AI Instructions

Update the assistant instructions in `pdf_assistant.py`:

```python
instructions=[
    "Your custom instruction here",
    "Additional context for the AI",
    # More instructions...
]
```

### Styling Customization

Modify the CSS in `app.py` within the `st.markdown()` section to change the appearance.

## 🐛 Troubleshooting

### Common Issues

1. **"Database connection failed"**
   - Check your PostgreSQL connection string
   - Ensure pgvector extension is installed
   - Verify database credentials

2. **"GROQ API key not found"**
   - Ensure `.env` file exists with valid `GROQ_API_KEY`
   - Check API key permissions and quota

3. **"PDF loading failed"**
   - Verify the PDF URL is accessible
   - Check if the PDF is password-protected
   - Try with a different PDF to isolate the issue

4. **"Duplicate collection errors"**
   - Use "Force reload" option to clear existing data
   - Or use "Clear Database" to reset everything

### Performance Tips

- **Large PDFs**: May take longer to process; be patient during initial load
- **Complex Queries**: Vector search performance depends on document size
- **Session History**: Clear old sessions periodically to maintain performance

## 📝 Development

### Project Structure

```
recipe-pdf-assistant/
├── app.py              # Main Streamlit application
├── pdf_assistant.py    # AI assistant logic
├── utils.py           # Utility functions
├── .env              # Environment variables (create this)
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

### Adding Features

1. **New Query Types**: Extend the assistant instructions
2. **Additional PDF Sources**: Modify the PDF loading logic
3. **Enhanced UI**: Update the Streamlit components and CSS
4. **Export Features**: Add functionality to export chat history or recipes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Phi Framework**: For the AI assistant capabilities
- **Streamlit**: For the excellent web app framework
- **pgvector**: For efficient vector similarity search
- **GROQ**: For fast AI inference

## 📞 Support

For questions, issues, or suggestions:

1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Review existing discussions and documentation

---

**Happy Cooking! 👨‍🍳👩‍🍳**

*Transform any cookbook into your personal AI cooking assistant!*
