from flask import render_template

from auto_resume import app
from auto_resume.model.config import Files
from auto_resume.model.resume import MasterResume


@app.route("/")
def root():
    print('ROOT')
    resume = MasterResume.load(Files.plain_text_resume_file)
    return render_template("index.html.j2", resume=resume)


