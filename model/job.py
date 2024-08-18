from typing import ClassVar
from prisma.partials import JobWithCompany as JobBase

from dataclasses import dataclass

from agent.summarize import SummarizeJob

class Job(JobBase):

    summarizer: ClassVar = SummarizeJob()

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
            where={'external_id': job_id},
            data={
                'create': { 'external_id': job_id, **payload },
                'update': payload
            },
            include={'company': True}
        )
        

    async def summarize(self):
        summary = self.summarizer(self.info)

        await self.prisma().update(
            where={'id': self.id},
            data={
                'summary': summary
            }
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
