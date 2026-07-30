import os
import json
import torch
from typing import List, Literal
import streamlit as st

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline, ChatHuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig

# ==========================================
# 1. DATA CONTRACTS
# ==========================================
class GapAnalysisOutput(BaseModel):
    status: str = Field(description="Either 'complete' or 'incomplete'")
    inferred_role: str = Field(description="The expert role that should execute this task (e.g., 'Senior Python Engineer', 'Expert Baking Instructor'). Infer this from the user's request.")
    clarifying_questions: List[str] = Field(description="Specific, contextual questions to ask the user to gather missing information. Ask about domain-specific details, NOT about prompt structure.")

class OptimizedPromptOutput(BaseModel):
    framework_used: str = Field(description="The specific prompt engineering framework or playbook selected from the reference material.")
    role: str
    context: str
    task: str
    constraints: List[str]
    output_format: str

# ==========================================
# 2. INITIALIZATION & RAG INGESTION
# ==========================================
@st.cache_resource
def initialize_system():
    st.write("Loading Qwen2.5-7B-Instruct model... (This takes ~60-90 seconds on first run)")
    model_id = "Qwen/Qwen2.5-7B-Instruct"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_config,
    )

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        temperature=0.0,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
        return_full_text=False
    )

    llm_pipeline = HuggingFacePipeline(pipeline=pipe)
    chat_model = ChatHuggingFace(llm=llm_pipeline)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")])

    # Read from the external file instead of hardcoding
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.md")
    if not os.path.exists(kb_path):
        raise FileNotFoundError("knowledge_base.md not found in the project directory.")
        
    with open(kb_path, "r", encoding="utf-8") as f:
        knowledge_base_content = f.read()

    documents = splitter.split_text(knowledge_base_content)
    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    st.success("Model and RAG loaded successfully.")
    return chat_model, retriever

# ==========================================
# 3. PROMPTS & PARSERS 
# ==========================================
gap_parser = JsonOutputParser(pydantic_object=GapAnalysisOutput)
architect_parser = JsonOutputParser(pydantic_object=OptimizedPromptOutput)
refiner_parser = JsonOutputParser(pydantic_object=OptimizedPromptOutput)


gap_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Prompt Analyst. Your job is to analyze vague user requests and determine what specific information is missing.

CRITICAL RULES:
1. **Auto-infer the role**: Based on the request, determine what EXPERT would execute this task.
   - "teach me to bake" → "Expert Baking Instructor"
   - "write code" → "Senior Software Engineer"
   - "help me market" → "Marketing Strategist"

2. **Ask specific, contextual questions**: Ask about domain-specific details, NOT about prompt structure.
   - For baking: "What type of cake?", "What's your skill level?", "Any dietary restrictions?"
   - For coding: "What should the script do?", "What programming language?", "What libraries can you use?"
   - For marketing: "Who is your target audience?", "What product/service?", "What platform?"

3. **A request is "complete" only if**: It has enough specific details for an expert to execute immediately without asking follow-up questions.

4. **Output ONLY valid JSON**.

{format_instructions}"""),
    ("user", "Analyze this request: {user_input}")
]).partial(format_instructions=gap_parser.get_format_instructions())

architect_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the Architect. Your SOLE purpose is to create structured prompts using ONLY the frameworks and playbooks provided in the Reference material.

CRITICAL RULES:
1. You MUST select a framework/playbook from the Reference material. DO NOT invent new frameworks.
2. The 'role' field must be the EXPERT who will EXECUTE the task (use the inferred role from gap analysis).
3. DO NOT hallucinate or make up information. Use ONLY what's in the Reference.
4. If the Reference contains "CRISPE", "CREATE", or domain playbooks, you MUST use one of those.
5. State the EXACT framework name in 'framework_used' field.
6. Output ONLY valid JSON. No explanations, no markdown.

{format_instructions}"""),
    ("user", "Request: {user_input}\nUser's Answers to Clarifying Questions: {user_clarifications}\nReference: {rag_context}")
]).partial(format_instructions=architect_parser.get_format_instructions())

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict Prompt Engineering Professor. Evaluate the draft prompt. Assign a score from 1 to 10. Provide specific, actionable feedback. Format exactly as:\nScore: [X]/10\nFeedback: [Your critique]"),
    ("user", "Draft: {draft_prompt}")
])

refiner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the Refiner. Rewrite the draft prompt to address the feedback. Output ONLY a valid JSON object. CRITICAL: The 'role' field must be a professional EXPERT persona. Maintain the 'framework_used' from the draft.\n\n{format_instructions}"),
    ("user", "Draft: {draft_prompt}\nFeedback: {critic_feedback}")
]).partial(format_instructions=refiner_parser.get_format_instructions())

# ==========================================
# 4. STREAMLIT UI & EXECUTION PIPELINE
# ==========================================
st.set_page_config(page_title="MetaPrompt Architect", page_icon="🧠", layout="wide")

st.title("🧠 MetaPrompt Architect")
st.markdown("Transform vague requests into highly structured, professional AI prompts using a **Self-Reflective RAG Chain**.")

# Initialize session state
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = "input"
if 'gap_result' not in st.session_state:
    st.session_state.gap_result = None
if 'inferred_role' not in st.session_state:
    st.session_state.inferred_role = ""
if 'clarifying_questions' not in st.session_state:
    st.session_state.clarifying_questions = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = ""

# Sidebar
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    1. Enter a vague request
    2. AI analyzes and asks specific questions
    3. Answer the questions
    4. Get a professionally optimized prompt
    """)
    if st.button("🔄 Reset Everything"):
        st.session_state.workflow_step = "input"
        st.session_state.gap_result = None
        st.session_state.inferred_role = ""
        st.session_state.clarifying_questions = []
        st.session_state.user_answers = ""
        st.rerun()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Input")
    user_input = st.text_area("Vague User Request",
                             value=st.session_state.user_input if 'user_input' in st.session_state else "",
                             height=100,
                             placeholder="e.g., Teach me to bake a cake",
                             key="input_text",
                             disabled=(st.session_state.workflow_step in ["clarify", "done"]))

    # STEP 1: Analyze button
    if st.session_state.workflow_step == "input":
        if st.button("🔍 Analyze Request", type="primary", use_container_width=True):
            if not user_input.strip():
                st.warning("Please enter a vague request first.")
            else:
                st.session_state.user_input = user_input

                with st.spinner("Analyzing your request..."):
                    chat_model, retriever = initialize_system()

                    # Run Gap Analysis
                    gap_chain = gap_prompt | chat_model | gap_parser

                    try:
                        gap_result = gap_chain.invoke({"user_input": user_input})
                        st.session_state.gap_result = gap_result

                        if gap_result:
                            st.session_state.inferred_role = gap_result.get('inferred_role', 'Expert')
                            st.session_state.clarifying_questions = gap_result.get('clarifying_questions', [])
                            status = gap_result.get('status', 'incomplete')

                            if status == "incomplete" and st.session_state.clarifying_questions:
                                # Need clarifications
                                st.session_state.workflow_step = "clarify"
                                st.rerun()
                            else:
                                # Complete enough to proceed
                                st.session_state.user_answers = "Request was complete enough to proceed."
                                st.session_state.workflow_step = "done"
                                st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

    # STEP 2: Show clarifying questions
    elif st.session_state.workflow_step == "clarify":
        st.success(f"✅ **Inferred Role:** {st.session_state.inferred_role}")
        st.markdown("---")
        st.info(" **I need a bit more information:**")

        # Display each clarifying question as a bullet point
        questions_text = "\n".join([f"- {q}" for q in st.session_state.clarifying_questions])
        st.markdown(questions_text)

        user_answers = st.text_area("📝 Your Answers",
                                   value=st.session_state.user_answers,
                                   height=150,
                                   placeholder="Please answer the questions above. You can answer briefly or in detail.",
                                   key="answers_text")

        if st.button("✅ Generate Final Prompt", type="primary", use_container_width=True):
            if not user_answers.strip():
                st.warning("Please provide answers to the questions above.")
            else:
                st.session_state.user_answers = user_answers
                st.session_state.workflow_step = "done"
                st.rerun()

    # STEP 3: Done
    elif st.session_state.workflow_step == "done":
        st.success("✅ Prompt generated! See results on the right.")
        if st.button("🔄 Start New Request", use_container_width=True):
            st.session_state.workflow_step = "input"
            st.session_state.gap_result = None
            st.session_state.inferred_role = ""
            st.session_state.clarifying_questions = []
            st.session_state.user_answers = ""
            st.session_state.user_input = ""
            st.rerun()

# ==========================================
# RIGHT COLUMN: RESULTS
# ==========================================
with col2:
    if st.session_state.workflow_step == "done":
        with st.spinner("Generating your optimized prompt..."):
            chat_model, retriever = initialize_system()

            user_input = st.session_state.user_input
            user_answers = st.session_state.user_answers

            st.subheader("Results")

            # Show Gap Analysis
            with st.expander("🔍 Phase 1: Gap Analysis", expanded=True):
                st.write(f"**Inferred Role:** {st.session_state.inferred_role}")
                st.write(f"**Clarifying Questions Asked:**")
                for q in st.session_state.clarifying_questions:
                    st.write(f"- {q}")
                st.write(f"**Your Answers:** {user_answers}")

            # RAG Retrieval
            rag_docs = retriever.invoke(user_input)
            rag_context = "\n\n".join([doc.page_content for doc in rag_docs])

            with st.expander("📚 RAG Retrieved Context", expanded=False):
                st.text(rag_context)

            # Phase 2: Architect
            arch_chain = architect_prompt | chat_model | architect_parser
            draft_str = "Architect failed to generate."
            try:
                draft_obj = arch_chain.invoke({
                    "user_input": user_input,
                    "user_clarifications": user_answers,
                    "rag_context": rag_context
                })
                draft_str = json.dumps(draft_obj, indent=2)
            except Exception as e:
                draft_str = f"Error: {e}"

            with st.expander("️ Phase 2: Architect Draft", expanded=False):
                st.code(draft_str, language="json")

            # Phase 3: Critic
            critic_chain = critic_prompt | chat_model | StrOutputParser()
            critic_feedback = "Score: 8/10\nFeedback: Good structure, but add more specific constraints."
            try:
                feedback = critic_chain.invoke({"draft_prompt": draft_str})
                if len(feedback.strip()) > 10:
                    critic_feedback = feedback
            except Exception:
                pass

            with st.expander("👨‍🏫 Phase 3: Critic Feedback", expanded=False):
                st.text(critic_feedback)

            # Phase 4: Refiner
            refiner_chain = refiner_prompt | chat_model | refiner_parser
            final_str = "Refiner failed to generate."
            try:
                final_obj = refiner_chain.invoke({
                    "draft_prompt": draft_str,
                    "critic_feedback": critic_feedback
                })
                final_str = json.dumps(final_obj, indent=2)
            except Exception as e:
                final_str = f"Error: {e}"

            st.markdown("### ✅ Final Optimized Prompt")
            st.code(final_str, language="json")
