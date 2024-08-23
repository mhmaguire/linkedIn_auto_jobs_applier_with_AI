from pathlib import Path
from typing import ClassVar, Dict, List
import yaml
from pydantic import Field

from auto_resume.model.base import BaseModel
from auto_resume.model.render import PdfRenderer
from auto_resume.model.config import Files
from prisma.models import Resume as BaseResume
from auto_resume.agent.cover_letter import CoverLetterFactory

from jinja2 import Template


class Resume(BaseResume):

    cover_letter_factory: ClassVar = CoverLetterFactory()
    

    @classmethod
    async def cover_letter(cls, resume_id):
        resume = await cls.prisma().find_unique(
            where={'id': resume_id },
            include={'job': True}
        )

        cover_letter = cls.cover_letter_factory(job=resume.job, resume=resume)

        return await cls.prisma().update(
            where={'id': resume_id},
            data={'cover_letters': { 'create': {'content': cover_letter}}},
            include={
                    'job': { "include": {"company": True}},
                    'cover_letters': True
                }
            )

    def to_pdf(self):
        return PdfRenderer()(str(self))


class PersonalInformation(BaseModel):
    name: str
    surname: str
    dateOfBirth: str
    country: str
    city: str
    address: str
    phone: str
    phonePrefix: str
    email: str
    github: str
    linkedin: str


class SelfIdentification(BaseModel):
    gender: str
    pronouns: str
    veteran: bool
    disability: bool
    ethnicity: str


class LegalAuthorization(BaseModel):
    euWorkAuthorization: bool
    usWorkAuthorization: bool
    requiresUsVisa: bool
    legallyAllowedToWorkInUs: bool
    requiresUsSponsorship: bool
    requiresEuVisa: bool
    legallyAllowedToWorkInEu: bool
    requiresEuSponsorship: bool


class WorkPreferences(BaseModel):
    remoteWork: bool
    inPersonWork: bool
    openToRelocation: bool
    willingToCompleteAssessments: bool
    willingToUndergoDrugTests: bool
    willingToUndergoBackgroundChecks: bool


class Education(BaseModel):
    degree: str
    university: str
    gpa: str
    graduationYear: str
    fieldOfStudy: str
    skillsAcquired: Dict[str, str]


class Experience(BaseModel):
    position: str
    company: str
    employmentPeriod: str
    location: str
    industry: str
    keyResponsibilities: Dict[str, str]
    skillsAcquired: Dict[str, str]


class Availability(BaseModel):
    noticePeriod: str


class SalaryExpectations(BaseModel):
    salaryRangeUSD: str


class Language(BaseModel):
    language: str
    proficiency: str


class MasterResume(BaseModel):
    personal_information: PersonalInformation = Field(..., title='Personal Information')
    self_identification: SelfIdentification = Field(..., title='Self Identification')
    legal_authorization: LegalAuthorization = Field(..., title='Legal Authorization')
    work_preferences: WorkPreferences = Field(..., title='Work Preferences')
    projects: Dict[str, str] = Field(..., title='Projects')
    availability: Availability = Field(..., title='Availability')
    salary_expectations: SalaryExpectations = Field(..., title='Salary Expectations')
    education_details: List[Education] = Field(..., default_factory=list, title='Education')
    experience_details: List[Experience] = Field(..., default_factory=list, title='Experience')
    certifications: List[str] = Field(..., default_factory=list, title='Certifications')
    languages: List[Language] = Field(..., default_factory=list, title='Languages')
    interests: List[str] = Field(..., default_factory=list, title='Interests')
    skills: Dict[str, str|int] = Field(..., description='Skills')

    template: ClassVar = Path('./templates/master_resume.md.j2')

    @classmethod
    def load(cls, plain_txt_resume: Path = Files.plain_text_resume_file):
        if not plain_txt_resume.exists():
            raise FileNotFoundError

        return cls(**yaml.safe_load(plain_txt_resume.read_text()))

    def __str__(self):
        return Template(self.template.read_text()).render(resume=self)
        
        

    def to_pdf(self):
        return PdfRenderer()(str(self))
