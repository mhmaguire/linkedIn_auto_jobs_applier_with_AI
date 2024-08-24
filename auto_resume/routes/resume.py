from flask import render_template, send_file

from auto_resume import app
from auto_resume.model.resume import Resume


@app.route("/jobs/<job_id>/resumes/<resume_id>")
def show_resume(job_id, resume_id):
    # async with get_db():
    resume = Resume.prisma().find_unique(
        where={"id": resume_id, "job_id": job_id},
        include={"job": {"include": {"company": True}}},
    )

    if not resume:
        return "Resume not found", 404

    return render_template("resume.html.j2", resume=resume)


@app.post("/resumes/<resume_id>/pdf")
def resume_pdf(resume_id):
    # async with get_db():
    resume = Resume.prisma().find_unique(
        where={"id": resume_id},
        include={"job": {"include": {"company": True}}},
    )

    if not resume:
        return "Resume not found", 404

    pdf_path = resume.to_pdf()

    return send_file(pdf_path, as_attachment=True)


@app.post("/resume/<resume_id>/cover_letter")
def cover_letter(resume_id):
    # async with get_db():
    resume = Resume.cover_letter(resume_id)

    return render_template("resume.html.j2", resume=resume)