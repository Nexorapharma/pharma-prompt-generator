import csv
import os
from google import genai
import requests
import streamlit as st
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(page_title="PharmaDRAFT", page_icon="⚡", layout="centered")


# Helper function to load Lottie animations from a URL
def load_lottie_url(url):
  try:
    r = requests.get(url)
    if r.status_code != 200:
      return None
    return r.json()
  except Exception:
    return None


# Load a medical/pharmaceutical vector animation
lottie_pharma = load_lottie_url(
    "https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json"
)

st.markdown("""
# ⚡ PharmaDRAFT
Generate engineered AI prompts tailored for pharmaceutical regulatory tasks.
""")

# Display the animation right under the title (if it loads successfully)
if lottie_pharma:
  st_lottie(lottie_pharma, height=180, key="pharma_header_anim")

# Initialize Gemini Client (expects GEMINI_API_KEY in Streamlit Secrets or environment variables)
try:
  client = genai.Client()
except Exception as e:
  st.error(
      f"Failed to initialize GenAI Client. Check your API Key in secrets. {e}"
  )

# --- AUDIENCE SELECTION DROPDOWNS ---
audience_category = st.selectbox(
    "Select Target Audience / Category:",
    ["People", "UG Student", "Industry / PG / PhD"]
)

sub_option = ""
if audience_category == "People":
    sub_option = st.selectbox(
        "Select Exploration Level:",
        ["Want to explore", "Detailed info"]
    )
elif audience_category == "UG Student":
    sub_option = st.selectbox(
        "Select Specialization:",
        [
            "Pharmaceutics",
            "Pharmaceutical Chemistry",
            "Pharmacology",
            "Regulatory Affairs",
            "Pharmacognosy"
        ]
    )

# --- DYNAMIC DATABASE MAPPING BASED ON YOUR EXACT FILE NAMES ---
filenames = []

if audience_category == "Industry / PG / PhD":
    filenames = [
        "ICH_India_Paracetamol_Ibuprofen-1.csv",
        "Pharmacy_Master_Reference_Compendium-All-Syllabus-Resources.csv",
    ]
elif audience_category == "People":
    filenames = ["pharma_and_youtube_references.csv"]
elif audience_category == "UG Student":
    if sub_option == "Pharmaceutics":
        filenames = ["ug_pharmaceutics_database.csv"]
    elif sub_option == "Pharmaceutical Chemistry":
        filenames = ["ug_pharmaceutical_chemistry_database.csv"]
    elif sub_option == "Pharmacology":
        filenames = ["ug_pharmacology_database.csv"]
    elif sub_option == "Regulatory Affairs":
        filenames = ["ug_regulatory_affairs_database.csv"]
    elif sub_option == "Pharmacognosy":
        filenames = ["ug_pharmacognosy_database.csv"]

# Load selected database context efficiently with latin1 encoding and row-capping
document_database = ""

for filename in filenames:
  try:
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="latin1") as file:
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
    else:
        document_database += f"Database file '{filename}' pending upload. Operating in standard mode.\n"
  except Exception as e:
    st.warning(f"Could not load {filename}: {e}")

# User Inputs Form
task_option = st.selectbox(
    "Select Regulatory/Academic Task:",
    [
        "ICH Quality & Safety (Q-Series)",
        "CDSCO Compliance (India)",
        "US FDA Regulatory Submission",
        "Clinical Trial Protocol (GCP)",
        "Regulatory Compliance Check Prompt",
    ],
)

model_option = st.selectbox(
    "Target AI Model:", ["Google Gemini", "ChatGPT (GPT-4o)", "Claude 3.5 Sonnet"]
)

user_goal = st.text_area(
    "Describe what you want the generated prompt to accomplish:",
    placeholder=(
        "E.g., Generate a prompt to analyze Paracetamol purity standards"
        " according to Indian Pharmacopoeia..."
    ),
)

if st.button("🚀 Generate AI Prompt"):
  if not user_goal.strip():
    st.warning(
        "Please enter a description of what you want the prompt to accomplish."
    )
  else:
    with st.spinner(
        "Engineering high-rigor regulatory prompt from selected compendiums..."
    ):
      try:
        meta_prompt = f"""
You are an expert pharmaceutical regulatory affairs and academic prompt engineer. 
Your task is to engineer a comprehensive, production-ready AI prompt for a target model ({model_option}).

Target Audience Context: {audience_category} -> {sub_option if sub_option else 'Advanced Professional'}
Selected Regulatory/Academic Task: {task_option}
User Objective: {user_goal}

Reference Database Sample & Structure:
{document_database}

Instructions for the generated prompt:
1. Force the target AI model to act as a senior pharmaceutical consultant tailored to the selected audience level.
2. Require it to cross-reference appropriate standards including CDSCO, FDA, EMA, and ICH guidelines where applicable.
3. Structure the output prompt with clear constraints, required outputs, compliance checkpoints, and safety guardrails.
4. Output ONLY the final engineered prompt ready to be copied and used.
"""

        # Call Gemini model using the stable active model identifier
        response = client.models.generate_content(
            model="gemini-3.8-flash", contents=meta_prompt
        )

        st.success("Prompt Generated Successfully!")

        # Display output in a clean text area
        st.text_area(
            "Your Engineered Prompt:", 
            value=response.text, 
            height=300
        )

        # Standalone Custom Copy Button placed strictly below on the left side
        safe_text = response.text.replace("`", "\\`").replace('"', '\\"')
        components.html(f"""
            <div style="display: flex; justify-content: flex-start; margin-top: 5px;">
                <button onclick="navigator.clipboard.writeText(`{safe_text}`); alert('Prompt copied to clipboard!');" style="background-color: #FF4B4B; color: white; padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    📋 Copy Prompt
                </button>
            </div>
        """, height=60)

      except Exception as e:
        st.error(f"Server busy. Please try again. Error details: {e}")
