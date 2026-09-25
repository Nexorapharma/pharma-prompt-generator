import csv
import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Pharma AI Prompt Generator", layout="wide")

st.title("⚡ PharmaDRAFT ")
st.write("Generate engineered AI prompts tailored for pharmaceutical regulatory tasks.")

# Define models globally to prevent any name errors
MODELS_TO_TRY = ["gemini-3.1-flash-lite", "gemini-3-flash-preview"]

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Load database context efficiently
filenames = [
    "ICH_India_Paracetamol_Ibuprofen-1.csv",
    "Pharmacy_Master_Reference_Compendium-All-Syllabus-Resources.csv"
]

document_database = ""

for filename in filenames:
    try:
        with open(filename, mode='r', encoding='latin1') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Get column headers
            if header:
                document_database += f"File: {filename} | Columns: {str(header)}\n"
            
            # Read first 50 rows to keep token size safe and prevent server timeout
            row_count = 0
            for row in reader:
                if row_count < 50:
                    document_database += str(row) + "\n"
                    row_count += 1
                else:
                    break
    except Exception as e:
        st.warning(f"Could not load {filename}: {e}")
# User Inputs for Prompt Generation
col1, col2 = st.columns(2)

with col1:
    task_type = st.selectbox(
        "Select Regulatory Task:",
        [
            "Regulatory Compliance Check Prompt",
            "Quality & Stability Analysis Prompt",
            "Adverse Event & Safety Report Prompt",
            "Drug Comparison & Efficacy Prompt",
            "Custom Regulatory Task",
            "CDSCO Compliance (India)",
            "US FDA Regulatory Submission",
            "EMA / EU Guidelines",
            "ICH Quality & Safety (Q-Series)",
            "Pharmacovigilance & Safety Audit",
            "Clinical Trial Protocol (GCP)",
            "Medical Affairs & Literature Review"
        ]
    )
    target_ai = st.selectbox(
        "Target AI Model:",
        ["ChatGPT (GPT-4o)", "Google Gemini", "Claude 3.5 Sonnet"]
    )

user_goal = st.text_area(
    "Describe what you want the generated prompt to accomplish:",
    placeholder="E.g., Generate a prompt to analyze Paracetamol purity standards according to Indian Pharmacopoeia..."
)

if st.button("🚀 Generate AI Prompt"):
    if user_goal:
        with st.spinner("Engineering your custom prompt..."):
            meta_prompt = f"""
            You are an expert AI Prompt Engineer specializing in Pharmaceutical Regulatory Affairs.
            
            Your job is NOT to answer the user's task directly. 
            Your job is to GENERATE A HIGH-QUALITY, PROFESSIONAL AI PROMPT that a regulatory specialist can copy and paste into an LLM ({target_ai}).

            Use the following CSV database as reference context for background constraints and guidelines:
            {document_database}

            Task Type: {task_type}
            Target AI: {target_ai}
            User Goal: {user_goal}

 Construct a comprehensive, production-ready, highly granular prompt using this exact structure, deeply cross-referencing all loaded pharmaceutical master compendiums, regulatory frameworks (CDSCO, US FDA, EMA, ICH), and syllabus resources:
    1. **Role / Persona** (Define an elite, authoritative expert persona with deep domain and regulatory context)
    2. **Task Definition** (Outline a precise, multi-step execution objective for `{task_type}` matching `{user_goal}`)
    3. **Context & Reference Data** (Embed extracted, detailed parameters, guidelines, and comparative data from the multi-file pharma database `{document_database}`)
    4. **Instructions & Constraints** (Enforce strict regulatory boundaries, validation steps, risk mitigation protocols, and safety guardrails like ICH/NLEM/GCP)
    5. **Expected Output Format** (Mandate a professional delivery layout utilizing structured markdown, executive summaries, compliance matrices, and comparative data tables)
            """

            done = False

            for model_name in MODELS_TO_TRY:
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=meta_prompt,
                            config=types.GenerateContentConfig(
                                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                            )
                        )
                        st.success("Generated Prompt Ready!")
                        st.code(response.text, language="markdown")
                        done = True
                        break
                    except Exception:
                        if attempt < 2:
                            time.sleep(2)
                if done:
                    break

            if not done:
                st.error("Server busy. Please try again.")
    else:
        st.warning("Please describe your goal first.")
