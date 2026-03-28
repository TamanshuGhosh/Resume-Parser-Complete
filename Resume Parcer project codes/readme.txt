AI RESUME PARSER AND CANDIDATE MATCHING SYSTEM
=============================================

1. PROBLEM STATEMENT
--------------------
Recruiters often receive a large number of resumes for a single job role. 
Manually reviewing and shortlisting candidates based on skills, experience, 
and relevance to the job description is time-consuming and inefficient.

This project aims to automate the process of:
- Parsing resumes (PDF/DOCX)
- Extracting key information such as skills, education, and experience
- Matching candidates with a given job description
- Ranking candidates based on relevance using AI techniques

The system improves efficiency, reduces manual effort, and provides 
data-driven candidate selection.

------------------------------------------------------------

2. TECHNOLOGIES USED
--------------------
- Python (Core programming language)
- FastAPI (Backend API framework)
- Streamlit (Frontend dashboard/UI)
- spaCy (Natural Language Processing)
- SentenceTransformers (Text embeddings)
- FAISS (Similarity search and ranking)
- PyMuPDF (PDF text extraction)
- python-docx (DOCX file parsing)
- NumPy (Numerical computations)

------------------------------------------------------------

3. HOW TO RUN THE PROJECT
-------------------------

Prerequisites:
- Python 3.9 or above installed
- Required libraries installed (via pip)

Step 1: Install Dependencies
---------------------------
Run the following command:

pip install fastapi uvicorn streamlit spacy pymupdf python-docx sentence-transformers faiss-cpu numpy

Also download spaCy model:

python -m spacy download en_core_web_sm

------------------------------------------------------------

Step 2: Run the Application (Recommended Method)
-----------------------------------------------

Use the unified launcher script:

python run_app.py

This will automatically:
- Start the FastAPI backend server
- Launch the Streamlit frontend dashboard

------------------------------------------------------------

Step 3: Manual Run (Alternative)
-------------------------------

If not using run_app.py, run both services separately:

Terminal 1 (Backend):
uvicorn app:app --reload

Terminal 2 (Frontend):
streamlit run dashboard.py

------------------------------------------------------------

Step 4: Using the Application
----------------------------

1. Open the Streamlit dashboard in your browser
2. Upload multiple resumes (PDF/DOCX)
3. Enter job description and required skills
4. Set minimum experience (optional)
5. Click "Search Candidates"
6. View ranked candidates along with:
   - Name
   - Resume file name
   - Skills
   - Experience
   - Match score

------------------------------------------------------------

4. PROJECT FEATURES
-------------------
- Multi-format resume parsing (PDF & DOCX)
- Skill extraction using NLP
- Experience estimation from text
- Semantic matching using embeddings
- Candidate ranking using weighted scoring
- Interactive UI dashboard
- Resume traceability via file names

------------------------------------------------------------

5. NOTES
--------
- Ensure backend is running before using frontend
- Resumes must be uploaded before searching candidates
- Experience extraction may vary depending on resume format
- System uses approximate matching and may not be 100% accurate

------------------------------------------------------------

6. FILE STRUCTURE
-----------------
- app.py            → FastAPI backend
- dashboard.py      → Streamlit frontend
- run_app.py        → Unified launcher script
- resumes/          → Uploaded resume storage

------------------------------------------------------------

END OF DOCUMENT