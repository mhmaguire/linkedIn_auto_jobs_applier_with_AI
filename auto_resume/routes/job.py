from flask import render_template
from qdrant_client import QdrantClient

from auto_resume import app
from auto_resume.model import Job, MasterResume, Files

from langchain_openai.embeddings import OpenAIEmbeddings

@app.route("/jobs")
def jobs():
    # async with get_db():
    jobs = Job.prisma().find_many()
    resume = MasterResume.load(Files.plain_text_resume_file)
    query = OpenAIEmbeddings().embed_query(str(resume))
    qdrant = QdrantClient()
    results = qdrant.search('auto_resume_jobs', 
                            query_vector=query,
                            limit=1000,
                            with_payload=['metadata'])

    results = {result.payload['metadata']['source']: result for result in results}
    jobs = [{'score': results.get(job.id, None), 'job': job} for job in jobs]
    jobs = list(sorted(jobs, reverse=True, key=lambda x: x['score'].score))

    return render_template("jobs.html.j2", **{"jobs": jobs})


@app.route("/jobs/<job_id>")
def job(job_id):
    # async with get_db():
    job = Job.prisma().find_unique(
        where={"id": job_id}, include={"company": True, "resumes": True}
    )

    return render_template("job.html.j2", job=job)


@app.post("/jobs/<job_id>/summarize")
def summarize(job_id):
    # async with get_db():
    job = Job.summarize(job_id)

    return render_template("job.html.j2", job=job)


@app.post("/jobs/<job_id>/resume")
def resume(job_id):
    # async with get_db():
    resume = MasterResume.load(Files.plain_text_resume_file)
    job = Job.generate_resume(job_id, master_resume=resume)

    return render_template("job.html.j2", job=job)
