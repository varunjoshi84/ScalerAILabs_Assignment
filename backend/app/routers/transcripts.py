from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import get_current_user
from app.models import User, Meeting, TranscriptSegment
from app.schemas import TranscriptSearchResponse
from typing import List

router = APIRouter(prefix="/meetings", tags=["Transcripts"])

@router.get("/{meeting_id}/transcript/search", response_model=TranscriptSearchResponse)
def search_transcript(
    meeting_id: int,
    q: str = Query(..., min_length=1, description="The search term to find in transcript segments"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify meeting exists and belongs to current user
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.owner_id == current_user.id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    # 2. Query transcript segments that match the query
    matching_segments = db.query(TranscriptSegment).filter(
        TranscriptSegment.meeting_id == meeting_id,
        TranscriptSegment.text.ilike(f"%{q}%")
    ).order_by(TranscriptSegment.timestamp_seconds.asc()).all()

    return {
        "meeting_id": meeting_id,
        "matching_segments": matching_segments
    }
