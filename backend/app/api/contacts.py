from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import User, Contact
from ..schemas.schemas import ContactCreate, ContactResponse
from .deps import get_db, get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts / VIP"])

@router.get("", response_model=List[ContactResponse])
def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    # Seed default VIP contacts if empty
    if not contacts:
        defaults = [
            Contact(user_id=current_user.id, name="Rahul Verma", phone_number="+919810098765", category="Client", notes="Lead Enterprise Client (Acme)", always_alert=True),
            Contact(user_id=current_user.id, name="Ananya Kumar", phone_number="+919877665544", category="Family", notes="Immediate Family", always_alert=True, always_transfer=True),
            Contact(user_id=current_user.id, name="Dr. Mehta", phone_number="+919811002233", category="Other", notes="Family Physician", always_alert=True),
            Contact(user_id=current_user.id, name="RoboMarketer Spam", phone_number="+919800000001", category="Other", notes="Unsolicited loan telemarketing", is_blocked=True)
        ]
        db.add_all(defaults)
        db.commit()
        contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    return contacts

@router.post("", response_model=ContactResponse)
def create_contact(contact_in: ContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = Contact(
        user_id=current_user.id,
        name=contact_in.name,
        phone_number=contact_in.phone_number,
        category=contact_in.category,
        notes=contact_in.notes,
        always_alert=contact_in.always_alert,
        always_transfer=contact_in.always_transfer,
        is_blocked=contact_in.is_blocked
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_in: ContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact.name = contact_in.name
    contact.phone_number = contact_in.phone_number
    contact.category = contact_in.category
    contact.notes = contact_in.notes
    contact.always_alert = contact_in.always_alert
    contact.always_transfer = contact_in.always_transfer
    contact.is_blocked = contact_in.is_blocked
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}")
def delete_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"status": "success", "message": "Contact deleted"}
