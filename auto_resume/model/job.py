from typing import ClassVar

from langchain_core.documents import Document

from auto_resume.agent.graph import (
    ExtractKnowledge as KnowledgeFactory,
    ExtractSchema as SchemaFactory,
)
from auto_resume.agent.resume import ResumeReviewer as ResumeFactory
from auto_resume.agent.summarize import SummarizeJob as SummaryFactory
from auto_resume.model.indexer import Indexer
from prisma.partials import JobWithCompany as JobBase


class Job(JobBase):
    summary_factory: ClassVar = SummaryFactory()
    resume_factory: ClassVar = ResumeFactory()
    knowledge_factory: ClassVar = KnowledgeFactory()
    schema_factory: ClassVar = SchemaFactory()
    indexer: ClassVar = Indexer("auto_resume_jobs")

    def extract_knowledge(self):
        return self.knowledge_factory([self.info])

    def extract_schema(self):
        return self.schema_factory(self.info)

    def index(self):
        self.indexer([self.to_doc()])

    def summarize(self):
        summary = self.summary_factory(self.info)

        return self.prisma().update(
            where={"id": self.id}, data={"summary": summary}, include={"company": True}
        )

    def generate_resume(self, *, master_resume):
        resume_content = self.resume_factory(resume=master_resume, job=self)

        return self.__class__.prisma().update(
            where={"id": self.id},
            data={"resumes": {"createMany": {"data": [{"content": resume_content}]}}},
            include={"resumes": True, "company": True},
        )

    @classmethod
    def upsert(cls, job_id: str, data: dict):
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

        return cls.prisma().upsert(
            where={"external_id": job_id},
            data={"create": {"external_id": job_id, **payload}, "update": payload},
            include={"company": True},
        )

    def to_doc(self):
        return Document(page_content=self.info, metadata={"source": self.id})

    @property
    def company_name(self):
        company = self.company
        return company.name if company is not None else ""

    @property
    def info(self):
        """
        Formats the job information as a markdown string.
        """

        return f"""
        # Job Description
        ## Job Information 
        - Position: {self.title}
        - At: {self.company_name}

        ## Summary
        {self.summary or 'No summary provided'}
        """.strip()
