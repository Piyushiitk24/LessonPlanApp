import streamlit as st
import requests
import json
import pypdf
import io
from fpdf import FPDF
import os

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Lesson Plan Generator",
    page_icon="⚓"
)

# --- Function Definitions ---

def extract_text_from_pdf(uploaded_file):
    # (This function remains the same)
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

# --- NEW: Function to convert Markdown to PDF ---
class PDF(FPDF):
    def __init__(self, institute_name="NIETT", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.institute_name = institute_name
        # Add a Unicode font (ensure the .ttf file is in your project directory)
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        self.add_font("DejaVu", "", font_path, uni=True)
        self.set_font("DejaVu", size=10)

    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, self.institute_name, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def markdown_to_pdf(markdown_text, subject, institute_name="NIETT"):
    pdf = PDF(institute_name=institute_name)
    pdf.add_page()
    pdf.set_font("DejaVu", size=10)
    
    # Use multi_cell for markdown rendering
    pdf.multi_cell(0, 5, markdown_text)
    
    # Return the PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def generate_lesson_plan(final_prompt):
    # (This function remains the same, but we can increase the timeout)
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3:mini",
        "prompt": final_prompt,
        "stream": False
    }
    try:
        # Increased timeout for a very long and complex generation task
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return json.loads(response.text)['response']
    except requests.exceptions.Timeout:
        return "Error: The request to Ollama timed out. The model is taking too long. Try a shorter syllabus extract."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}. Is Ollama running?"

# --- MASTER PROMPT TEMPLATE (Paste the huge new template from Step 2 here) ---
MASTER_PROMPT_TEMPLATE = """
You are an expert instructional designer and master trainer for a military educational institution. Your task is to create a hyper-detailed, all-inclusive lesson plan for an instructor who may be teaching this topic for the first time. The lesson plan must strictly follow the provided format and be filled with concrete, actionable content.

**CRITICAL INSTRUCTIONS:**
1.  **Adhere to the Format:** Use Markdown tables and headers exactly as specified in the template below. Do not deviate.
2.  **Be Specific:** Do not provide generic guidance. Write the exact questions, examples, and talking points the instructor should use.
3.  **Hybrid Knowledge:** If 'Reference Document Context' is provided, base your content primarily on it, enriching it with your own general knowledge. If it's not provided, rely solely on your own expertise about the syllabus topic.
4.  **Fill Every Section:** Provide plausible and detailed content for all parts of the lesson plan, including the 'Personal Experience of Instructor' section, by anticipating common scenarios.

---
### **LESSON PLAN TEMPLATE**
---

# LESSON PLAN

**SUBJECT:** {subject}
**CLASS:** {class_name}
**LESSON PLAN No:** {lesson_no}
**TOTAL NO. OF LESSON PLAN:** {total_lessons}
**TIME:** {duration} Min

---

### **PART A**

| 1. TOPIC | {topic} |
| :--- | :--- |
| **2. TOTAL NUMBER OF SESSIONS FOR THIS TOPIC** | 01 |
| **3. SEQUENCE OF THIS SESSION** | 01/01 |

**4. SYLLABUS EXTRACT**
> {syllabus_extract}

**5. SPECIFIC OBJECTIVES**
*At the end of this lesson, the trainees will be able to:*
(a) [Generate the first specific, measurable learning objective based on the syllabus]
(b) [Generate the second specific, measurable learning objective]
(c) [Generate the third specific, measurable learning objective]
(d) [Continue for all key concepts in the syllabus extract]
(e) ...
(f) ...

**6. LIST OF TEACHING AIDS**
| No. | Description | Remarks |
| :--- | :--- | :--- |
| (a) | **BR/Text Book** | *Based on your knowledge, suggest 1-2 highly relevant, standard textbooks for this topic. If a PDF was provided, list it as the primary reference.* |
| (b) | **CBT/PPT** | *Suggest key themes and slide titles for a PowerPoint presentation (e.g., "Slides 1-3: Introduction to Motivation", "Slides 4-11: Maslow's Hierarchy Explained").* |

**7. PRACTICAL IN LAB/EQUIPMENT ROOMS**
> Nil

**8. EXISTING KNOWLEDGE OF THE CLASS**
> The trainees have a basic understanding of [mention a foundational concept], but are likely unaware of the specific models and practical application techniques covered in this lesson, such as [mention a key term from the syllabus].

**9. CHECKING OF PREVIOUS KNOWLEDGE / INTRODUCTION (05 Min)**
*Instructor to ask the following questions to bridge the previous lesson and introduce the topic:*
> (a) "Can anyone tell me what we discussed last time regarding [previous related topic]?"
> (b) "In your own words, what does the term '[key syllabus term]' mean to you?"
> (c) "Why do you think understanding [topic] is important in our field?"

---

### **PART B: DEVELOPMENT OF LESSON PLAN**

| SCHEME OF TEACHING | METHOD | TRG AIDS | TIME (Min) |
| :--- | :--- | :--- | :--- |
| **(a) Introduction & Linking with Previous Knowledge** <br> *Instructor states the topic and its importance. Briefly explains the learning objectives for the session.* <br> **Talking Point:** "Good morning. Today, we're going to delve into {topic}, which is crucial for [state importance]. By the end of this 80-minute session, you will be able to..." | L/Ds | PPT Slide 1-2 | 5 |
| **(b) [First Key Concept from Syllabus]** <br> *Instructor defines the concept and provides a real-world example.* <br> **Example:** "[Provide a detailed, relatable example for this concept. For instance, if teaching 'Arousal Function', explain it with a story about an upcoming inspection.]" | L/Ds | PPT Slide 3-5 | 15 |
| **(c) [Second Key Concept from Syllabus]** <br> *Instructor explains the theory/model and uses an analogy.* <br> **Analogy:** "[Create a simple analogy. If discussing Maslow's Hierarchy, compare it to building a house from the foundation up.]" | L/Ds | PPT Slide 6-9 | 15 |
| **(d) Interactive Activity / Case Study** <br> *Instructor presents a short case study and asks trainees to discuss it in pairs.* <br> **Case Study:** "[Write a short, challenging scenario related to the topic. E.g., 'A junior rating is consistently late and seems disengaged. Using the principles we've just discussed, what are the first two steps you would take as their supervisor?']" | Pr/Ds | Whiteboard | 20 |
| **(e) [Third Key Concept from Syllabus]** <br> *Instructor explains the concept and its practical application.* <br> **Application:** "So, how do we use this on the job? For the [concept], you would [describe a specific action or process]." | L/Ds | PPT Slide 10-12 | 15 |
| **(f) Summary and Evaluation** <br> *Instructor summarizes the key takeaways, recapping the specific objectives.* <br> **Recap Questions:** "To quickly recap, can someone define [key term 1]? What are the stages of [key model 2]?" | L | PPT Slide 13 | 5 |
| **(g) Home Assignment and Follow-up** <br> *Instructor gives a thought-provoking question for the trainees to consider.* <br> **Assignment:** "[Pose a practical, open-ended question. E.g., 'Observe one instance of high motivation and one of low motivation in your environment before our next session. Be prepared to discuss the contributing factors.']" | - | - | 5 |

---

### **PART C: PREPARATION FOR TOMORROW (PFT)**

| Ser | Syllabus for PFT | References | Related Lesson Plan Number |
| :--- | :--- | :--- | :--- |
| 1 | [Generate a logical next topic that would follow the current lesson] | Handout / Chapter X | {next_lesson_no} |

---

### **PART D: PERSONAL EXPERIENCE OF INSTRUCTOR**

| Ser | Item | Remarks |
| :--- | :--- | :--- |
| 1 | **Additional resources/Techniques used** | *Anticipate and suggest a useful technique. E.g., "Used the 'Think-Pair-Share' method during the case study which increased engagement."* |
| 2 | **Doubts/Intelligent questions raised by the trainees** | *Anticipate a likely, intelligent question from a trainee. E.g., "A trainee asked how to apply these motivational theories when dealing with passive-aggressive behavior."* |
| 3 | **Difficulties faced by Instructor** | *Anticipate a common teaching challenge. E.g., "Some trainees found it difficult to differentiate between 'expectancy' and 'incentive' functions initially. Required re-explanation with a different example."* |
| 4 | **Suggestions for improvement** | *Suggest a potential improvement for the next time. E.g., "A short, 2-minute video clip showcasing a real-life leadership scenario could be very effective."* |

---
### **INPUT FOR GENERATION**
---

*   **Reference Document Context:** "{pdf_context}"
*   **Syllabus Extract:** "{syllabus_extract}"

---

Now, generate the complete lesson plan based on all the provided information.
"""

# --- Main Application UI ---

st.title("⚓ NIETT AI Lesson Plan Generator")
st.markdown("This tool generates a hyper-detailed lesson plan in the official NIETT format.")

# Use session state to hold the generated plan
if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ""

# Sidebar for all inputs and settings
with st.sidebar:
    st.header("⚙️ 1. Lesson Details")
    
    institute_input = st.text_input("Institute Name:", "NIETT")  # <-- NEW FIELD
    
    subject_input = st.text_input("Subject:", "Training Technology")
    class_input = st.text_input("Class:", "TT(O)")
    
    col1, col2 = st.columns(2)
    with col1:
        lesson_no_input = st.number_input("Lesson Plan No:", min_value=1, value=11)
    with col2:
        total_lessons_input = st.number_input("Total Lessons:", min_value=1, value=25)
    
    duration_input = st.number_input("Duration (Mins):", min_value=30, value=80, step=10)

    st.header("📄 2. Lesson Content")
    
    syllabus_input = st.text_area(
        "Syllabus Extract:",
        "Motivation, Motivational functions of an instructor. List of activities which contribute towards motivation in the trainees, Instructor's motivation, Motivational grid.",
        height=125,
        help="Paste the specific topic or module description from your syllabus here."
    )
    
    uploaded_pdf = st.file_uploader(
        "Upload Reference PDF (Optional)", type="pdf"
    )
    
    st.header("🚀 3. Generate")
    generate_button = st.button("✨ Generate Lesson Plan", type="primary", use_container_width=True)

# Main content area for displaying the output
st.header("Generated Lesson Plan")
output_area = st.empty()

if generate_button:
    if not syllabus_input.strip():
        st.error("Syllabus Extract cannot be empty.")
    else:
        with st.spinner("Reading inputs and preparing the AI prompt..."):
            pdf_context_text = "No specific reference document provided. Relying on general knowledge."
            if uploaded_pdf is not None:
                pdf_context_text = extract_text_from_pdf(uploaded_pdf)
                if pdf_context_text:
                    with st.sidebar:
                        st.success("✅ PDF Read Successfully")
            
            # Assemble the final prompt
            final_prompt = MASTER_PROMPT_TEMPLATE.format(
                subject=subject_input,
                class_name=class_input,
                lesson_no=lesson_no_input,
                total_lessons=total_lessons_input,
                duration=duration_input,
                topic=syllabus_input.strip().split(',')[0], # Use first part of syllabus as topic
                syllabus_extract=syllabus_input,
                next_lesson_no=lesson_no_input + 1,
                pdf_context=pdf_context_text
            )
        
        with st.spinner("🧠 The AI is crafting your detailed lesson plan. This may take a few minutes..."):
            st.session_state.generated_plan = generate_lesson_plan(final_prompt)
        
        if "Error:" in st.session_state.generated_plan:
            st.error(st.session_state.generated_plan)
        else:
            st.success("Lesson Plan Generated Successfully!")

# Display the generated plan from session state
if st.session_state.generated_plan:
    with output_area.container():
        st.markdown(st.session_state.generated_plan)
        
        # --- NEW: PDF Download Button ---
        try:
            pdf_bytes = markdown_to_pdf(
                st.session_state.generated_plan,
                subject_input,
                institute_name=institute_input  # <-- Pass user input here
            )
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_bytes,
                file_name=f"Lesson_Plan_{lesson_no_input}_{subject_input.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate PDF. Error: {e}")


st.markdown("---")
st.markdown("Built for NIETT | Powered by [Ollama](https://ollama.com) & [Streamlit](https://streamlit.io)")