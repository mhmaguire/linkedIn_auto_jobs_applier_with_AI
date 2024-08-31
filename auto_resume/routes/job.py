from flask import abort
from qdrant_client import QdrantClient

from auto_resume import app
from auto_resume.model import Job, MasterResume, Files

from langchain_openai.embeddings import OpenAIEmbeddings


def get_job(job_id):
    job = Job.prisma().find_unique(
        where={"id": job_id}, include={"company": True, "resumes": True}
    )

    if job is None:
        abort(404, description="Job not found")

    return job


@app.route("/api/jobs")
def jobs():
    jobs = Job.prisma().find_many()
    resume = MasterResume.load(Files.plain_text_resume_file)
    query = OpenAIEmbeddings().embed_query(str(resume))
    qdrant = QdrantClient()
    results = qdrant.search(
        "auto_resume_jobs", query_vector=query, limit=1000, with_payload=["metadata"]
    )

    results = {result.payload["metadata"]["source"]: result for result in results}

    def get_result(id):
        result = results.get(id, None)

        if result is None:
            return None

        return result.score

    jobs = [{"score": get_result(job.id), "job": job.model_dump()} for job in jobs]
    jobs = list(sorted(jobs, reverse=True, key=lambda x: x["score"]))

    return {"jobs": jobs}


@app.route("/api/jobs/<job_id>")
def job(job_id):
    return {"job": get_job(job_id).model_dump()}


@app.post("/api/jobs/<job_id>/summarize")
def summarize(job_id):
    return {"job": get_job(job_id).summarize().model_dump()}


@app.post("/api/jobs/<job_id>/resume")
def resume(job_id):
    resume = MasterResume.load(Files.plain_text_resume_file)

    return {"job": get_job(job_id).generate_resume(master_resume=resume).model_dump()}
