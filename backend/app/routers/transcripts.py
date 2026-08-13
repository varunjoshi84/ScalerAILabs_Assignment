from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import get_current_user
from app.models import User, Meeting, TranscriptSegment
from app.schemas import TranscriptSearchResponse, TranscriptSegmentResponse, TranscriptSegmentUpdate
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

@router.put("/transcript-segments/{segment_id}", response_model=TranscriptSegmentResponse, tags=["Transcripts"])
def update_transcript_segment(
    segment_id: int,
    segment_in: TranscriptSegmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch segment joining with Meeting to check ownership
    db_segment = db.query(TranscriptSegment).join(Meeting).filter(
        TranscriptSegment.id == segment_id,
        Meeting.owner_id == current_user.id
    ).first()
    
    if not db_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript segment not found"
        )
        
    if segment_in.is_highlighted is not None:
        db_segment.is_highlighted = segment_in.is_highlighted
    if segment_in.comment is not None:
        # Allow clearing comments with empty strings or None
        db_segment.comment = segment_in.comment
        
    db.commit()
    db.refresh(db_segment)
    return db_segment
