from __future__ import annotations

from sqlalchemy.orm import Session

from .config import settings
from .models import AdminUser, Question
from .question_bank import QUESTION_BANK
from .security import hash_password


def seed_admin(db: Session) -> None:
    admin = db.query(AdminUser).filter(AdminUser.username == settings.admin_username).first()
    if admin:
        return

    db.add(
        AdminUser(
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
    )
    db.commit()


def seed_questions(db: Session) -> None:
    existing = {row.order_no: row for row in db.query(Question).all()}
    changed = False

    for item in QUESTION_BANK:
        row = existing.get(item["order_no"])
        if row is None:
            db.add(Question(**item))
            changed = True
            continue

        for key, value in item.items():
            setattr(row, key, value)
        changed = True

    if changed:
        db.commit()
