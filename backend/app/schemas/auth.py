from pydantic import BaseModel, Field, field_validator


class PasswordSignup(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return email


class PasswordLogin(BaseModel):
    identifier: str = Field(min_length=2, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class AdminLogin(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=1, max_length=128)
