from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import get_current_user
from app.models import User, Meeting, ActionItem
from app.schemas import ActionItemCreate, ActionItemUpdate, ActionItemResponse

router = APIRouter(tags=["Action Items"])

@router.post("/meetings/{meeting_id}/action-items", response_model=ActionItemResponse, status_code=status.HTTP_201_CREATED)
def create_action_item(
    meeting_id: int,
    action_in: ActionItemCreate,
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

    # 2. Create action item
    db_action = ActionItem(
        meeting_id=meeting_id,
        text=action_in.text,
        assignee=action_in.assignee,
        is_completed=False
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action

@router.put("/action-items/{action_item_id}", response_model=ActionItemResponse)
def update_action_item(
    action_item_id: int,
    action_in: ActionItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch action item joining with Meeting to check ownership
    db_action = db.query(ActionItem).join(Meeting).filter(
        ActionItem.id == action_item_id,
        Meeting.owner_id == current_user.id
    ).first()
    
    if not db_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )

    # 2. Update fields if provided
    if action_in.text is not None:
        db_action.text = action_in.text
    if action_in.assignee is not None:
        db_action.assignee = action_in.assignee
    if action_in.is_completed is not None:
        db_action.is_completed = action_in.is_completed

    db.commit()
    db.refresh(db_action)
    return db_action

@router.delete("/action-items/{action_item_id}", status_code=status.HTTP_200_OK)
def delete_action_item(
    action_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch action item joining with Meeting to check ownership
    db_action = db.query(ActionItem).join(Meeting).filter(
        ActionItem.id == action_item_id,
        Meeting.owner_id == current_user.id
    ).first()
    
    if not db_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )

    # 2. Delete action item
    db.delete(db_action)
    db.commit()
    return {"message": "Action item successfully deleted"}
