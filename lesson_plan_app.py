import streamlit as st
import requests
import json
import pypdf
import io

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    layout="wide",
    page_title="AI Lesson Plan Generator",
    page_icon="🎓"
)

# --- Function Definitions ---

def extract_text_from_pdf(uploaded_file):
    """Reads an uploaded PDF file and returns its text content."""
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def generate_lesson_plan(final_prompt):
    """Sends the final prompt to the Ollama model and gets the response."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3:mini",
        "prompt": final_prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=120) # Added timeout
        response.raise_for_status()
        return json.loads(response.text)['response']
    except requests.exceptions.Timeout:
        return "Error: The request to Ollama timed out. The model might be taking too long to respond."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}. Is Ollama running?"

# --- Master Prompt Template ---
# This is the core instruction set for the AI model.
MASTER_PROMPT_TEMPLATE = """
You are an expert instructional designer for a higher education institute. Your task is to create a detailed, ready-to-use lesson plan.

First, carefully review the provided 'Reference Document Context'. This is the primary source material. Base your lesson plan heavily on this content, citing specific examples or concepts from it where appropriate.

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


# --- Main Application UI ---

# Header
st.title("🎓 AI Lesson Plan Generator")
st.markdown("An offline tool to create customized lesson plans from syllabus extracts and reference PDFs.")

# Sidebar for all inputs and settings
with st.sidebar:
    st.header("⚙️ 1. Configure Settings")
    
    course_name_input = st.text_input("Course Name:", "Introduction to Programming")
    
    teacher_style_option = st.selectbox(
        "Teaching Style:",
        ("Interactive & Hands-on", "Lecture & Discussion-Based", "Case-Study & Problem-Based", "Flipped Classroom")
    )
    
    references_input = st.text_input(
        "Other References (e.g., Book Title, Website Name):", "N/A"
    )
    st.info("ℹ️ Note: Website links are not actively visited. This is for listing purposes only.")

    st.header("📄 2. Provide Content")
    
    uploaded_pdf = st.file_uploader(
        "Upload Reference PDF (Optional)", type="pdf"
    )
    
    syllabus_input = st.text_area(
        "Syllabus Extract:",
        "Module 3: Introduction to Python Programming - Variables, Data Types (Integers, Floats, Strings, Booleans), and Basic Operators.",
        height=150,
        help="Paste the specific topic or module description from your syllabus here."
    )
    
    # Generate Button
    st.header("🚀 3. Generate")
    generate_button = st.button("✨ Generate Lesson Plan", type="primary", use_container_width=True)


# Main content area
col1, col2 = st.columns(2, gap="large")

with col1:
    st.info("Your generated lesson plan will appear here.")
    # Placeholder for the output
    output_area = st.empty()

if generate_button:
    if not syllabus_input.strip():
        st.error("Please enter a syllabus extract before generating.")
    else:
        with st.spinner("Analyzing your inputs..."):
            pdf_context_text = "No PDF provided. The plan will be generated based on general knowledge."
            if uploaded_pdf is not None:
                st.spinner("Reading PDF document... This may take a moment.")
                pdf_context_text = extract_text_from_pdf(uploaded_pdf)
                if pdf_context_text:
                    with st.sidebar:
                        with st.expander("✅ PDF Read Successfully (Snippet)"):
                            st.write(pdf_context_text[:500] + "...")
            
            # Assemble the final prompt
            final_prompt = MASTER_PROMPT_TEMPLATE.format(
                pdf_context=pdf_context_text,
                topic=syllabus_input.strip().split('-')[0].strip(),
                course_name=course_name_input,
                references=references_input,
                teacher_style=teacher_style_option,
                syllabus_extract=syllabus_input
            )
        
        with st.spinner("🧠 The AI is crafting your lesson plan... Please wait."):
            generated_plan = generate_lesson_plan(final_prompt)
        
        # Display the result in the placeholder
        with output_area.container():
            st.header("✅ Your Generated Lesson Plan")
            st.markdown(generated_plan)

            # Add a download button for the generated plan
            st.download_button(
                label="📥 Download as Text File",
                data=generated_plan,
                file_name=f"lesson_plan_{course_name_input.replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Add a little footer
st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Ollama](https://ollama.com).")