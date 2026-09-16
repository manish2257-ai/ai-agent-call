from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import User, KnowledgeBaseItem
from ..schemas.schemas import KnowledgeItemCreate, KnowledgeItemResponse
from .deps import get_db, get_current_user

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

@router.get("", response_model=List[KnowledgeItemResponse])
def get_knowledge_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.user_id == current_user.id).all()
    if not items:
        defaults = [
            KnowledgeBaseItem(user_id=current_user.id, category="Working Hours", title="General Business Hours", content="Monday through Friday from 9:00 AM to 6:00 PM IST. Closed on Sunday."),
            KnowledgeBaseItem(user_id=current_user.id, category="Services", title="Core Engineering Offerings", content="Full stack web & mobile applications, AI voice automation systems, backend microservices, and database tuning."),
            KnowledgeBaseItem(user_id=current_user.id, category="Appointments", title="Consultation Booking Policy", content="Meetings can be scheduled with 24 hours prior notice via calendar invite or email."),
            KnowledgeBaseItem(user_id=current_user.id, category="Emergency", title="Medical & Life Safety Protocol", content="The AI assistant cannot handle active life-threatening emergencies. Callers are directed to contact 112/911 directly.")
        ]
        db.add_all(defaults)
        db.commit()
        items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.user_id == current_user.id).all()
    return items

@router.post("", response_model=KnowledgeItemResponse)
def add_knowledge_item(item_in: KnowledgeItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = KnowledgeBaseItem(
        user_id=current_user.id,
        title=item_in.title,
        category=item_in.category,
        content=item_in.content
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}", response_model=KnowledgeItemResponse)
def update_knowledge_item(item_id: int, item_in: KnowledgeItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.id == item_id, KnowledgeBaseItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    item.title = item_in.title
    item.category = item_in.category
    item.content = item_in.content
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
def delete_knowledge_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.id == item_id, KnowledgeBaseItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Item deleted"}
