import streamlit as st
import requests
import json
import pypdf  # --- NEW: Import the PDF library ---
import io     # --- NEW: Needed to handle the uploaded file in memory ---

# --- NEW: A function to extract text from an uploaded PDF file ---
def extract_text_from_pdf(uploaded_file):
    """Reads an uploaded PDF file and returns its text content."""
    try:
        # pypdf reads the file from memory
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF file: {e}"

# This is the "memory" of your application.
# --- MODIFIED: Added a placeholder for the PDF context ---
MASTER_PROMPT_TEMPLATE = """
You are an expert instructional designer for a higher education institute. Your task is to create a detailed, ready-to-use lesson plan.

First, carefully review the provided 'Reference Document Context'. This is the primary source material. Base your lesson plan heavily on this content.

Then, use the 'Syllabus Extract' to understand the specific topic to focus on.

Finally, adhere strictly to the 'Lesson Plan Skeleton' and 'Customization Settings' to format your output.

---
### **REFERENCE DOCUMENT CONTEXT**
---
{pdf_context}

---
### **LESSON PLAN SKELETON**
---

**Topic:** {topic}
**Course:** {course_name}
**Duration:** 90 Minutes

**1. Learning Objectives:**
   - At the end of this lesson, students will be able to:
   - (Objective 1: Use action verbs like Define, Explain, Analyze, Apply, etc., based on the context)
   - (Objective 2)
   - (Objective 3)

**2. Pre-requisite Knowledge:**
   - (List 1-2 topics students should already know)

**3. Materials & Resources:**
   - Projector & Screen
   - Whiteboard & Markers
   - {references}
   - The provided reference document.

**4. Lesson Activities & Timeline (90 Mins):**
   *   **(0-10 mins) Introduction & Icebreaker:**
       - [Activity based on the teaching style: '{teacher_style}']

   *   **(10-40 mins) Core Concept Delivery:**
       - [Activity based on the teaching style: '{teacher_style}'. This is the main teaching part. Refer to specific concepts from the provided document.]

   *   **(40-60 mins) Interactive Activity / Case Study:**
       - [An activity to reinforce learning. Create a small case study or problem directly from the reference document.]

   *   **(60-80 mins) Group Discussion / Q&A:**
       - [A guided discussion prompt for students related to the document.]

   *   **(80-90 mins) Wrap-up & Summary:**
       - [Recap the key learning objectives and preview the next lesson.]

**5. Assessment & Evaluation:**
   - **Formative:** [How to check for understanding during the class.]
   - **Summative:** [A small take-home question or a hint for the final exam.]

**6. Teacher's Notes:**
   - [Any specific points for the teacher to remember from the document.]

---
### **CUSTOMIZATION & INPUT**
---

*   **Teaching Style:** "{teacher_style}"
*   **Syllabus Extract:** "{syllabus_extract}"

---

Now, generate the complete lesson plan.
"""

# This function sends the final prompt to the Ollama model and gets the response
def generate_lesson_plan(final_prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3:mini",
        "prompt": final_prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return json.loads(response.text)['response']
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}"

# --- Streamlit User Interface ---

st.set_page_config(layout="wide", page_title="Lesson Plan Generator")
st.title("🎓 AI Lesson Plan Generator with PDF Reference")

# --- MODIFIED: Sidebar now includes a file uploader ---
st.sidebar.header("⚙️ Custom Settings")

uploaded_pdf = st.sidebar.file_uploader(
    "Upload Reference PDF", type="pdf"
)

teacher_style_option = st.sidebar.selectbox(
    "Select Teaching Style:",
    ("Interactive & Hands-on (Live Coding)", "Lecture & Discussion-Based", "Case-Study & Problem-Based Learning", "Flipped Classroom Model")
)

references_input = st.sidebar.text_input(
    "Other References (e.g., Book Title):", "N/A"
)

course_name_input = st.sidebar.text_input("Course Name:", "Introduction to Programming")

# Main area for the syllabus extract
st.header("📋 Enter Syllabus Extract")
syllabus_input = st.text_area(
    "Paste the syllabus topic or module description here:",
    "Module 3: Introduction to Python Programming - Variables, Data Types (Integers, Floats, Strings, Booleans), and Basic Operators.",
    height=150
)

# Generate Button
if st.button("✨ Generate Lesson Plan"):
    if not syllabus_input.strip():
        st.error("Please enter a syllabus extract.")
    else:
        # --- MODIFIED: Logic to handle the uploaded PDF ---
        pdf_context_text = "No PDF provided. The plan will be generated based on general knowledge."
        if uploaded_pdf is not None:
            with st.spinner("Reading PDF document..."):
                pdf_context_text = extract_text_from_pdf(uploaded_pdf)
            # Show a snippet of the extracted text to the user for confirmation
            st.sidebar.success("PDF successfully read!")
            with st.sidebar.expander("View extracted text snippet"):
                st.write(pdf_context_text[:500] + "...")
        
        with st.spinner("🧠 The AI is thinking... Please wait."):
            # 1. Assemble the final prompt from the template and user inputs
            final_prompt = MASTER_PROMPT_TEMPLATE.format(
                pdf_context=pdf_context_text, # NEW: Pass the PDF text to the prompt
                topic=syllabus_input.strip().split('-')[0].strip(),
                course_name=course_name_input,
                references=references_input,
                teacher_style=teacher_style_option,
                syllabus_extract=syllabus_input
            )

            # 2. Call the LLM to get the lesson plan
            generated_plan = generate_lesson_plan(final_prompt)

            # 3. Display the result
            st.header("✅ Your Generated Lesson Plan")
            st.markdown(generated_plan)