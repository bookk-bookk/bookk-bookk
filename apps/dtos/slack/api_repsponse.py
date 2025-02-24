from typing import Optional

from pydantic import BaseModel


class CommonResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class UserProfile(BaseModel):
    real_name: str


class UserProfileResponse(CommonResponse):
    profile: UserProfile
