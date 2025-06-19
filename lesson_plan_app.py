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
    page_title="AI Lesson Plan Generator",
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

# --- MODIFIED: PDF class now accepts institute_name ---
class PDF(FPDF):
    # NEW: __init__ method to store the institute name
    def __init__(self, institute_name):
        super().__init__()
        self.institute_name = institute_name

    def header(self):
        self.set_font('DejaVu', 'B', 12)
        # MODIFIED: Use the stored institute_name variable instead of a hardcoded string
        self.cell(0, 10, self.institute_name, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- MODIFIED: markdown_to_pdf function now requires institute_name ---
def markdown_to_pdf(markdown_text, subject, institute_name):
    # MODIFIED: Pass the institute_name when creating the PDF object
    pdf = PDF(institute_name=institute_name)
    
    font_path = 'DejaVuSans.ttf'
    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_path, uni=True)
        pdf.add_font('DejaVu', 'I', font_path, uni=True)
        pdf.set_font('DejaVu', '', 10)
    else:
        st.warning("DejaVuSans.ttf not found. PDF may have character issues. Using standard font.")
        pdf.set_font("Helvetica", size=10)

    pdf.add_page()
    
    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            pdf.set_font('DejaVu', 'B', 16)
            pdf.multi_cell(0, 10, line[2:], ln=1)
            pdf.set_font('DejaVu', '', 10)
        elif line.startswith('### '):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.multi_cell(0, 8, line[4:], ln=1)
            pdf.set_font('DejaVu', '', 10)
        else:
            pdf.multi_cell(0, 5, line, ln=1)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_lesson_plan(final_prompt):
    # (This function remains the same)
    url = "http://localhost:11434/api/generate"
    payload = { "model": "phi3:mini", "prompt": final_prompt, "stream": False }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return json.loads(response.text)['response']
    except requests.exceptions.Timeout:
        return "Error: The request to Ollama timed out."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}."

# --- MASTER PROMPT TEMPLATE (This remains the same as the last version) ---
# --- FINAL, CORRECTED MASTER PROMPT TEMPLATE ---
MASTER_PROMPT_TEMPLATE = """
You are an expert instructional designer and master trainer for a military educational institution. Your task is to create a hyper-detailed, all-inclusive lesson plan for an instructor who may be teaching this topic for the first time.

**CRITICAL INSTRUCTIONS:**
1.  **Adhere to the Format:** Use Markdown tables and headers exactly as specified in the template below. Do not deviate.
2.  **Prioritize Teaching Style:** The most important customization is the **Teaching Style: '{teaching_style}'**. You MUST adapt the 'SCHEME OF TEACHING' section, especially the activities, examples, and instructor's role, to perfectly match this style. For example:
    -   If 'Case-Study & Problem-Based', the main activity must be a detailed case study.
    -   If 'Interactive & Hands-on', include practical exercises, live demonstrations, or group activities.
    -   If 'Flipped Classroom', the plan should focus on in-class activities that build upon pre-read material, not on lecturing new content.
3.  **Be Specific:** Do not provide generic guidance. Write the exact questions, examples, and talking points the instructor should use.
4.  **Hybrid Knowledge:** If 'Reference Document Context' is provided, base your content primarily on it. Otherwise, rely on your own expertise about the syllabus topic.
5.  **Fill Every Section:** Provide plausible and detailed content for all parts of the lesson plan.

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

**6. LIST OF TEACHING AIDS**
| No. | Description | Remarks |
| :--- | :--- | :--- |
| (a) | **BR/Text Book / Pre-Read Material** | *Suggest 1-2 relevant textbooks. If the style is 'Flipped Classroom', specify this as mandatory pre-reading material.* |
| (b) | **CBT/PPT** | *Suggest key themes for a presentation. For 'Lecture' style, this is primary. For 'Interactive' style, it's a supplement with visuals and prompts.* |

**7. PRACTICAL IN LAB/EQUIPMENT ROOMS**
> *Specify if the chosen teaching style requires it (e.g., for a 'Demonstration' style). Otherwise, state 'Nil'.*

**8. EXISTING KNOWLEDGE OF THE CLASS**
> The trainees have a basic understanding of [mention a foundational concept], but are likely unaware of the specific models and practical application techniques covered in this lesson.

**9. CHECKING OF PREVIOUS KNOWLEDGE / INTRODUCTION (05 Min)**
*Instructor to ask the following questions to bridge the previous lesson and introduce the topic:*
> (a) "Can anyone tell me what we discussed last time regarding [previous related topic]?"
> (b) "Based on your pre-reading (for Flipped Classroom) or general knowledge, what does the term '[key syllabus term]' mean to you?"
> (c) "Why do you think understanding [topic] is important in our field?"

---

### **PART B: DEVELOPMENT OF LESSON PLAN**

| SCHEME OF TEACHING | METHOD | TRG AIDS | TIME (Min) |
| :--- | :--- | :--- | :--- |
| **(a) Introduction & Session Framing** <br> *Instructor states the topic and its importance, framing the session according to the **{teaching_style}** style.* <br> **Talking Point:** "Good morning. Today, we're going to tackle {topic}. We'll be using a **{teaching_style}** approach, which means..." | L/Ds | PPT Slide 1-2 | 5 |
| **(b) Core Activity Part 1: [First Key Concept]** <br> ***Instruction tailored to {teaching_style}***. <br> *[For Lecture: Explain the concept with examples. For Case-Study: Introduce the case and the first problem. For Interactive: Pose a question and facilitate a group brainstorm.]* | {teaching_style_abbr} | PPT / Whiteboard | 20 |
| **(c) Core Activity Part 2: [Second Key Concept]** <br> ***Instruction tailored to {teaching_style}***. <br> *[For Lecture: Explain the second concept. For Case-Study: Groups work on solving the case. For Interactive: Trainees perform a hands-on task or simulation.]* | {teaching_style_abbr} | Handout / Equipment | 25 |
| **(d) Debrief and Synthesis** <br> *Instructor facilitates a discussion to connect the activity back to the learning objectives.* <br> **Guiding Question:** "Excellent work. Now, let's synthesize. How does the solution to our case study demonstrate the [key model from syllabus]? What were the key decision points?" | Ds | Whiteboard | 15 |
| **(e) Summary and Evaluation** <br> *Instructor summarizes the key takeaways, recapping the specific objectives in the context of the activity.* <br> **Recap Questions:** "To quickly recap, can someone define [key term 1]? How did our activity illustrate [key term 2]?" | L | PPT Slide | 10 |
| **(f) Home Assignment and Follow-up** <br> *Instructor gives a thought-provoking assignment that extends the in-class activity.* <br> **Assignment:** "[Pose a practical, open-ended question related to the {teaching_style} activity. E.g., 'Find one real-world example that mirrors our case study and analyze it using the same framework.']" | - | - | 5 |

---

### **PART C: PREPARATION FOR TOMORROW (PFT)**

| Ser | Syllabus for PFT | References | Related Lesson Plan Number |
| :--- | :--- | :--- | :--- |
| 1 | [Generate a logical next topic that would follow the current lesson] | Handout / Chapter X | {next_lesson_no} |

---

### **PART D: PERSONAL EXPERIENCE OF INSTRUCTOR**

| Ser | Item | Remarks |
| :--- | :--- | :--- |
| 1 | **Additional resources/Techniques used** | *Suggest a technique specific to the **{teaching_style}**. E.g., "For the Case-Study method, used the 'Jigsaw' technique to have groups become experts on different parts of the problem."* |
| 2 | **Doubts/Intelligent questions raised by the trainees** | *Anticipate a question relevant to the **{teaching_style}**. E.g., "A trainee asked if the case study had a single 'right' answer, leading to a discussion on decision-making under ambiguity."* |
| 3 | **Difficulties faced by Instructor** | *Anticipate a challenge related to the **{teaching_style}**. E.g., "Keeping the more dominant groups from finishing the problem-based exercise too quickly was a challenge."* |
| 4 | **Suggestions for improvement** | *Suggest an improvement for the **{teaching_style}**. E.g., "Next time, provide different data sets to each group to encourage more diverse solutions."* |

---
### **INPUT FOR GENERATION**
---

*   **Reference Document Context:** "{pdf_context}"
*   **Syllabus Extract:** "{syllabus_extract}"

---

Now, generate the complete lesson plan based on all the provided information.
"""

# --- Main Application UI ---

st.title("⚓ AI Lesson Plan Generator")
st.markdown("This tool generates a hyper-detailed lesson plan in your institute's format, customized to your teaching style.")

if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ""

with st.sidebar:
    st.header("⚙️ 1. Lesson Details")
    
    # --- NEW: Text input for Institute Name ---
    institute_name_input = st.text_input(
        "Institute Name:", 
        "NAVAL INSTITUTE OF EDUCATIONAL AND TRAINING TECHNOLOGY"
    )
    
    subject_input = st.text_input("Subject:", "Training Technology")
    class_input = st.text_input("Class:", "TT(O)")
    
    col1, col2 = st.columns(2)
    with col1:
        lesson_no_input = st.number_input("Lesson No:", min_value=1, value=11)
    with col2:
        total_lessons_input = st.number_input("Total Lessons:", min_value=1, value=25)
    
    duration_input = st.number_input("Duration (Mins):", min_value=30, value=80, step=10)

    st.header("👨‍🏫 2. Instructional Method")
    teaching_style_option = st.selectbox(
        "Select Teaching Style:",
        ("Lecture & Discussion", "Case-Study & Problem-Based", "Interactive & Hands-on", "Flipped Classroom", "Demonstration"),
        help="The AI will tailor the lesson activities to match this style."
    )
    style_abbr_map = {
        "Lecture & Discussion": "L/Ds", "Case-Study & Problem-Based": "PBL/Ds",
        "Interactive & Hands-on": "Pr/Ds", "Flipped Classroom": "FC/Ds", "Demonstration": "Dm/L"
    }
    teaching_style_abbr = style_abbr_map[teaching_style_option]

    st.header("📄 3. Lesson Content")
    syllabus_input = st.text_area(
        "Syllabus Extract:",
        "Motivation, Motivational functions of an instructor. List of activities which contribute towards motivation in the trainees, Instructor's motivation, Motivational grid.",
        height=125
    )
    uploaded_pdf = st.file_uploader("Upload Reference PDF (Optional)", type="pdf")
    
    st.header("🚀 4. Generate")
    generate_button = st.button("✨ Generate Lesson Plan", type="primary", use_container_width=True)

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
                    with st.sidebar: st.success("✅ PDF Read Successfully")
            
            final_prompt = MASTER_PROMPT_TEMPLATE.format(
                subject=subject_input, class_name=class_input, lesson_no=lesson_no_input,
                total_lessons=total_lessons_input, duration=duration_input,
                topic=syllabus_input.strip().split(',')[0], syllabus_extract=syllabus_input,
                next_lesson_no=lesson_no_input + 1, pdf_context=pdf_context_text,
                teaching_style=teaching_style_option, teaching_style_abbr=teaching_style_abbr
            )
        
        with st.spinner(f"🧠 AI is crafting your plan using the '{teaching_style_option}' style. This may take a few minutes..."):
            st.session_state.generated_plan = generate_lesson_plan(final_prompt)
        
        if "Error:" in st.session_state.generated_plan:
            st.error(st.session_state.generated_plan)
        else:
            st.success("Lesson Plan Generated Successfully!")

if st.session_state.generated_plan and "Error:" not in st.session_state.generated_plan:
    with output_area.container():
        st.markdown(st.session_state.generated_plan)
        
        try:
            # --- MODIFIED: Pass the institute_name_input to the function ---
            pdf_bytes = markdown_to_pdf(
                st.session_state.generated_plan, 
                subject_input, 
                institute_name_input 
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
st.markdown("Powered by [Ollama](https://ollama.com) & [Streamlit](https://streamlit.io)")