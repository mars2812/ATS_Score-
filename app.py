import streamlit as st
import PyPDF2 as pdf
import re
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect('resume_ats.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY,
            resume_text TEXT,
            job_description TEXT,
            ats_score REAL,
            email TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_resume_data(resume_text, job_description, ats_score, email, phone):
    conn = sqlite3.connect('resume_ats.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes (resume_text, job_description, ats_score, email, phone)
        VALUES (?, ?, ?, ?, ?)
    ''', (resume_text, job_description, ats_score, email, phone))
    conn.commit()
    conn.close()

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page_obj = reader.pages[page]
        text += page_obj.extract_text()
    return text

def calculate_ats_score(resume_text, job_description):
    documents = [resume_text, job_description]
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform(documents)
    tfidf_matrix = X.toarray()
    similarity_score = np.dot(tfidf_matrix[0], tfidf_matrix[1]) / (np.linalg.norm(tfidf_matrix[0]) * np.linalg.norm(tfidf_matrix[1]))
    score_percentage = round(similarity_score * 100, 2)
    return score_percentage

# def extract_skills(resume_text):
#     skills = re.findall(r'\b(?:Python|Java|JavaScript|SQL|HTML|CSS|Data Science|Machine Learning|Deep Learning|React|Django|Node.js|AWS|GCP|Azure)\b', resume_text, re.IGNORECASE)
#     return set(skills)

# def suggest_additional_skills(job_description):
#     recommended_skills = set()
    
#     if re.search(r'\b(?:Data Science|Machine Learning|Deep Learning|AI)\b', job_description, re.IGNORECASE):
#         recommended_skills = {'Python', 'R', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'Keras', 'Pandas', 'NumPy', 'SciPy'}
#     elif re.search(r'\b(?:Web Development|Frontend|Backend|JavaScript|React|Angular|Django|Flask)\b', job_description, re.IGNORECASE):
#         recommended_skills = {'HTML', 'CSS', 'JavaScript', 'React', 'Angular', 'Node.js', 'Django', 'Flask', 'MySQL', 'PostgreSQL'}
#     elif re.search(r'\b(?:Cloud|AWS|Azure|GCP)\b', job_description, re.IGNORECASE):
#         recommended_skills = {'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform'}
#     else:
#         recommended_skills = {'Communication', 'Project Management', 'Problem Solving'}
    
#     return recommended_skills

def extract_contact_info(resume_text):
    # Regex for email
    email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', resume_text)
    
    # Regex for phone numbers (various formats)
    phone = re.search(r'\b(\+?\d{1,4}[-.\s]?)?(\(?\d{1,3}\)?[-.\s]?)?(\d{1,4}[-.\s]?)?(\d{1,4}[-.\s]?)?(\d{1,9})\b', resume_text)
    
    return {
        'Email': email.group(0) if email else 'Not found',
        'Phone': phone.group(0) if phone else 'Not found'
    }

# Initialize the database
init_db()

# Streamlit app
st.markdown("""
    <style>
    .title {
        color: #FF6F61;
        font-size: 36px;
        text-align: center;
        font-weight: bold;
    }
    .subheader {
        color: #FF6F61;
        font-size: 24px;
        font-weight: bold;
    }
    .section {
        margin-top: 20px;
        padding: 10px;
        border-radius: 5px;
        background-color: #F9F9F9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .ats-score {
        font-size: 28px;
        font-weight: bold;
        color: #FF6F61;
        text-align: center;
    }
    .button {
        background-color: #FF6F61;
        color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="title">Resume ATS Score</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center;">
        <h2>Evaluate your resume to know your ATS score</h2>
    </div>
    """,
    unsafe_allow_html=True
)

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF file")

if uploaded_file is not None and jd:
    resume_text = input_pdf_text(uploaded_file)
    ats_score = calculate_ats_score(resume_text, jd)
    # skills = extract_skills(resume_text)
    job_description = jd  # Directly use job description text
    # additional_skills = suggest_additional_skills(job_description)
    # contact_info = extract_contact_info(resume_text)
    
    st.markdown('<div class="section"><div class="ats-score">Your resume matches the job description by {:.2f}%</div></div>'.format(ats_score), unsafe_allow_html=True)
    
    # st.markdown('<div class="section"><div class="subheader">Contact Information Extracted</div></div>', unsafe_allow_html=True)
    # st.write(f"Email: {contact_info['Email']}")
    # st.write(f"Phone: {contact_info['Phone']}")
    
    # st.markdown('<div class="section"><div class="subheader">Skills in Your Resume</div></div>', unsafe_allow_html=True)
    # st.write(f"Skills found: {', '.join(skills)}")
    
    # st.markdown('<div class="section"><div class="subheader">Recommended Skills Based on Job Description</div></div>', unsafe_allow_html=True)
    # st.write(f"Consider adding the following skills:")
    # st.write(f"{', '.join(additional_skills)}")
    
    # st.markdown('<div class="section"><div class="subheader">Project Ideas to Enhance Your Resume</div></div>', unsafe_allow_html=True)
    # if re.search(r'\b(?:Data Science|Machine Learning|Deep Learning|AI)\b', job_description, re.IGNORECASE):
    #     st.write("- Build a machine learning model to predict stock prices")
    #     st.write("- Create a data visualization dashboard using Python")
    # elif re.search(r'\b(?:Web Development|Frontend|Backend|JavaScript|React|Angular|Django|Flask)\b', job_description, re.IGNORECASE):
    #     st.write("- Develop a full-stack web application")
    #     st.write("- Create a personal portfolio website")
    # elif re.search(r'\b(?:Cloud|AWS|Azure|GCP)\b', job_description, re.IGNORECASE):
    #     st.write("- Set up a cloud-based infrastructure using AWS or Azure")
    #     st.write("- Develop a CI/CD pipeline with Docker and Kubernetes")
    # else:
    #     st.write("- Improve your soft skills and work on general projects")
    
    # Save data to database
    # save_resume_data(resume_text, jd, ats_score, contact_info['Email'], contact_info['Phone'])
