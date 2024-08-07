from fastapi import Depends, HTTPException, status, APIRouter, Query
import database, models
from sqlmodel import Session, select, desc
import OAuth2
# from sqlalchemy import desc

router = APIRouter(
    tags=['Notification']
)

@router.get('/notifications')
def get_notifications(
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Member","Librarian"])),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(10, le=100, description="Maximum number of notifications to return")
):
    user = db.exec(select(models.User).where(models.User.email == token_data.email)).first()
    
    
    statement = (select(models.Notification)
                 .where(models.Notification.user_id == user.id)
                 .order_by(desc(models.Notification.created_at))  # Order by created_at in descending order
                 .offset(skip)
                 .limit(limit))
    notifications = db.exec(statement).all()
    
    return notifications

@router.put('/notifications/{notification_id}/read')
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(database.get_db),
    token_data: models.TokenData = Depends(OAuth2.role_required(["Member","Librarian"]))
):
    notification = db.exec(select(models.Notification).where(models.Notification.id == notification_id)).first()
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    
    if notification.user_id != db.exec(select(models.User).where(models.User.email == token_data.email)).first().id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this notification.")
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    
    return {"message": "Notification marked as read."}
