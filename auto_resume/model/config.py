import re
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, List, Literal

import yaml
from pydantic import AfterValidator, ConfigDict, Field, create_model, field_serializer
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from auto_resume.model.base import BaseModel


class Files:
    app_data_folder = Path("data_folder")
    output_folder = app_data_folder / "output"
    secrets_file = app_data_folder / "secrets.yaml"
    config_file = app_data_folder / "config.yaml"
    plain_text_resume_file = app_data_folder / "plain_text_resume.yaml"

    @classmethod
    def init(cls):
        cls.app_data_folder.mkdir(exist_ok=True)
        cls.output_folder.mkdir(exist_ok=True)
        cls.validate()

    @classmethod
    def paths(cls):
        return (
            cls.secrets_file,
            cls.config_file,
            cls.plain_text_resume_file,
            cls.output_folder,
        )

    @classmethod
    def dict(cls):
        return {f.name: f for f in [cls.config_file, cls.secrets_file, cls.plain_text_resume_file]}

    @classmethod
    def validate(cls):
        if not cls.app_data_folder.exists():
            raise FileNotFoundError(f"Data folder not found: {cls.app_data_folder}")

        if missing := cls.missing():
            raise FileNotFoundError(f"Missing files in the data folder: {', '.join(missing)}")

    @classmethod
    def missing(cls):
        return [
            f
            for f in [cls.config_file, cls.secrets_file, cls.plain_text_resume_file]
            if not f.exists()
        ]


class EnumModel(BaseModel):
    pass


def enum_model(enum_class):
    return create_model(
        f"{enum_class.__name__}s",
        **{attr: (bool, ...) for attr in iter(enum_class.__members__)},
        __base__=EnumModel
    )


class WorkType(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = str(param)
        return obj

    on_site = ("on_site", 1)
    hybrid = ("hybrid", 2)
    remote = ("remote", 3)


class Date(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = param
        return obj

    all_time = ("all_time", "")
    month = ("month", f"r{24 * 60 * 60 * 7 * 4}")
    week = ("week", f"r{24 * 60 * 60 * 7}")
    day = ("day", f"r{24 * 60 * 60}")


class ExperienceLevel(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = str(param)
        return obj

    internship = ("internship", 1)
    entry = ("entry", 2)
    associate = ("associate", 3)
    mid_senior_level = ("mid-senior level", 4)
    director = ("director", 5)
    executive = ("executive", 6)


class JobType(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = param
        return obj

    full_time = ("full_time", "F")
    part_time = ("part_time", "P")
    contract = ("contract", "C")
    temporary = ("temporary", "T")
    internship = ("internship", "I")
    other = ("other", "O")
    volunteer = ("volunteer", "V")


ExperienceLevels = enum_model(ExperienceLevel)
JobTypes = enum_model(JobType)
WorkTypes = enum_model(WorkType)


class Parameters(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    email: str = Field(
        None,
        title="Email",
        description="The email address to use for job applications."
    )
    work_types: WorkTypes = Field(
        ...,
        title="Work Types",
        description="The types of work to search for (e.g. full-time, part-time, contract)."
    )
    experience_level: ExperienceLevels = Field(
        ...,
        title="Experience Level",
        description="The desired level of experience for the job search."
    )
    job_types: JobTypes = Field(
        ...,
        title="Job Types",
        description="The types of jobs to search for (e.g. full-time, part-time, contract)."
    )
    date: Date = Field(
        ...,
        title="Date Range",
        description="The date range to search for job postings."
    )
    distance: Literal[0, 5, 10, 25, 50, 100] = Field(
        ...,
        title="Distance",
        description="The maximum distance (in miles) to search for jobs."
    )
    positions: List[str] = Field(
        ...,
        title="Positions",
        description="The job titles or positions to search for."
    )
    locations: List[str] = Field(
        ...,
        title="Locations",
        description="The locations to search for jobs in."
    )
    company_blacklist: List[str] = Field(
        ...,
        default_factory=list,
        title="Company Blacklist",
        description="A list of companies to exclude from the job search."
    )
    title_blacklist: List[str] = Field(
        ...,
        default_factory=list,
        title="Title Blacklist",
        description="A list of job titles to exclude from the job search."
    )

    output_file_directory: ClassVar = str(Files.output_folder)


    @field_serializer('date')
    def serialize_date(self, date):
        return date.value

    @classmethod
    def load(cls, path: Path = Files.config_file):
        return cls(**yaml.unsafe_load(path.read_text()))

    @classmethod
    def update(cls, attributes):
        model = cls.model_validate(attributes)
        Files.config_file.write_text(yaml.dump(model.model_dump()))


def valid_email(v: str) -> str:
    assert re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v), "Invalid Email"
    return v


Email = Annotated[str, AfterValidator(valid_email)]


class Secrets(BaseModel):
    email: Email
    password: str
    openai_api_key: str

    @classmethod
    def load(cls, path: Path = Files.secrets_file):
        return cls(**yaml.load(path.read_text(), yaml.FullLoader))


class Config(BaseModel):
    secrets: Secrets
    parameters: Parameters

    @classmethod
    def load(cls):
        return cls(secrets=Secrets.load(), parameters=Parameters.load())
