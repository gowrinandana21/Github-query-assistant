

## Overview

Understanding an unfamiliar or large codebase can take time. **GitHub Query Assistant** helps developers explore a repository by retrieving relevant code sections and using a language model to explain them.

Paste a public GitHub repository URL into the chat interface. The application clones the repository, reads supported source files, splits the code into overlapping chunks, creates vector embeddings, and stores them in a Qdrant collection. You can then ask questions about the code and receive answers based on the retrieved snippets, with the source file paths shown for reference.

## Features

- **GitHub repository loading:** Clones a repository from its URL.
- **Source-code extraction:** Reads Python, JavaScript, TypeScript, Java, C, C++, HTML, and CSS files.
- **Code chunking:** Splits files into 40-line chunks with a 10-line overlap to preserve nearby context.
- **Semantic retrieval:** Uses the `all-MiniLM-L6-v2` Sentence Transformers model to create 384-dimensional embeddings.
- **Vector search:** Stores and retrieves code embeddings using Qdrant.
- **LLM-based explanations:** Sends the retrieved code context and the user's question to the Mistral chat API.
- **Source references:** Displays the file paths of retrieved code snippets.
- **Chat interface:** Provides an interactive Streamlit interface.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Language | Python |
| Repository cloning | GitPython |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector database | Qdrant Client |
| LLM | Mistral API |
| Retrieval approach | Retrieval-Augmented Generation (RAG) |

## How It Works

1. **Enter a repository URL:** The user submits a GitHub repository URL through the Streamlit chat interface.
2. **Clone the repository:** GitPython performs a shallow clone of the repository.
3. **Read source files:** The loader extracts files with supported source-code extensions.
4. **Chunk the code:** Each file is divided into overlapping chunks, retaining file paths and line ranges.
5. **Generate embeddings:** Sentence Transformers converts each chunk into a 384-dimensional vector.
6. **Store and retrieve:** Qdrant stores the vectors and retrieves code chunks relevant to the user's question.
7. **Generate an explanation:** The retrieved snippets and question are sent to the Mistral API, which generates a concise answer grounded in the provided repository context.
8. **Show references:** The interface displays the file paths used to generate the answer.

## Project Structure

```text
Github-query-assistant/
│
├── app.py
├── requirements.txt
├── test_clone.py
│
└── backend/
    ├── repo_loader.py
    ├── code_reader.py
    ├── code_parser.py
    ├── embeddings.py
    ├── index_repo.py
    ├── vector_store.py
    └── llm_explainer.py
```

## Getting Started

### Prerequisites

- Python 3.9 or later
- Git installed and available on your PATH
- A Mistral API key

### 1. Clone this project

```bash
git clone https://github.com/gowrinandana21/Github-query-assistant.git
cd Github-query-assistant
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install requests python-dotenv
```

`requests` and `python-dotenv` are also required by the current Mistral API integration.

### 4. Configure your API key

Create a file named `.env` in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

Replace the example value with your own API key. Do not commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open it in your browser.

## How to Use

1. Start the application.
2. Paste a public GitHub repository URL into the chat input.
3. Wait for the repository to be cloned and indexed.
4. Ask questions about its code, such as:
   - "Explain the main application flow."
   - "Where is the database connection handled?"
   - "How does authentication work?"
   - "Which files handle repository loading?"
5. Review the answer and the reference file paths displayed by the application.

## Current Limitations

- The repository loader is designed for public GitHub repositories; private-repository authentication is not configured.
- Only the source file extensions listed in the Features section are indexed.
- The current Qdrant client uses in-memory storage. Indexed vectors are not persisted across application restarts.
- The application depends on a valid Mistral API key and network access to the Mistral API.
- Answers depend on the code snippets retrieved for a question. Review the referenced source files when making important decisions.

## Security

- Keep API keys in your local `.env` file.
- Never commit API keys, passwords, or other secrets to GitHub.
- Only submit repositories that you are permitted to access and analyze.

## Author

**Gowri Nandana R**

GitHub: [@gowrinandana21](https://github.com/gowrinandana21)

---

If you find a problem or have a suggestion, feel free to open an issue in this repository.
'''
path = Path("/mnt/data/README.md")
path.write_text(readme, encoding="utf-8")
print(f"Created {path}")
