from pydantic import BaseModel, EmailStr


class ValidateEmail(BaseModel):
    email: EmailStr
