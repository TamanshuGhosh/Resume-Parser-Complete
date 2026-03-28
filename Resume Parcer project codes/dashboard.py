import streamlit as st
import requests

# PAGE CONFIG
st.set_page_config(page_title="AI Resume Parser", layout="wide")

# HEADER
st.markdown(
    """
    <h1 style='text-align: center;'>📄 AI Resume Parser Dashboard</h1>
    <p style='text-align: center; color: gray;'>Find the best candidates instantly</p>
    """,
    unsafe_allow_html=True
)

st.divider()

#INPUT SECTION
col1, col2 = st.columns(2)

with col1:
    job_desc = st.text_area("📝 Job Description")

with col2:
    required_skills = st.text_input("🛠 Required Skills (comma separated)")
    min_exp = st.slider("💼 Minimum Experience (Years)", 0, 10, 0)

#SEARCH BUTTON
st.markdown("## 📂 Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload multiple resumes (PDF/DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if st.button("📤 Upload Resumes"):
    if not uploaded_files:
        st.warning("Please upload at least one resume")
    else:
        with st.spinner("Uploading resumes..."):
            try:
                files = [
                    ("files", (file.name, file.getvalue()))
                    for file in uploaded_files
                ]

                res = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files=files
                )

                if res.status_code == 200:
                    st.success("✅ Resumes uploaded successfully!")
                else:
                    st.error(f"Upload failed: {res.text}")

            except Exception as e:
                st.error(f"Error: {e}")

st.divider()

if st.button("🔍 Search Candidates", use_container_width=True):

    if not job_desc.strip():
        st.warning("Please enter a job description")
        st.stop()

    with st.spinner("Analyzing candidates..."):

        try:
            res = requests.post(
                "http://127.0.0.1:8000/search",
                json={
                    "job_description": job_desc,
                    "required_skills": required_skills,
                    "min_experience": min_exp
                },
                timeout=15
            )

            res.raise_for_status()
            data = res.json()

        except requests.exceptions.ConnectionError:
            st.error("🚫 Backend is not running")
            st.stop()

        except requests.exceptions.Timeout:
            st.error("⏳ Request timed out")
            st.stop()

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
            st.stop()

    #PROCESS RESULTS
    results = data.get("results", [])

    if not results:
        st.warning("No candidates found")
        st.stop()

    job_skills = [s.strip().lower() for s in required_skills.split(",") if s]

    processed_results = []

    for c in results:
        candidate_skills = [s.lower() for s in c.get("skills", [])]

        if job_skills:
            matched = set(candidate_skills) & set(job_skills)
            skill_match = len(matched) / len(job_skills)
        else:
            matched = []
            skill_match = 0

        c["skill_match"] = round(skill_match * 100, 2)
        c["matched_skills"] = list(matched)

        processed_results.append(c)

    #FILTER
    
    filtered_results = processed_results

    #SORT
    sorted_results = sorted(
        filtered_results,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )

    if not sorted_results:
        st.warning("No candidates matched your filters")
        st.stop()

    #TOP CANDIDATE
    top = sorted_results[0]

    st.markdown("## 🏆 Top Candidate")
    st.success(
        f"{top.get('name','Unknown')} | Score: {round(top.get('final_score',0)*100,2)}%"
    )

    st.divider()

    #DISPLAY ALL CANDIDATES
    st.markdown("## 📋 Candidate Rankings")

    for c in sorted_results:

        name = c.get("name", "Unknown")
        email = c.get("email", "N/A")
        phone = c.get("phone", "N/A")
        exp = c.get("experience_years", 0)
        edu = c.get("education", "N/A")
        skills = c.get("skills", [])
        score = float(c.get("final_score", 0))
        score = max(0, min(score, 1))
        file_name = c.get("file_name", "Unknown file")

        st.markdown(f"### 👤 {name}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"📧 **Email:** {email}")
            st.markdown(f"📞 **Phone:** {phone}")

        with col2:
            st.markdown(f"💼 **Experience:** {exp} years")
            st.markdown(f"🎓 **Education:** {edu}")

        with col3:
            st.markdown(f"🎯 **Skill Match:** {c['skill_match']}%")
            st.markdown(f"✅ **Matched Skills:** {', '.join(c['matched_skills'])}")

        st.markdown(f"🛠 **Skills:** {', '.join(skills)}")
        st.markdown(f"📄 **Resume:** {file_name}")

        st.progress(score)

        with st.expander("📊 Detailed Info"):
            st.write("Timeline:", c.get("timeline", "N/A"))
            st.write("Final Score:", c.get("final_score", 0))

        st.divider()