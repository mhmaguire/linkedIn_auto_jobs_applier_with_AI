from pathlib import Path
from typing import ClassVar, Dict, List

import yaml
from jinja2 import Template
from pydantic import Field

from auto_resume.agent.cover_letter import CoverLetterFactory
from auto_resume.model.base import BaseModel
from auto_resume.model.config import Files
from auto_resume.model.render import PdfRenderer
from prisma.models import CoverLetter as BaseCoverLetter
from prisma.models import Resume as BaseResume

from langchain_core.documents import Document


class CoverLetter(BaseCoverLetter):
    pass


class Resume(BaseResume):
    cover_letter_factory: ClassVar = CoverLetterFactory()
    render_pdf: ClassVar = PdfRenderer()

    def cover_letter(self):
        cover_letter = self.cover_letter_factory(job=self.job, resume=self)

        return self.prisma().update(
            where={"id": self.id},
            data={"cover_letters": {"create": {"content": cover_letter}}},
            include={"job": {"include": {"company": True}}, "cover_letters": True},
        )

    def to_pdf(self):
        return self.render_pdf(str(self.content))


class PersonalInformation(BaseModel):
    name: str = Field(..., title="First Name", description="Your first name.")
    surname: str = Field(..., title="Last Name", description="Your last name.")
    date_of_birth: str = Field(
        ..., title="Date of Birth", description="Your date of birth in YYYY-MM-DD format."
    )
    country: str = Field(
        ..., title="Country of Residence", description="Your country of residence."
    )
    city: str = Field(..., title="City of Residence", description="Your city of residence.")
    address: str = Field(
        ..., title="Street Address", description="Your street address of residence."
    )
    phone: str = Field(
        ..., title="Phone Number", description="Your phone number without country code."
    )
    phone_prefix: str = Field(
        ..., title="Phone Prefix", description="Your country code for phone number."
    )
    email: str = Field(..., title="Email Address", description="Your email address.")
    github: str = Field(..., title="GitHub Username", description="Your GitHub username.")
    linkedin: str = Field(..., title="LinkedIn Profile", description="Your LinkedIn profile URL.")


class SelfIdentification(BaseModel):
    gender: str = Field(..., title="Gender Identity", description="Your gender identity.")
    pronouns: str = Field(..., title="Preferred Pronouns", description="Your preferred pronouns.")
    veteran: bool = Field(
        ..., title="Military Veteran", description="Whether you are a military veteran."
    )
    disability: bool = Field(
        ..., title="Disability Status", description="Whether you have a disability."
    )
    ethnicity: str = Field(..., title="Ethnic Background", description="Your ethnic background.")


class LegalAuthorization(BaseModel):
    eu_work_authorization: bool = Field(
        ...,
        title="EU Work Authorization",
        description="Whether you are authorized to work in the EU.",
    )
    us_work_authorization: bool = Field(
        ...,
        title="US Work Authorization",
        description="Whether you are authorized to work in the US.",
    )
    requires_us_visa: bool = Field(
        ..., title="Requires US Visa", description="Whether you require a US visa to work."
    )
    legally_allowed_to_work_in_us: bool = Field(
        ...,
        title="Legally Allowed to Work in US",
        description="Whether you are legally allowed to work in the US.",
    )
    requires_us_sponsorship: bool = Field(
        ...,
        title="Requires US Sponsorship",
        description="Whether you require US sponsorship to work.",
    )
    requires_eu_visa: bool = Field(
        ..., title="Requires EU Visa", description="Whether you require an EU visa to work."
    )
    legally_allowed_to_work_in_eu: bool = Field(
        ...,
        title="Legally Allowed to Work in EU",
        description="Whether you are legally allowed to work in the EU.",
    )
    requires_eu_sponsorship: bool = Field(
        ...,
        title="Requires EU Sponsorship",
        description="Whether you require EU sponsorship to work.",
    )


class WorkPreferences(BaseModel):
    remote_work: bool = Field(
        ..., title="Open to Remote Work", description="Whether you are open to remote work."
    )
    in_person_work: bool = Field(
        ..., title="Open to In-Person Work", description="Whether you are open to in-person work."
    )
    open_to_relocation: bool = Field(
        ..., title="Open to Relocation", description="Whether you are open to relocating for a job."
    )
    willing_to_complete_assessments: bool = Field(
        ...,
        title="Willing to Complete Assessments",
        description="Whether you are willing to complete job assessments.",
    )
    willing_to_undergo_drug_tests: bool = Field(
        ...,
        title="Willing to Undergo Drug Tests",
        description="Whether you are willing to undergo drug tests.",
    )
    willing_to_undergo_background_checks: bool = Field(
        ...,
        title="Willing to Undergo Background Checks",
        description="Whether you are willing to undergo background checks.",
    )


class Education(BaseModel):
    degree: str = Field(
        ..., title="Degree Obtained", description="Degree you obtained (e.g. Bachelor's, Master's)."
    )
    university: str = Field(
        ..., title="University Attended", description="Name of the university you attended."
    )
    gpa: str = Field(
        ...,
        title="Grade Point Average (GPA)",
        description="Grade point average (GPA) you achieved.",
    )
    graduation_year: str = Field(..., title="Graduation Year", description="Year you graduated.")
    field_of_study: str = Field(
        ..., title="Field of Study", description="Your field of study or major."
    )
    skills_acquired: Dict[str, str] = Field(
        ..., title="Skills Acquired", description="Skills you acquired during the degree program."
    )


class Experience(BaseModel):
    position: str = Field(..., title="Position Held", description="Job title or position you held.")
    company: str = Field(
        ..., title="Company Name", description="Name of the company you worked for."
    )
    employment_period: str = Field(
        ...,
        title="Employment Period",
        description="Duration of your employment (e.g. Jan 2020 - Present).",
    )
    location: str = Field(
        ...,
        title="Job Location",
        description="Location of the job (city, state/province, country).",
    )
    industry: str = Field(..., title="Industry", description="Industry the company operates in.")
    key_responsibilities: Dict[str, str] = Field(
        ...,
        title="Key Responsibilities",
        description="Your key responsibilities and achievements in the role.",
    )
    skills_acquired: Dict[str, str] = Field(
        ..., title="Skills Acquired", description="Skills you acquired during the employment."
    )


class Availability(BaseModel):
    notice_period: str = Field(
        ...,
        title="Notice Period",
        description="Notice period required before you can start a new job.",
    )


class SalaryExpectations(BaseModel):
    salary_range_usd: str = Field(
        ...,
        title="Expected Salary Range (USD)",
        description="Your expected salary range in US dollars.",
    )


class Language(BaseModel):
    language: str = Field(..., title="Language Name", description="Name of the language.")
    proficiency: str = Field(
        ..., title="Language Proficiency", description="Your proficiency level in the language."
    )


class Project(BaseModel):
    name: str = Field(..., title="Project Name", description="Name of the project.")
    description: str = Field(
        ..., title="Project Description", description="Description of the project."
    )


class Skill(BaseModel):
    name: str = Field(..., title="Skill Name", description="Name of the skill.")
    level: int = Field(
        ..., title="Years of Experience", description="Your years of experience with the skill."
    )


class Interest(BaseModel):
    name: str = Field(..., title="Name")
    description: str | None = Field(None, title="Description")


class Certification(BaseModel):
    name: str = Field(..., title="Certification Name", description="Name of the certification.")
    issuer: str = Field(
        ...,
        title="Issuing Authority",
        description="The organization that issued the certification.",
    )
    description: str = Field(
        ..., title="Certification Description", description="Description of the certification."
    )
    date_obtained: str = Field(
        ..., title="Date Obtained", description="The date when the certification was obtained."
    )


class MasterResume(BaseModel):
    personal_information: PersonalInformation = Field(
        ..., title="Personal Information", description="Your personal details."
    )
    self_identification: SelfIdentification = Field(
        ..., title="Self Identification", description="Your self-identification details."
    )
    legal_authorization: LegalAuthorization = Field(
        ..., title="Legal Authorization", description="Your legal authorization details for work."
    )
    work_preferences: WorkPreferences = Field(
        ..., title="Work Preferences", description="Your preferences related to work arrangements."
    )
    salary_expectations: SalaryExpectations = Field(
        ..., title="Salary Expectations", description="Your expected salary range."
    )
    availability: Availability = Field(
        ..., title="Availability", description="Your availability details for starting a new job."
    )
    projects: List[Project] = Field(
        ..., title="Projects", description="List of projects you have undertaken."
    )
    education_details: List[Education] = Field(
        ...,
        default_factory=list,
        title="Education",
        description="List of your educational qualifications.",
    )
    experience_details: List[Experience] = Field(
        ...,
        default_factory=list,
        title="Experience",
        description="List of your professional experiences.",
    )
    certifications: List[Certification] = Field(
        ...,
        default_factory=list,
        title="Certifications",
        description="List of certifications you have obtained.",
    )
    languages: List[Language] = Field(
        ...,
        default_factory=list,
        title="Languages",
        description="List of languages you know and your proficiency levels.",
    )
    interests: List[Interest] = Field(
        ...,
        default_factory=list,
        title="Interests",
        description="List of your personal interests and hobbies.",
    )
    skills: List[Skill] = Field(
        ..., title="Skills", description="List of your skills and corresponding experience levels."
    )

    template: ClassVar = Path("./auto_resume/templates/master_resume.md.j2")

    @classmethod
    def load(cls, plain_txt_resume: Path = Files.plain_text_resume_file):
        if not plain_txt_resume.exists():
            raise FileNotFoundError

        return cls(**yaml.safe_load(plain_txt_resume.read_text()))


    @classmethod
    def update(cls, data, plain_txt_resume: Path = Files.plain_text_resume_file):

        model = cls.model_validate(data)
        plain_txt_resume.write_text(yaml.safe_dump(model.model_dump()))

    def __str__(self):
        return Template(self.template.read_text()).render(resume=self)

    def to_pdf(self):
        return PdfRenderer()(str(self))

    def to_doc(self):
        return Document(page_content=str(self))
