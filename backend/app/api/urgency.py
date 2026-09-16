from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import User, UrgencyRuleModel
from ..schemas.schemas import UrgencyRuleCreate, UrgencyRuleResponse
from .deps import get_db, get_current_user

router = APIRouter(prefix="/urgency-rules", tags=["Urgency Rules Engine"])

@router.get("", response_model=List[UrgencyRuleResponse])
def get_urgency_rules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rules = db.query(UrgencyRuleModel).filter(UrgencyRuleModel.user_id == current_user.id).all()
    if not rules:
        defaults = [
            UrgencyRuleModel(user_id=current_user.id, title="High Urgency Outage Rule", condition_type="URGENCY_LEVEL", condition_value="HIGH", action="SMS", is_enabled=True),
            UrgencyRuleModel(user_id=current_user.id, title="Critical Emergency Escalation", condition_type="URGENCY_LEVEL", condition_value="CRITICAL", action="CALL_TRANSFER", is_enabled=True),
            UrgencyRuleModel(user_id=current_user.id, title="Always Alert VIP Clients & Family", condition_type="VIP_CALLER", condition_value="ALL_VIP", action="SMS", is_enabled=True),
            UrgencyRuleModel(user_id=current_user.id, title="Deadline Today Keyword Trigger", condition_type="KEYWORD", condition_value="deadline today", action="SMS", is_enabled=True),
            UrgencyRuleModel(user_id=current_user.id, title="Ignore Marketing & Telemarketing Calls", condition_type="MARKETING_SPAM", condition_value="loan,credit card,promotion", action="NO_ALERT", is_enabled=True)
        ]
        db.add_all(defaults)
        db.commit()
        rules = db.query(UrgencyRuleModel).filter(UrgencyRuleModel.user_id == current_user.id).all()
    return rules

@router.post("", response_model=UrgencyRuleResponse)
def create_rule(rule_in: UrgencyRuleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = UrgencyRuleModel(
        user_id=current_user.id,
        title=rule_in.title,
        condition_type=rule_in.condition_type,
        condition_value=rule_in.condition_value,
        action=rule_in.action,
        is_enabled=rule_in.is_enabled
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{rule_id}", response_model=UrgencyRuleResponse)
def update_rule(rule_id: int, rule_in: UrgencyRuleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(UrgencyRuleModel).filter(UrgencyRuleModel.id == rule_id, UrgencyRuleModel.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.title = rule_in.title
    rule.condition_type = rule_in.condition_type
    rule.condition_value = rule_in.condition_value
    rule.action = rule_in.action
    rule.is_enabled = rule_in.is_enabled
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(UrgencyRuleModel).filter(UrgencyRuleModel.id == rule_id, UrgencyRuleModel.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "success", "message": "Rule deleted"}
