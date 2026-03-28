# Resume-Parser-Complete
AI-powered resume parser with recruiter dashboard.

---

## 🔍 Problem Statement

Recruiters often receive a large number of resumes for a single job role.  
Manually reviewing and shortlisting candidates based on skills, experience, and relevance is:

- Time-consuming  
- Error-prone  
- Inefficient  

This project automates the process of:

- Parsing resumes (PDF/DOCX)
- Extracting key information (skills, education, experience)
- Matching candidates with job descriptions
- Ranking candidates using AI-based scoring

---

## 🚀 Features

- 📂 Upload multiple resumes (PDF & DOCX)
- 🧠 NLP-based skill extraction
- 📅 Experience detection (years + date ranges)
- 🤖 Semantic matching using embeddings
- 📊 Candidate ranking using weighted scoring
- 📄 Resume file name tracking
- 💻 Interactive Streamlit dashboard

---

## 🛠️ Technologies Used

| Category        | Tools / Libraries |
|----------------|------------------|
| Language        | Python |
| Backend         | FastAPI |
| Frontend        | Streamlit |
| NLP             | spaCy |
| Embeddings      | SentenceTransformers |
| Similarity      | FAISS |
| PDF Parsing     | PyMuPDF |
| DOCX Parsing    | python-docx |
| Computation     | NumPy |

---

## 📁 Project Structure
project-folder/
│
├── app.py # FastAPI backend
├── dashboard.py # Streamlit frontend
├── run_app.py # Run both frontend + backend together
├── resumes/ # Uploaded resumes
└── README.md
