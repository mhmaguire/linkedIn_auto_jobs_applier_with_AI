from pathlib import Path
from typing import Dict, List
import yaml
from pydantic import Field

from model.base import BaseModel

from model.render import PdfRenderer


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


class Resume(BaseModel):
    personal_information: PersonalInformation
    self_identification: SelfIdentification
    legal_authorization: LegalAuthorization
    work_preferences: WorkPreferences
    projects: Dict[str, str]
    availability: Availability
    salary_expectations: SalaryExpectations
    education_details: List[Education] = Field(..., default_factory=list)
    experience_details: List[Experience] = Field(..., default_factory=list)
    certifications: List[str] = Field(..., default_factory=list)
    languages: List[Language] = Field(..., default_factory=list)
    interests: List[str] = Field(..., default_factory=list)

    @classmethod
    def load(cls, plain_txt_resume: Path):
        if not plain_txt_resume.exists():
            raise FileNotFoundError

        return cls(**yaml.safe_load(plain_txt_resume.read_text()))

    def __str__(self):
        def format_dict(dict_obj):
            return "\n".join(f"{key}: {value}" for key, value in dict_obj.items())

        def format_model(obj):
            return "\n".join(
                f"{field}: {getattr(obj, field)}" for field in obj.__fields__.keys()
            )

        return (
            "Personal Information:\n" + format_model(self.personal_information) + "\n\n"
            "Self Identification:\n" + format_model(self.self_identification) + "\n\n"
            "Legal Authorization:\n" + format_model(self.legal_authorization) + "\n\n"
            "Work Preferences:\n" + format_model(self.work_preferences) + "\n\n"
            "Education Details:\n"
            + "\n".join(
                f"  - {edu.degree} in {edu.fieldOfStudy} from {edu.university}, "
                f"GPA: {edu.gpa}, Graduation Year: {edu.graduationYear}\n"
                f"    Skills Acquired:\n{format_dict(edu.skillsAcquired)}"
                for edu in self.education_details
            )
            + "\n\n"
            "Experience Details:\n"
            + "\n".join(
                f"  - {exp.position} at {exp.company} ({exp.employmentPeriod}), {exp.location}, {exp.industry}\n"
                f"    Key Responsibilities:\n{format_dict(exp.keyResponsibilities)}\n"
                f"    Skills Acquired:\n{format_dict(exp.skillsAcquired)}"
                for exp in self.experience_details
            )
            + "\n\n"
            "Projects:\n"
            + "\n".join(f"  - {proj}" for proj in self.projects.values())
            + "\n\n"
            f"Availability: {self.availability.noticePeriod}\n\n"
            f"Salary Expectations: {self.salary_expectations.salaryRangeUSD}\n\n"
            "Certifications: " + ", ".join(self.certifications) + "\n\n"
            "Languages:\n"
            + "\n".join(
                f"  - {lang.language} ({lang.proficiency})" for lang in self.languages
            )
            + "\n\n"
            "Interests:\n" + ", ".join(self.interests)
        )

    def to_pdf(self):
        return PdfRenderer()(str(self))
