import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def clean(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be blank")
    return value


class ContentPillar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)

    @field_validator("name", "description")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        return clean(value)


class NicheDNAInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    niche_name: str = Field(min_length=1, max_length=120)
    niche_description: str = Field(min_length=1, max_length=2000)
    target_audience: str = Field(min_length=1, max_length=500)
    language: str = Field(
        min_length=2, max_length=35, pattern=r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$"
    )
    tone: str = Field(min_length=1, max_length=500)
    content_pillars: list[ContentPillar] = Field(min_length=1, max_length=20)
    forbidden_topics: list[str] = Field(default_factory=list, max_length=50)
    trend_transformation_guidance: str = Field(default="", max_length=2000)
    change_note: str = Field(min_length=1, max_length=500)

    @field_validator("niche_name", "niche_description", "target_audience", "tone", "change_note")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return clean(value)

    @field_validator("trend_transformation_guidance")
    @classmethod
    def strip_optional(cls, value: str) -> str:
        return value.strip()

    @field_validator("forbidden_topics")
    @classmethod
    def validate_topics(cls, values: list[str]) -> list[str]:
        result = [clean(value) for value in values]
        if len({value.casefold() for value in result}) != len(result):
            raise ValueError("forbidden topics must be unique")
        if any(len(value) > 120 for value in result):
            raise ValueError("forbidden topic exceeds 120 characters")
        return result

    @model_validator(mode="after")
    def unique_pillars(self) -> "NicheDNAInput":
        names = [pillar.name.casefold() for pillar in self.content_pillars]
        if len(names) != len(set(names)):
            raise ValueError("content pillars must be unique")
        return self


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=120)
    platform: str = "instagram"
    platform_handle: str | None = Field(default=None, max_length=60)
    niche_dna: NicheDNAInput

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str) -> str:
        return clean(value)

    @field_validator("platform")
    @classmethod
    def instagram_only(cls, value: str) -> str:
        if value != "instagram":
            raise ValueError("only instagram is supported")
        return value

    @field_validator("platform_handle")
    @classmethod
    def normalize_handle(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = clean(value.removeprefix("@")).lower()
        if not value.replace(".", "").replace("_", "").isalnum():
            raise ValueError("invalid handle")
        return value


class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    platform_handle: str | None = Field(default=None, max_length=60)

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str | None) -> str | None:
        return clean(value) if value is not None else None

    @field_validator("platform_handle")
    @classmethod
    def normalize_handle(cls, value: str | None) -> str | None:
        return AccountCreate.normalize_handle(value)


class NicheDNARevisionCreate(NicheDNAInput):
    expected_active_revision_number: int = Field(ge=1)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    platform: str
    platform_handle: str | None
    paused: bool
    active_niche_revision_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime


class NicheDNARevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    revision_number: int
    niche_name: str
    niche_description: str
    target_audience: str
    language: str
    tone: str
    content_pillars: list[ContentPillar]
    forbidden_topics: list[str]
    trend_transformation_guidance: str
    created_at: datetime
    actor: str
    change_note: str


class AccountChangeEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    actor: str
    action: str
    occurred_at: datetime
    request_id: uuid.UUID
    summary: str
    old_revision_id: uuid.UUID | None
    new_revision_id: uuid.UUID | None


class EventPage(BaseModel):
    items: list[AccountChangeEventResponse]
    next_cursor: str | None
