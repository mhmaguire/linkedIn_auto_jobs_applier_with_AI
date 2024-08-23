from pathlib import Path
from enum import Enum, IntEnum, StrEnum, auto
from typing import List, Literal
from typing_extensions import Annotated
import re

from pydantic import BaseModel, ConfigDict, AfterValidator, Field, create_model
from pydantic.alias_generators import to_camel
import yaml


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
        return {
            f.name: f
            for f in [cls.config_file, cls.secrets_file, cls.plain_text_resume_file]
        }

    @classmethod
    def validate(cls):
        if not cls.app_data_folder.exists():
            raise FileNotFoundError(f"Data folder not found: {cls.app_data_folder}")

        if missing := cls.missing():
            raise FileNotFoundError(
                f"Missing files in the data folder: {', '.join(missing)}"
            )

    @classmethod
    def missing(cls):
        return [
            f
            for f in [cls.config_file, cls.secrets_file, cls.plain_text_resume_file]
            if not f.exists()
        ]


def enum_model(enum_class):
    return create_model(
        f"{enum_class.__name__}s",
        **{attr: (bool, ...) for attr in iter(enum_class.__members__)},
    )

class WorkType(StrEnum):

    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = str(param)
        return obj
    
    on_site = ('on_site', 1)
    hybrid = ('hybrid', 2)
    remote = ('remote', 3)
    


class Date(StrEnum):

    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = param
        return obj
    
    all_time = ('all_time', '')
    month = ('month', f'r{24 * 60 * 60 * 7 * 4}')
    week = ('week', f'r{24 * 60 * 60 * 7}')
    day = ('day', f'r{24 * 60 * 60}')


class ExperienceLevel(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = str(param)
        return obj
    
    internship = ('internship', 1)
    entry = ('entry', 2)
    associate = ('associate', 3)
    mid_senior_level = ('mid-senior level', 4)
    director = ('director', 5)
    executive = ('executive', 6)


class JobType(StrEnum):
    def __new__(cls, value, param):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.param = param
        return obj
    
    full_time = ('full_time', "F")
    part_time = ('part_time', "P")
    contract = ('contract', "C")
    temporary = ('temporary', "T")
    internship = ('internship', "I")
    other = ('other', 'O')
    volunteer = ('volunteer', 'V')


ExperienceLevels = enum_model(ExperienceLevel)
JobTypes = enum_model(JobType)
WorkTypes = enum_model(WorkType)

class Parameters(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    
    output_file_directory: str = str(Files.output_folder)
    email: str = None
    work_types: WorkTypes
    experience_level: ExperienceLevels
    job_types: JobTypes
    date: Date
    distance: Literal[0, 5, 10, 25, 50, 100]
    positions: List[str]
    locations: List[str]
    company_blacklist: List[str] | None = Field(..., default_factory=list)
    title_blacklist: List[str] | None = Field(..., default_factory=list)

    

    @classmethod
    def load(cls, path: Path = Files.config_file):
        return cls(**yaml.load(path.read_text(), yaml.FullLoader))


def valid_email(v: str) -> str:
    assert re.match(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v
    ), "Invalid Email"
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
