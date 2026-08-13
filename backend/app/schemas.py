from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any

# ==========================================
# Auth & User Schemas
# ==========================================
class UserBase(BaseModel):
    email: str = Field(..., description="The user's email address")
    name: str = Field(..., description="The user's full name")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Minimum 6 characters password")

class UserLogin(BaseModel):
    email: str = Field(..., description="The user's email address")
    password: str = Field(..., description="The user's password")

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

# ==========================================
# Participant Schemas
# ==========================================
class ParticipantResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# ==========================================
# Transcript Segment Schemas
# ==========================================
class TranscriptSegmentCreate(BaseModel):
    speaker_name: str = Field(..., description="Speaker name")
    timestamp_seconds: int = Field(..., description="Timestamp of the segment in seconds")
    text: str = Field(..., description="Transcription text")

class TranscriptSegmentResponse(TranscriptSegmentCreate):
    id: int
    meeting_id: int
    is_highlighted: bool
    comment: Optional[str] = None

    class Config:
        from_attributes = True

class TranscriptSegmentUpdate(BaseModel):
    is_highlighted: Optional[bool] = None
    comment: Optional[str] = None

class TranscriptSearchResponse(BaseModel):
    meeting_id: int
    matching_segments: List[TranscriptSegmentResponse]

# ==========================================
# Summary Schemas
# ==========================================
class SummaryResponse(BaseModel):
    id: int
    overview_text: str
    key_topics: Optional[List[str]] = None

    class Config:
        from_attributes = True

# ==========================================
# Action Item Schemas
# ==========================================
class ActionItemCreate(BaseModel):
    text: str = Field(..., description="Description of the action item")
    assignee: Optional[str] = Field(None, description="Assigned participant name")

class ActionItemUpdate(BaseModel):
    text: Optional[str] = None
    assignee: Optional[str] = None
    is_completed: Optional[bool] = None

class ActionItemResponse(ActionItemCreate):
    id: int
    meeting_id: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# Meeting Schemas
# ==========================================
class MeetingCreate(BaseModel):
    title: str = Field(..., description="Title of the meeting")
    date: datetime = Field(..., description="Date and time of the meeting")
    duration: int = Field(..., description="Duration in seconds")
    participants: List[str] = Field(default=[], description="List of participant names")
    transcript_text: Optional[str] = Field(
        None, 
        description="Raw pasted transcript text. Will be auto-parsed into segments if provided."
    )
    transcript_segments: Optional[List[TranscriptSegmentCreate]] = Field(
        None, 
        description="Structured transcript segments with speakers and timestamps."
    )

class MeetingResponse(BaseModel):
    id: int
    title: str
    date: datetime
    duration: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    participants: List[ParticipantResponse]

    class Config:
        from_attributes = True

class MeetingDetailResponse(MeetingResponse):
    transcript_segments: List[TranscriptSegmentResponse]
    summary: Optional[SummaryResponse] = None
    action_items: List[ActionItemResponse]

    class Config:
        from_attributes = True
