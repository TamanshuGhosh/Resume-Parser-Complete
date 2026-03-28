import os
import re
import shutil
import fitz
import spacy
import faiss
import datetime
import numpy as np

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from docx import Document
from sentence_transformers import SentenceTransformer

# LOAD MODELS

nlp = spacy.load("en_core_web_sm")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# FASTAPI INIT

app = FastAPI()

# STORAGE

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# TEXT EXTRACTION

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    return ""

# CLEAN TEXT

def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text

# BASIC INFO

def extract_basic_info(text):
    doc = nlp(text)
    name = None

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    email = re.findall(r"\S+@\S+", text)
    phone = re.findall(r"\+?\d[\d -]{8,12}\d", text)

    return name, email, phone

# EDUCATION

education_keywords = [
    "bachelor","master","b.tech","mba","phd","bsc","msc",
    "b.e","be","m.e","me","bca","mca","bba","bcom","mcom"
]

def extract_education(text):
    text = text.lower()
    found = []

    for keyword in education_keywords:
        if keyword in text:
            found.append(keyword)

    return list(set(found))

# EXPERIENCE

def extract_experience_years(text):
    text = text.lower()

    total_months = 0

    # CASE 1: "X years" 
    matches = re.findall(r"(\d+)\+?\s*(years|yrs)", text)
    for m in matches:
        total_months += int(m[0]) * 12

    # CASE 2: Month-Year ranges 
    month_map = {
        "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
        "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
    }

    pattern = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*(20\d{2})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present)[a-z]*\s*(20\d{2})?"

    matches = re.findall(pattern, text)

    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    for start_m, start_y, end_m, end_y in matches:
        start_month = month_map.get(start_m[:3], 1)
        start_year = int(start_y)

        if end_m == "present":
            end_month = current_month
            end_year = current_year
        else:
            end_month = month_map.get(end_m[:3], 1)
            end_year = int(end_y)

        months = (end_year - start_year) * 12 + (end_month - start_month)
        if months > 0:
            total_months += months

    # CASE 3: Year ranges 
    year_ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present)", text)

    for start, end in year_ranges:
        start = int(start)
        end = current_year if end == "present" else int(end)

        if end >= start:
            total_months += (end - start) * 12

    # FINAL OUTPUT
    total_years = total_months / 12

    return round(total_years, 1)

# SKILLS

skills_ontology = [
    "python","java","c++","c","javascript","typescript","go","rust","kotlin","swift",
    "machine learning","deep learning","nlp","computer vision","data science",
    "data analysis","statistics","pandas","numpy","scikit-learn","tensorflow","keras","pytorch",
    "sql","mysql","postgresql","mongodb","oracle","sqlite","redis",
    "excel","power bi","tableau","spark","hadoop",
    "html","css","react","angular","vue","node.js","express","django","flask","fastapi",
    "aws","azure","gcp","docker","kubernetes","ci/cd","jenkins","terraform",
    "git","github","linux","bash","jira","postman",
    "financial analysis","accounting","taxation","auditing","tally","sap"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in skills_ontology:
        if skill in text:
            found.append(skill)

    return list(set(found))

# EMBEDDINGS

def embed_text(text):
    return embedding_model.encode(text)

# FAISS

dimension = 384
index = faiss.IndexFlatL2(dimension)
metadata_store = []

def reset_index():
    global index, metadata_store
    index = faiss.IndexFlatL2(dimension)
    metadata_store = []

def add_to_index(embedding, metadata):
    vector = np.array([embedding]).astype("float32")
    index.add(vector)
    metadata_store.append(metadata)

def search_index(query_embedding, k=5):
    if len(metadata_store) == 0:
        return []

    query = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query, min(k, len(metadata_store)))

    results = []

    for i, idx in enumerate(indices[0]):
        if idx < len(metadata_store):
            candidate = metadata_store[idx].copy()
            similarity = 1 / (1 + distances[0][i])
            candidate["similarity_score"] = round(float(similarity), 4)
            results.append(candidate)

    return results

# PIPELINE

def process_resume(file_path):
    text = parse_resume(file_path)
    text = clean_text(text)

    name, email, phone = extract_basic_info(text)
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience_years(text)

    embedding = embed_text(text)

    candidate = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience_years": experience
    }

    return candidate, embedding

# REQUEST MODEL

class Query(BaseModel):
    job_description: str
    required_skills: str = ""
    min_experience: int = 0

# UPLOAD

@app.post("/upload")
async def upload_resumes(files: list[UploadFile]):
    reset_index()

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        candidate, embedding = process_resume(file_path)
        candidate["file_name"] = file.filename
        add_to_index(embedding, candidate)

    return {"message": "Resumes uploaded successfully"}

# SEARCH

@app.post("/search")
def search_candidates(query: Query):

    query_embedding = embed_text(query.job_description)
    job_skills = [s.strip().lower() for s in query.required_skills.split(",") if s]

    results = search_index(query_embedding)

    final_results = []

    for c in results:

        candidate_skills = [s.lower() for s in c.get("skills", [])]

        if job_skills:
            matched = set(candidate_skills) & set(job_skills)
            skill_match = len(matched) / len(job_skills)
        else:
            matched = []
            skill_match = 0

        exp = c.get("experience_years", 0)
        exp_score = min(exp / 10, 1)

        if exp < query.min_experience:
            exp_score *= 0.5

        sim_score = c.get("similarity_score", 0)

        final_score = ((
            0.5 * skill_match +
            0.3 * exp_score +
            0.2 * sim_score)* 100
        )

        c["skill_match"] = round(skill_match * 100, 2)
        c["matched_skills"] = list(matched)
        c["final_score"] = round(final_score, 4)

        final_results.append(c)
        print(c)

    return {"results": final_results}