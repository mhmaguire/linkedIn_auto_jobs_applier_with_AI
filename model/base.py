from pydantic import BaseModel as _BaseModel, field_validator

class BaseModel(_BaseModel):

    @field_validator("*", mode="before")
    @classmethod
    def not_none(cls, v, val_info):
        """
        Convert None to Default on optional fields.
        Why doesn't Pydantic have this option?
        """
        field = cls.model_fields[val_info.field_name]
        if v is None and (default := field.get_default(call_default_factory=True)) is not None:
            return default
        return v