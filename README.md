# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026

> 🏆 This repository is my official submission for the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        |  Zeina Wael Mahmoud                                  |
| Project Name     |  MetaPrompt-Architect                                    |
| GitHub Username  |  ZeinaAbdelshafy                                    |
| Challenge Batch  | June–July 2026                       |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

# 📖 Project Overview

MetaPrompt Architect is an AI-powered tool designed to transform vague user requests into structured, professional AI prompts. It utilizes a Self-Reflective Retrieval-Augmented Generation (RAG) chain to analyze user intent, identify missing context, and iteratively refine the output. Instead of forcing users to understand prompt engineering, the system acts as an intelligent intermediary that asks specific clarifying questions and applies established frameworks to generate the final prompt.

---

# ✨ Features

*Intelligent Gap Analysis: Automatically detects missing context in a user's request and generates specific, domain-relevant clarifying questions.
*Self-Reflective Pipeline: Employs a multi-step generation process featuring an Architect, a Critic, and a Refiner to iteratively improve prompt quality.
*RAG Grounding: Retrieves relevant prompt engineering frameworks (such as CRISPE and CREATE) and domain playbooks to prevent hallucinations and ensure structural correctness.


---

# 🛠️ Technologies Used

*Python 3.10+
*LangChain and LangChain Community
*Hugging Face Transformers and Accelerate
*Qwen2.5-7B-Instruct (4-bit quantized via BitsAndBytes)
*FAISS and Sentence-Transformers for vector storage and retrieval
*Streamlit for the web interface
*Pyngrok for secure tunneling and deployment
*Pydantic for strict data validation and JSON schema enforcement

---

# ⚙️ Installation
Guide for running in Google Colab.
1. upload all files in Colab
2. Install dependencies:
   '''python
   !pip install -r requirements.txt
   ''' 
3.Create a .env file with your ngrok token:
'''python
with open(".env", "w") as f:
   f.write("NGROK_AUTH_TOKEN=your_ngrok_token_here")
'''
5. Start the Streamlit server in the background:
'''python
    !streamlit run app.py --server.port 8501 --server.headless true &
'''
7. create ngrok tunnel in new cell
'''python
import os, time
from pyngrok import ngrok
from dotenv import load_dotenv
   
load_dotenv()
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
time.sleep(5)
   
public_url = ngrok.connect(8501)
print(f"App is live at: {public_url}")'''

---

# 🚀 Usage

1. Run the Streamlit application in headless mode: streamlit run app.py --server.port 8501 --server.headless true
2. In a separate terminal, start the ngrok tunnel to expose the local server: ngrok http 8501
3. Open the generated ngrok URL in your web browser.
4. Enter a vague request into the input field. If the system identifies missing context, it will prompt you with specific questions. Answer them to generate the final optimized prompt.

---

# 📸 Demo

demo video link: https://drive.google.com/file/d/1_ayQG6kdFoGRLC-xHl-TTaXZKIb167K1/view?usp=sharing 

---

# 📈 Results

The MetaPrompt Architect successfully delivers a fully functional, deployed web application that bridges the gap between novice user intent and expert-level prompt engineering. By implementing a self-reflective RAG chain, the system reliably identifies missing context and generates domain-specific clarifying questions rather than relying on generic defaults.

---

# 🔮 Future Improvements

*Integrate larger, more capable models via API to further reduce JSON parsing errors and improve reasoning.
*Expand the RAG knowledge base to include more specialized domain playbooks and industry-specific frameworks.
*Add a backend database to allow users to save, version, and share their generated prompts.

---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
