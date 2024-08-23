from contextlib import asynccontextmanager
from flask import Flask, render_template, request, g
from markdown import Markdown
import jinja2

import prisma
from auto_resume.markdown import MarkdownExt
from auto_resume.model.job import Job
from auto_resume.model.resume import MasterResume, Resume
from auto_resume.model.config import Files, Config


app = Flask(__name__)
prisma.register(prisma.Prisma())
md = Markdown()

app.jinja_env.add_extension(MarkdownExt)


@app.template_filter('md')
def mkdn(s):
    print('MARKDOWN', s)
    
    return md.convert(s)


def get_resume():
    if 'resume' not in g:
        g.resume = MasterResume.load(Files.plain_text_resume_file)

    return g.resume


@asynccontextmanager
async def get_db():
    db = prisma.get_client()
    await db.connect()
    try: 
        yield
    finally: 
        await db.disconnect()


@app.route('/')
def root():
    resume = get_resume()
    return render_template('index.html.j2', resume=resume)

@app.route('/jobs')
async def jobs():
    async with get_db(): 
        jobs = await Job.prisma().find_many()
        
        return render_template("jobs.html.j2", **{'jobs': jobs})

@app.route('/jobs/<job_id>')
async def job(job_id):
    async with get_db():
        job = await Job.prisma().find_unique(
            where={
                'id': job_id 
            },
            include={'company': True, 'resumes': True}
        )

    return render_template("job.html.j2", job=job)


@app.post('/jobs/<job_id>/summarize')
async def summarize(job_id):
    async with get_db():
        job = await Job.summarize(job_id)

    return render_template("job.html.j2", job=job)

@app.post('/jobs/<job_id>/resume')
async def resume(job_id):
    async with get_db():
        job = await Job.generate_resume(job_id, master_resume=get_resume())

    return render_template("job.html.j2", job=job)


@app.route('/jobs/<job_id>/resumes/<resume_id>')
async def show_resume(job_id, resume_id):
    async with get_db():
        resume = await Resume.prisma().find_unique(
            where={'id': resume_id, 'job_id': job_id },
            include={
                'job': {
                    'include': { 
                        'company': True 
                    }
                }
            }
        )

        if not resume:
            return "Resume not found", 404

    return render_template("resume.html.j2", resume=resume)



@app.post('/resume/<resume_id>/cover_letter')
async def cover_letter(resume_id):
    async with get_db():
        resume = await Resume.cover_letter(resume_id)

    return render_template("resume.html.j2", resume=resume)
