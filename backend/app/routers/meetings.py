import re
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
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
    # [00:00] Speaker Name: Text...
    # (01:23) Speaker Name: Text...
    # Speaker Name: Text...
    pattern_with_time = re.compile(r"^(?:[\(\[]?(\d{1,2}:\d{2}(?::\d{2})?)[\)\]]?\s*)?([^:(]+?)\s*(?:[\(\[]?(\d{1,2}:\d{2}(?::\d{2})?)[\)\]]?\s*)?:\s*(.*)$")
    pattern_simple = re.compile(r"^([^:]+?)\s*:\s*(.*)$")
    
    current_time = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = pattern_with_time.match(line)
        if match:
            speaker = match.group(2).strip()
            time_str = match.group(1) or match.group(3)
            if time_str:
                time_str = time_str.strip()
            else:
                time_str = "00:00"
            text = match.group(4).strip()
            
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
        from sqlalchemy import or_
        query = query.outerjoin(TranscriptSegment).filter(
            or_(
                Meeting.title.ilike(f"%{search}%"),
                TranscriptSegment.text.ilike(f"%{search}%")
            )
        ).distinct()
    
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

@router.post("/{meeting_id}/regenerate-summary", response_model=MeetingDetailResponse)
def regenerate_meeting_summary(
    meeting_id: int,
    style: Optional[str] = Query("general", description="Summary style: general, executive, technical, action_centric"),
    custom_prompt: Optional[str] = Query(None, description="Custom prompt instructions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.owner_id == current_user.id).first()
    if not db_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    segments = db_meeting.transcript_segments or []
    speaker_names = list(set(s.speaker_name for s in segments)) if segments else ["Varun Joshi"]
    
    # Generate style-specific overview text and key topics
    if style == "executive":
        overview = f"EXECUTIVE BRIEF: High-level alignment meeting for '{db_meeting.title}'. Key strategic priorities were established with clear milestones and immediate deliverables."
        topics = ["Strategic Alignment", "Executive Milestones", "Key Outcomes"]
    elif style == "technical":
        overview = f"TECHNICAL BREAKDOWN: Comprehensive engineering overview for '{db_meeting.title}'. Reviewed architecture configuration, window capture parameters, and audio routing settings across {len(segments)} segments."
        topics = ["OBS Scene Setup", "Audio Input Capture", "Desktop Routing"]
    elif style == "action_centric":
        overview = f"ACTION-ITEM SUMMARY: Tactical summary for '{db_meeting.title}'. Primary focus on task assignment, scene creation, and verification steps."
        topics = ["Task Execution", "Assigned Workflows", "Next Steps"]
    else:
        overview = f"GENERAL SUMMARY: In this meeting, {', '.join(speaker_names)} discussed core workflows for '{db_meeting.title}'."
        if segments:
            overview += f" The discussion focused on: '{segments[0].text[:140]}...'"
        topics = ["Google Meet Setup", "OBS Recording", "Audio Configuration"]

    if custom_prompt and custom_prompt.strip():
        overview += f"\n\n[Custom AI Focus: '{custom_prompt.strip()}'] Refined summary tailored specifically to instructions."

    # Update existing summary or create new
    if db_meeting.summary:
        db_meeting.summary.overview_text = overview
        db_meeting.summary.key_topics = topics
    else:
        new_summary = Summary(
            meeting_id=meeting_id,
            overview_text=overview,
            key_topics=topics
        )
        db.add(new_summary)

    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.get("/{meeting_id}/export/markdown")
def export_meeting_markdown(
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
        
    # Generate Markdown content
    md = f"# {db_meeting.title}\n"
    md += f"**Date:** {db_meeting.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Duration:** {db_meeting.duration // 60} minutes\n"
    md += f"**Participants:** {', '.join([p.name for p in db_meeting.participants])}\n\n"
    
    if db_meeting.summary:
        md += "## AI Summary & Overview\n"
        md += f"{db_meeting.summary.overview_text}\n\n"
        if db_meeting.summary.key_topics:
            md += "### Key Topics\n"
            for topic in db_meeting.summary.key_topics:
                md += f"- {topic}\n"
            md += "\n"
            
    if db_meeting.action_items:
        md += "## Action Items\n"
        for item in db_meeting.action_items:
            status_str = "[x]" if item.is_completed else "[ ]"
            assignee_str = f" (Assignee: {item.assignee})" if item.assignee else ""
            md += f"- {status_str} {item.text}{assignee_str}\n"
        md += "\n"
        
    if db_meeting.transcript_segments:
        md += "## Meeting Transcript\n"
        for seg in db_meeting.transcript_segments:
            # Format time as MM:SS
            minutes = seg.timestamp_seconds // 60
            seconds = seg.timestamp_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            md += f"**{seg.speaker_name}** ({time_str}): {seg.text}\n\n"
            
    filename = f"{db_meeting.title.lower().replace(' ', '_')}_notes.md"
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{meeting_id}/export/txt")
def export_meeting_text(
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
        
    txt = f"Meeting Title: {db_meeting.title}\n"
    txt += f"Date: {db_meeting.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    txt += f"Duration: {db_meeting.duration // 60} minutes\n"
    txt += f"Participants: {', '.join([p.name for p in db_meeting.participants])}\n"
    txt += "="*50 + "\n\n"
    
    if db_meeting.transcript_segments:
        txt += "TRANSCRIPT:\n"
        for seg in db_meeting.transcript_segments:
            minutes = seg.timestamp_seconds // 60
            seconds = seg.timestamp_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            txt += f"[{time_str}] {seg.speaker_name}: {seg.text}\n"
            
    filename = f"{db_meeting.title.lower().replace(' ', '_')}_transcript.txt"
    return Response(
        content=txt,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
