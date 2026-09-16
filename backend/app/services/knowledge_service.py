from typing import List
from sqlalchemy.orm import Session
from ..models.models import KnowledgeBaseItem

class KnowledgeService:
    @staticmethod
    def get_aggregated_knowledge(db: Session, user_id: int) -> str:
        items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.user_id == user_id).all()
        if not items:
            return (
                "- Working Hours: Monday to Friday, 9:00 AM to 6:00 PM IST.\n"
                "- Services: Technical consulting, system architecture, cloud deployment, and software engineering.\n"
                "- Location: Bangalore / Remote.\n"
                "- Emergency: Please dial 112 / 911 for life safety or medical emergencies."
            )
        lines = []
        for it in items:
            lines.append(f"[{it.category.upper()}] {it.title}: {it.content}")
        return "\n".join(lines)
