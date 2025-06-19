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

# --- FINAL, ROBUST PDF GENERATION CLASS AND FUNCTION ---
class PDF(FPDF):
    def __init__(self, institute_name):
        super().__init__()
        self.institute_name = institute_name
        font_path = 'DejaVuSans.ttf'
        if os.path.exists(font_path):
            self.add_font('DejaVu', '', font_path, uni=True)
            self.add_font('DejaVu', 'B', font_path, uni=True)
            self.add_font('DejaVu', 'I', font_path, uni=True)
            self.set_font('DejaVu', '', 10)
        else:
            st.warning("DejaVuSans.ttf not found. PDF may have character issues.")
            self.set_font("Helvetica", size=10)

    def header(self):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, self.institute_name, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def write_markdown(self, markdown_text):
        self.set_font('DejaVu', '', 10)
        lines = markdown_text.split('\n')
        for line in lines:
            if line.startswith('# '):
                self.set_font('DejaVu', 'B', 16)
                self.multi_cell(0, 10, line[2:], ln=1)
                self.set_font('DejaVu', '', 10)
            elif line.startswith('### '):
                self.ln(5)
                self.set_font('DejaVu', 'B', 12)
                self.multi_cell(0, 8, line[4:], ln=1, border='B')
                self.set_font('DejaVu', '', 10)
                self.ln(3)
            elif line.startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if not cells: continue

                if len(cells) == 4:
                    col_widths = [80, 25, 35, 20]
                elif len(cells) == 3:
                    col_widths = [20, 80, 60]
                else:
                    col_widths = [40, 120]

                line_height = 5
                max_lines = 1
                for i, cell in enumerate(cells):
                    text_width = self.get_string_width(cell.replace('**', ''))
                    num_lines = (text_width // col_widths[i]) + 1
                    if num_lines > max_lines:
                        max_lines = num_lines
                
                row_height = line_height * max_lines
                
                x_start, y_start = self.get_x(), self.get_y()
                for i, cell in enumerate(cells):
                    current_x = self.get_x()
                    current_y = self.get_y()
                    
                    if '**' in cell:
                        self.set_font('DejaVu', 'B', 10)
                        cell = cell.replace('**', '')
                    else:
                        self.set_font('DejaVu', '', 10)
                    
                    self.multi_cell(col_widths[i], line_height, cell, border=1, align='L')
                    self.set_xy(current_x + col_widths[i], current_y)
                
                self.set_xy(x_start, y_start + row_height)
                self.set_font('DejaVu', '', 10)
            else:
                self.multi_cell(0, 5, line, ln=1)

def markdown_to_pdf(markdown_text, subject, institute_name):
    pdf = PDF(institute_name=institute_name)
    pdf.add_page()
    pdf.write_markdown(markdown_text)
    # --- BUG FIX: Explicitly convert the bytearray from output() to bytes ---
    return bytes(pdf.output())

def generate_lesson_plan(final_prompt):
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

# --- MASTER PROMPT TEMPLATE (This remains the same) ---
MASTER_PROMPT_TEMPLATE = """
You are an expert instructional designer and master trainer for a military educational institution. Your task is to create a hyper-detailed, all-inclusive lesson plan.

**CRITICAL INSTRUCTIONS:**
1.  **Strictly Adhere to the Format:** Use Markdown tables and headers exactly as specified in the template below. **IMPORTANT: Do NOT include the Markdown table header separator line (e.g., | :--- | :--- |) in your output.**
2.  **Prioritize Teaching Style:** The most important customization is the **Teaching Style: '{teaching_style}'**. You MUST adapt the 'SCHEME OF TEACHING' section to perfectly match this style.
3.  **Be Hyper-Specific:** Do not provide generic guidance. Write the exact questions, examples, and talking points the instructor should use.
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
| (a) | **BR/Text Book / Pre-Read Material** | *Suggest 1-2 relevant textbooks. If the style is 'Flipped Classroom', specify this as mandatory pre-reading material.* |
| (b) | **CBT/PPT** | *Suggest key themes for a presentation. For 'Lecture' style, this is primary. For 'Interactive' style, it's a supplement with visuals and prompts.* |

**7. PRACTICAL IN LAB/EQUIPMENT ROOMS**
> *Specify if the chosen teaching style requires it (e.g., for a 'Demonstration' style). Otherwise, state 'Nil'.*

**8. EXISTING KNOWLEDGE OF THE CLASS**
> The trainees have a basic understanding of [mention a foundational concept], but are likely unaware of the specific models and practical application techniques covered in this lesson.

**9. CHECKING OF PREVIOUS KNOWLEDGE / INTRODUCTION (05 Min)**
*Instructor to ask the following questions:*
> (a) "Can anyone tell me what we discussed last time regarding [previous related topic]?"
> (b) "In your own words, what does the term '[key syllabus term]' mean to you?"

---

### **PART B: DEVELOPMENT OF LESSON PLAN**

| SCHEME OF TEACHING | METHOD | TRG AIDS | TIME (Min) |
| **(a) Introduction & Session Framing** <br> *Instructor states the topic and its importance, framing the session according to the **{teaching_style}** style.* <br> **Talking Point:** "Good morning. Today, we're going to delve into {topic}. We'll be using a **{teaching_style}** approach..." | {teaching_style_abbr} | PPT Slide 1-2 | 5 |
| **(b) Core Activity Part 1: [First Key Concept]** <br> ***Instruction tailored to {teaching_style}***. <br> *[For Lecture: Explain the concept with examples. For Case-Study: Introduce the case and the first problem. For Interactive: Pose a question and facilitate a group brainstorm.]* | {teaching_style_abbr} | PPT / Whiteboard | 20 |
| **(c) Core Activity Part 2: [Second Key Concept]** <br> ***Instruction tailored to {teaching_style}***. <br> *[For Lecture: Explain the second concept. For Case-Study: Groups work on solving the case. For Interactive: Trainees perform a hands-on task or simulation.]* | {teaching_style_abbr} | Handout / Equipment | 25 |
| **(d) Debrief and Synthesis** <br> *Instructor facilitates a discussion to connect the activity back to the learning objectives.* <br> **Guiding Question:** "Excellent work. Now, let's synthesize. How does the solution to our case study demonstrate the [key model from syllabus]?" | Ds | Whiteboard | 15 |
| **(e) Summary and Evaluation** <br> *Instructor summarizes the key takeaways, recapping the specific objectives in the context of the activity.* <br> **Recap Questions:** "To quickly recap, can someone define [key term 1]?" | L | PPT Slide | 10 |
| **(f) Home Assignment and Follow-up** <br> *Instructor gives a thought-provoking assignment that extends the in-class activity.* <br> **Assignment:** "[Pose a practical, open-ended question related to the {teaching_style} activity.]" | - | - | 5 |

---

### **PART C: PREPARATION FOR TOMORROW (PFT)**

| Ser | Syllabus for PFT | References | Related Lesson Plan Number |
| 1 | [Generate a logical next topic that would follow the current lesson] | Handout / Chapter X | {next_lesson_no} |

---

### **PART D: PERSONAL EXPERIENCE OF INSTRUCTOR**

| Ser | Item | Remarks |
| 1 | **Additional resources/Techniques used** | *Suggest a technique specific to the **{teaching_style}**.* |
| 2 | **Doubts/Intelligent questions raised by the trainees** | *Anticipate a likely question from a trainee.* |
| 3 | **Difficulties faced by Instructor** | *Anticipate a common teaching challenge related to the **{teaching_style}**.* |
| 4 | **Suggestions for improvement** | *Suggest a potential improvement for the **{teaching_style}**.* |

---
### **INPUT FOR GENERATION**
---

*   **Reference Document Context:** "{pdf_context}"
*   **Syllabus Extract:** "{syllabus_extract}"

---

Now, generate the complete lesson plan.
"""

# --- Main Application UI (This remains the same) ---
st.title("⚓ AI Lesson Plan Generator")
st.markdown("This tool generates a hyper-detailed lesson plan in your institute's format, customized to your teaching style.")

if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ""

with st.sidebar:
    st.header("⚙️ 1. Lesson Details")
    institute_name_input = st.text_input("Institute Name:", "NAVAL INSTITUTE OF EDUCATIONAL AND TRAINING TECHNOLOGY")
    subject_input = st.text_input("Subject:", "Training Technology")
    class_input = st.text_input("Class:", "TT(O)")
    col1, col2 = st.columns(2)
    with col1:
        lesson_no_input = st.number_input("Lesson No:", min_value=1, value=11)
    with col2:
        total_lessons_input = st.number_input("Total Lessons:", min_value=1, value=25)
    duration_input = st.number_input("Duration (Mins):", min_value=30, value=80, step=10)

    st.header("👨‍🏫 2. Instructional Method")
    teaching_style_option = st.selectbox("Select Teaching Style:", ("Lecture & Discussion", "Case-Study & Problem-Based", "Interactive & Hands-on", "Flipped Classroom", "Demonstration"))
    style_abbr_map = {"Lecture & Discussion": "L/Ds", "Case-Study & Problem-Based": "PBL/Ds", "Interactive & Hands-on": "Pr/Ds", "Flipped Classroom": "FC/Ds", "Demonstration": "Dm/L"}
    teaching_style_abbr = style_abbr_map[teaching_style_option]

    st.header("📄 3. Lesson Content")
    syllabus_input = st.text_area("Syllabus Extract:", "Motivation, Motivational functions of an instructor. List of activities which contribute towards motivation in the trainees, Instructor's motivation, Motivational grid.", height=125)
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
            pdf_bytes = markdown_to_pdf(st.session_state.generated_plan, subject_input, institute_name_input)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_bytes,
                file_name=f"Lesson_Plan_{lesson_no_input}_{subject_input.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Failed to generate PDF. Error: {e}")
            st.error("This can happen if the AI's output is malformed. Try generating again.")

st.markdown("---")
st.markdown("Powered by [Ollama](https://ollama.com) & [Streamlit](https://streamlit.io)")