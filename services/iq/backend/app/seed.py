from sqlalchemy.orm import Session

from .config import settings
from .models import AdminUser, Question
from .question_bank import QUESTION_BANK
from .security import hash_password


def seed_admin(db: Session):
    admin = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
    if not admin:
        db.add(
            AdminUser(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
        )
        db.commit()


def seed_questions(db: Session):
    count = db.query(Question).count()
    if count == 0:
        for item in QUESTION_BANK:
            db.add(Question(**item))
        db.commit()
