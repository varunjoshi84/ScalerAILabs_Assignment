import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import get_current_user
from app.models import User, Meeting, Participant, TranscriptSegment, Summary, ActionItem
from app.schemas import MeetingCreate, MeetingResponse, MeetingDetailResponse
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/meetings", tags=["Meetings"])

# Transcript parser helper
def parse_raw_transcript(raw_text: str) -> List[dict]:
    segments = []
    lines = raw_text.strip().split('\n')
    
    # Matches formats like:
    # Speaker Name (01:23): Text...
    # Speaker Name [1:23:45] Text...
    # Speaker Name: Text...
    pattern_with_time = re.compile(r"^([^:(]+?)\s*[\(\[]?(\d{1,2}:\d{2}(?::\d{2})?)[\)\]]?\s*:\s*(.*)$")
    pattern_simple = re.compile(r"^([^:]+?)\s*:\s*(.*)$")
    
    current_time = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = pattern_with_time.match(line)
        if match:
            speaker = match.group(1).strip()
            time_str = match.group(2).strip()
            text = match.group(3).strip()
            
            # Parse timestamp into seconds
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 2:
                current_time = parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                current_time = parts[0] * 3600 + parts[1] * 60 + parts[2]
            
            segments.append({
                "speaker_name": speaker,
                "timestamp_seconds": current_time,
                "text": text
            })
        else:
            match = pattern_simple.match(line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()
                current_time += 5  # Increment slightly
                segments.append({
                    "speaker_name": speaker,
                    "timestamp_seconds": current_time,
                    "text": text
                })
            else:
                if segments:
                    segments[-1]["text"] += " " + line
                else:
                    segments.append({
                        "speaker_name": "Unknown",
                        "timestamp_seconds": current_time,
                        "text": line
                    })
    return segments

# Heuristic helper to generate summary & action items from transcript segments
def generate_mock_analysis(db: Session, meeting_id: int, segments: List[dict]):
    if not segments:
        # Default empty summary
        default_summary = Summary(
            meeting_id=meeting_id,
            overview_text="No transcript was provided to generate a summary.",
            key_topics=["Overview"]
        )
        db.add(default_summary)
        return

    # 1. Generate overview text
    overview = f"In this meeting, {len(set(s['speaker_name'] for s in segments))} speaker(s) discussed key points. "
    if len(segments) > 0:
        # Grab first and last couple of sentences
        snippet = " ".join([s['text'] for s in segments[:2]])
        overview += f"The conversation opened with discussions around: '{snippet[:120]}...'."
    
    # 2. Extract key topics (words that are capitalized or common key nouns)
    topics = ["Discussion", "Collaboration"]
    for s in segments:
        for word in ["project", "timeline", "deadline", "budget", "client", "release", "marketing", "sprint"]:
            if word in s['text'].lower() and word.capitalize() not in topics:
                topics.append(word.capitalize())
    
    summary_obj = Summary(
        meeting_id=meeting_id,
        overview_text=overview,
        key_topics=topics
    )
    db.add(summary_obj)

    # 3. Heuristics for Action Items
    action_keywords = ["action item", "need to", "should", "will do", "task", "assign", "follow up"]
    for s in segments:
        text_lower = s['text'].lower()
        if any(kw in text_lower for kw in action_keywords):
            # Extract sentence containing keyword
            sentences = s['text'].split('.')
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in action_keywords) and len(sentence.strip()) > 8:
                    clean_item = sentence.strip().replace("I will ", "").replace("We need to ", "")
                    # Add item
                    action_obj = ActionItem(
                        meeting_id=meeting_id,
                        text=clean_item,
                        assignee=s['speaker_name'],
                        is_completed=False
                    )
                    db.add(action_obj)
                    break # Extract at most 1 action item per segment to avoid clutter

@router.get("", response_model=List[MeetingResponse])
def list_meetings(
    search: Optional[str] = Query(None, description="Search by meeting title"),
    date_from: Optional[datetime] = Query(None, description="Filter meetings starting from date"),
    date_to: Optional[datetime] = Query(None, description="Filter meetings up to date"),
    participant: Optional[str] = Query(None, description="Filter by participant name"),
    sort: Optional[str] = Query("date_desc", description="Sort by: date_asc, date_desc, title_asc, title_desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Meeting).filter(Meeting.owner_id == current_user.id)

    if search:
        query = query.filter(Meeting.title.ilike(f"%{search}%"))
    
    if date_from:
        query = query.filter(Meeting.date >= date_from)
        
    if date_to:
        query = query.filter(Meeting.date <= date_to)

    if participant:
        query = query.join(Participant).filter(Participant.name.ilike(f"%{participant}%"))

    # Apply sorting
    if sort == "date_asc":
        query = query.order_by(Meeting.date.asc())
    elif sort == "date_desc":
        query = query.order_by(Meeting.date.desc())
    elif sort == "title_asc":
        query = query.order_by(Meeting.title.asc())
    elif sort == "title_desc":
        query = query.order_by(Meeting.title.desc())

    return query.all()

@router.post("", response_model=MeetingDetailResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_in: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Create meeting
    db_meeting = Meeting(
        title=meeting_in.title,
        date=meeting_in.date,
        duration=meeting_in.duration,
        owner_id=current_user.id
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)

    # 2. Add Participants
    for p_name in meeting_in.participants:
        p_obj = Participant(meeting_id=db_meeting.id, name=p_name)
        db.add(p_obj)

    # 3. Add Transcript Segments (either parsed from text or structured input)
    segments_to_process = []
    if meeting_in.transcript_text:
        segments_to_process = parse_raw_transcript(meeting_in.transcript_text)
    elif meeting_in.transcript_segments:
        segments_to_process = [seg.model_dump() for seg in meeting_in.transcript_segments]

    for seg in segments_to_process:
        seg_obj = TranscriptSegment(
            meeting_id=db_meeting.id,
            speaker_name=seg["speaker_name"],
            timestamp_seconds=seg["timestamp_seconds"],
            text=seg["text"]
        )
        db.add(seg_obj)

    db.commit()

    # 4. Auto-generate summary & action items
    generate_mock_analysis(db, db_meeting.id, segments_to_process)
    db.commit()
    db.refresh(db_meeting)

    return db_meeting

@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting_detail(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.owner_id == current_user.id).first()
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    return db_meeting

@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: int,
    meeting_in: MeetingCreate,  # Reuse create validation, ignore transcript items in PUT
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.owner_id == current_user.id).first()
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    db_meeting.title = meeting_in.title
    db_meeting.date = meeting_in.date
    db_meeting.duration = meeting_in.duration
    
    # Update participants list (simple replace logic)
    # Delete old ones
    db.query(Participant).filter(Participant.meeting_id == meeting_id).delete()
    # Add new ones
    for p_name in meeting_in.participants:
        p_obj = Participant(meeting_id=meeting_id, name=p_name)
        db.add(p_obj)

    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.delete("/{meeting_id}", status_code=status.HTTP_200_OK)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.owner_id == current_user.id).first()
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    db.delete(db_meeting)  # SQLAlchemy handles cascade delete for participants, segments, summary, and action items
    db.commit()
    return {"message": "Meeting successfully deleted"}
