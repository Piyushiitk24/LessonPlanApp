# --- FINAL, POLISHED MASTER PROMPT TEMPLATE ---
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