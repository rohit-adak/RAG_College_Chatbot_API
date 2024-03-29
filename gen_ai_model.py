import os
import pandas as pd
import google.generativeai as genai
from uuid import uuid4
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from datetime import datetime
from langchain.chains import create_retrieval_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)
from database import connect_db
import psycopg2

# Load environment variables
load_dotenv()


# Template for chat prompts
template = """
[INTRODUCTION]
Your name is KHALNAIK, You are an ARTIFICIAL INTELLIGENCE who help Students to remain query free 
You were Created and owned by someone known Tony Stank...😼 maybe, 

[GREETINGS]
On receiving any greetings make sure to greet back

[HELP]
On prompt of `Help` suggest some questions the user could ask you !

[OUT OF CONTEXT ANSWERS]
Answer the question in humanized sentence, based following context:

WHEN question is out of context say the below with the reason for not answering: 
```
Can't help here you may use the followings below :
- [WhatsApp](https://wa.me/+919819342606)
- [RSET WEBSITE](https://www.rset.edu.in/gscc)```

[CONTEXT]

<context>
{context}
</context>

[SUGGESTED QUESTIONS]
Return Answer in single sencentence in markdown format

Suggest more questions with in the context in below format:
**You can also ask for** 
 - 
 - 
 - 

Question:{input}
"""


# Configure Google Generative AI
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# Initialize Google Generative AI chatbot
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)


with open(r'assets/general_qna.txt', 'r') as file:
    gen_data = file.read()

with open(r'assets/class_qna.txt', 'r') as file:
    class_data = file.read()



# Initialize embeddings and vectorstore
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Text splitting component
text_splitter = RecursiveCharacterTextSplitter()  # Clearly instantiate the splitter
gen_splits = text_splitter.split_text(gen_data)  # Split the input data for all general queries
class_splits = text_splitter.split_text(class_data)  # Split the input data all class specific queries

# [FOR GENERAL QUERIES]
# Vector store for embedding representations
gen_vectorstore = FAISS.from_texts(gen_splits, embeddings)  # Construct vector store from text and embeddings 
gen_retriever = gen_vectorstore.as_retriever()  # Designate the vector store as a retrieval engine 

# [FOR CLASS QUERIES]
# Vector store for embedding representations
class_vectorstore = FAISS.from_texts(class_splits, embeddings)  # Construct vector store from text and embeddings
class_retriever = class_vectorstore.as_retriever()  # Designate the vector store as a retrieval engine 

# [FOR GENERAL QUERIES]
# Document prompt creation
gen_doc_prompt = ChatPromptTemplate.from_template(template=template)  # Create prompt from template
gen_doc_chain = gen_doc_prompt | llm | StrOutputParser()  # Chain prompt, LLM, and output parser

# [FOR CLASS QUERIES]
# Document prompt creation
class_doc_prompt = ChatPromptTemplate.from_template(template=template)  # Create prompt from template
class_doc_chain = class_doc_prompt | llm | StrOutputParser()  # Chain prompt, LLM, and output parser

# Retriever integration
gen_retriever_chain = create_retrieval_chain(gen_retriever, gen_doc_chain)  # Build chain for retr for GENERAL QUERIES
class_retriever_chain = create_retrieval_chain(class_retriever, class_doc_chain)  # Build chain for retr for CLASS QUERIES

def chat_logger(user, prompt, response, source, time_stamp=None, id=None) -> None:
    """
    Logs chat interactions into a database.

    Args:
        user (str): User initiating the chat.
        prompt (str): Prompt or question from the user.
        response (str): Response from the AI system.
        source (str): Source of the interaction.
        time_stamp (str, optional): Timestamp of the interaction. Defaults to current time if not provided.
        id (str, optional): Unique identifier for the interaction. Defaults to a generated UUID if not provided.
    """
    if time_stamp is None:
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if id is None:
        id = uuid4()
    
    data = {
        'id': id,
        'Timestamp': time_stamp,
        'User': user,
        'Prompt': prompt,
        'Response': response,
        'Source': source}

    try:
        connection = connect_db()
        print("Connected to database!")
        # Create a cursor object
        cursor = connection.cursor()
        # SQL query to insert data into the table
        insert_query = """
        INSERT INTO chatbot_logs (id, "Timestamp", "User", "Prompt", "Response", "Source")
        VALUES (%(id)s, %(Timestamp)s, %(User)s, %(Prompt)s, %(Response)s, %(Source)s);
        """
        # Execute the query
        cursor.execute(insert_query, data)
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print("Error inserting data into the database:", e)
    except Exception as e:
        print("Error:", e)



# Function to handle user input and generate response
def ask_ai(user_question, user, source, time_stamp=None, id=None,load_class=False):
    """
    Handles user input and generates a response using a retriever chain.

    Args:
        user_question (str): User's question or input.
        user (str): User initiating the chat.
        source (str): Source of the interaction.
        time_stamp (str, optional): Timestamp of the interaction. Defaults to None.
        id (str, optional): Unique identifier for the interaction. Defaults to None.

    Returns:
        str: Response generated by the AI system.
    """
    try:
        if not load_class:
            # Define chat prompt template and output parser
            response = gen_retriever_chain.invoke({
                "input": user_question
            })
        else:
            response = class_retriever_chain.invoke({
                "input": user_question + 'also make sure to share me the relevant link within the context of the question'
            })


    except Exception as e:
        response = {'answer': 'I am not supposed to answer any such queries'}
    finally:
        chat_logger(id=id,
                    prompt=user_question,
                    response=response['answer'],
                    source=source,
                    time_stamp=time_stamp,
                    user=user)
        return response['answer']


if __name__ == '__main__':
    user_question = input('Please say what you wanna know ? ')
    user, source = 'Test', 'TESTINGS'
    response = ask_ai(user_question,user, source,load_class=True)
    print(response)
