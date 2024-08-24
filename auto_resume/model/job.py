from typing import ClassVar

from auto_resume.agent.resume import ResumeReviewer as ResumeFactory
from auto_resume.agent.summarize import SummarizeJob as SummaryFactory
from prisma.partials import JobWithCompany as JobBase


class Job(JobBase):
    summary_factory: ClassVar = SummaryFactory()
    resume_factory: ClassVar = ResumeFactory()

    async def summarize(self):
        summary = self.summary_factory(self.info)

        await self.prisma().update(
            where={"id": self.id}, data={"summary": summary}, include={"company": True}
        )

    @classmethod
    async def generate_resume(cls, job_id, *, master_resume):
        job = await cls.prisma().find_unique(
            where={"id": job_id},
            include={"resumes": {"orderBy": {"created_at": "desc"}}},
        )

        resume_content = cls.resume_factory(resume=master_resume, job=job)

        await cls.prisma().update(
            where={ "id": job_id },
            data={"resumes": {"create": [{"content": resume_content}]}},
            include={
                'resumes': True,
                'company': True
            }
        )

    @classmethod
    async def upsert(cls, job_id: str, data: dict):
        poster = data.get("poster")
        company = data.get("company")
        payload = {
            "title": data.get("title"),
            "description": data.get("description"),
            "link": data.get("link"),
        }

        if company:
            payload["company"] = {
                "connectOrCreate": {
                    "where": {"name": company.get("name")},
                    "create": company,
                }
            }

        if poster:
            payload["poster"] = {
                "connectOrCreate": {
                    "where": {"link": poster.get("link")},
                    "create": poster,
                }
            }

        return await cls.prisma().upsert(
            where={"external_id": job_id},
            data={"create": {"external_id": job_id, **payload}, "update": payload},
            include={"company": True},
        )

    @property
    def info(self):
        """
        Formats the job information as a markdown string.
        """

        return f"""
        # Job Description
        ## Job Information 
        - Position: {self.title}
        - At: {self.company.name}
        
        ## Description
        {self.description or 'No description provided.'}
        """.strip()
