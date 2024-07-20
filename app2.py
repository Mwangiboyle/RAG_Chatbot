import os
import streamlit as st
import tempfile
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader, Docx2txtLoader, PyMuPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import database
import shutil

load_dotenv()

# Load API keys
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# Initialize the SQLite database
# Initialize the SQLite database
db_file = 'chat_history.db'
conn = database.create_connection(db_file)
database.create_table(conn)

st.title("Gemma Document Q & A Chatbot")
ai=st.chat_message("assistant")
ai.write("How may I help you today")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma-7b-it")
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Questions: {input}
    """
)

def save_uploaded_files(uploaded_files):
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    return file_paths, temp_dir

def vector_embeddings():
    try:
    
        if "vectors" not in st.session_state:
            st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
            st.session_state.docs = []
            for file_path in file_paths:
                if file_path.endswith(".pdf"):
                    loader = PyMuPDFLoader(file_path)
                elif file_path.endswith(".docx" or ".doc"):
                    loader = Docx2txtLoader(file_path)
                else:
                    st.error("Unsupported file type")
                    return False
                
                st.session_state.docs.extend(loader.load())
            
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
            st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False
    
uploaded_files = st.sidebar.file_uploader("Upload files", type=["pdf", "docx", "doc"], accept_multiple_files=True)

if uploaded_files:
    file_paths, temp_dir = save_uploaded_files(uploaded_files)
    st.session_state.uploaded_files = file_paths
    
if st.sidebar.button("Submit your document"):
    if vector_embeddings()==True:
        st.success('Document submitted Sucessfully', icon="✅")

# Custom CSS for dark theme chat layout
st.markdown("""
<style>
body {
    background-color: #2c2f33;
    color: #ffffff;
}
.chat-container {
    display: flex;
    flex-direction: column;
}

.chat-message {
    display: flex;
    padding: 10px;
    margin: 5px 0;
    border-radius: 10px;
}

.user-message {
    justify-content: flex-end;
    background-color: #7289da;
    text-align: right;
    color: #ffffff;
}

.bot-message {
    justify-content: flex-start;
    background-color: #4f545c;
    text-align: left;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)
# Display chat history
prompt1 = st.chat_input("Ask a question from your document")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if prompt1 and st.session_state.get("vectors"):
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({'input': prompt1})
    answer = response['answer']
     
    # Save question and answer to chat history
    st.session_state.chat_history.append(("user", prompt1))
    st.session_state.chat_history.append(("bot", answer))
    
     # Save question and answer to the SQLite database
    database.insert_chat_history(conn, prompt1, answer)
    
    with st.expander("Document Similarity Search"):
        for i, doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write("---------------------------")

# Display chat history
st.write("### Chat History")
st.write('<div class="chat-container">', unsafe_allow_html=True)
for sender, message in st.session_state.chat_history:
    if sender == "user":
        user_message = f'<div class="chat-message user-message"><div>{message}</div></div>'
        st.write(user_message, unsafe_allow_html=True)
    else:
        bot_message = f'<div class="chat-message bot-message"><div>{message}</div></div>'
        st.write(bot_message, unsafe_allow_html=True)
st.write('</div>', unsafe_allow_html=True)

# Close the database connection when the script ends
conn.close()

# Clean up the temporary directory when the script ends
if 'temp_dir' in locals():
    shutil.rmtree(temp_dir)
