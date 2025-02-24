from typing import Optional

from pydantic import BaseModel


class CommonResponse(BaseModel):
    ok: bool
    error: Optional[str]


class UserProfile(BaseModel):
    real_name: str


class UserProfileResponse(CommonResponse):
    profile: UserProfile
