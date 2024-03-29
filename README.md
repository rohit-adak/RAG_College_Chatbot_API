### **Project Title: RAG College Chatbot API** 🎓🤖

#### **Overview**

Empower your college community with an intelligent chatbot driven by state-of-the-art Retrieval-Augmented Generation (RAG) technology. This API harnesses the power of a provided knowledge base file and integrates seamlessly with the Gemini API, offering enhanced responses tailored to the college domain. Key features include:

- **Contextual Question Answering:** The chatbot comprehensively addresses diverse college-related queries by leveraging information directly from the supplied text file.
- **Gemini Integration:** Augmenting its capabilities, the chatbot provides nuanced and detailed responses, enriching user interactions.
- **API-Driven:** The core functionality is exposed through a well-defined API, facilitating effortless integration into various college applications.

#### **Getting Started** 🚀

1. **Prerequisites:**
   - Python (version >= 3.12)
   - Obtain a Gemini API key from [Google GenAI](https://ai.google.dev/).
   - Acquire a META API key from [Facebook for Developers](https://developers.facebook.com/tools/explorer).
   - Hosted Database details including Host, Username, Password, and Database Name. You can use services like [RENDER](https://render.com/) to create and host databases for free.

2. **Installation:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   - Customize or replace the `.txt` file inside the `/assets/` folder.
   - Create a `.env` file to store configuration variables.

   **Environment Variables:**
    ```
    GOOGLE_API_KEY=<your_google_api_key>
    META_API_KEY=<your_meta_api_key>
    DB_HOSTNAME=<your_database_hostname> 
    DB_USERNAME=<your_database_username>
    DB_PASSWORD=<your_database_password>
    DB_NAME=<your_database_name>
    API_ACCESS_TOKEN=<random_string_for_api_access_token>
    API_SECRET_KEY=<random_string_for_api_secret_key>
    ```

4. **Running the API**
   ```bash
   python app.py 
   ```

#### **API Usage** 🤝

- **Endpoint:** `/chat`
- **Method:** POST
- **Request Body (JSON):**
   ```json
   {
      "queries": [
        {
          "id": "d0ea774a-5d10-4a04-80f9-e07cd6b28ec3",
          "prompt": "How can you help me?",
          "user": "Test user"
        }
      ],
      "model": "bscit_g_query",
      "access_token": "<Your_access_token>", 
      "secret_key": "<Your_secret_key>"
   }
   ```
- **Response Body (JSON):**
   ```json
   {
      "response data": [
        {
          "id": "d0ea774a-5d10-4a04-80f9-e07cd6b28ec3",
          "response": "I am a bot, an Artificial Intelligence designed to assist students. \n\n**You can also ask for:** \n - What are the subjects available in Semester 2?\n - Where can I find the syllabus for Semester 2?\n - Can you provide me with notes and study materials for Semester 2?"
        }
      ]
   }
   ```

#### **GUI For the Application** 💻

A Serate project for GUI of the same application via this api is available at 
[GUI FOR THE APPLICATION (ver. Streamlit)](https://github.com/rohit-adak/rohit-adak-RAG_College_Chatbot_GUI)

*NOTE: Installation of this project is necessary*

#### **Contributing** 🌟

We welcome contributions to enhance this project! Follow these guidelines:
1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request with detailed explanations.

#### **Contact** 📞

For questions or support, feel free to reach out:
- [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/rohit-adak-20001426a/)
- [![Instagram](https://img.shields.io/badge/Instagram-Follow-orange?style=flat-square&logo=instagram)](https://www.instagram.com/adak_rohit_/)
