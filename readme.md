The Gemma Document Q & A Chatbot is a Streamlit application that allows users to upload various document formats (PDF, DOCX, DOC) and ask questions based on the content of those documents. The chatbot uses the Groq API for language model interactions and Google Generative AI for embeddings. The chatbot's responses are stored in an SQLite database, and a chat history is displayed in a conversational flow format.

Features
Upload multiple document formats (PDF, DOCX, DOC)
Create a vector store from the uploaded documents
Ask questions based on the content of the documents
Display chat history with a conversational flow
Dark theme UI
Save chat history in an SQLite database
Installation

Create a virtual environment:


python -m venv venv
Activate the virtual environment:

On Windows:


.\venv\Scripts\activate
On macOS/Linux:


source venv/bin/activate
Install the required dependencies:


pip install -r requirements.txt
Set up the environment variables:

Create a .env file in the root directory and add the following variables:

env

GROQ_API_KEY=<your_groq_api_key>
GOOGLE_API_KEY=<your_google_api_key>
Usage
Run the Streamlit app:


streamlit run main.py
Upload Documents:

Use the file uploader to upload documents (PDF, DOCX, DOC).
The uploaded files are temporarily saved in a temp_file directory until the app is reloaded.
Create Vector Store:

Click on the "Create Vector Store" button to process the uploaded documents and create a vector store.
Ask Questions:

Enter your question in the text input field and get responses based on the uploaded documents.