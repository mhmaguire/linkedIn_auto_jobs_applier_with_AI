from flask import send_file, abort

from auto_resume import app
from auto_resume.model.resume import Resume


def get_resume(resume_id):
    resume = Resume.prisma().find_unique(
        where={"id": resume_id},
        include={"job": {"include": {"company": True}}},
    )

    if not resume:
        abort(404, description="Resume not found")

    return resume


@app.route("/api/resumes/<resume_id>")
def show_resume(resume_id):
    return {"resume": get_resume(resume_id).model_dump()}


@app.post("/api/resumes/<resume_id>/pdf")
def resume_pdf(resume_id):
    return send_file(get_resume(resume_id).to_pdf(), as_attachment=True)


@app.post("/api/resume/<resume_id>/cover_letter")
def cover_letter(resume_id):
    return {"resume": get_resume(resume_id).cover_letter(resume_id)}
