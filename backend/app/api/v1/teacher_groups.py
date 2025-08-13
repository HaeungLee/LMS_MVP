from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.models.orm import Group, GroupMember, TeacherGroup, User


router = APIRouter()


class GroupCreateDto(BaseModel):
    name: str


@router.get("/teacher/groups")
def list_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user), _=Depends(require_role(["teacher", "admin"]))):
    rows = (
        db.query(Group)
        .join(TeacherGroup, TeacherGroup.group_id == Group.id)
        .filter(TeacherGroup.teacher_user_id == user.id)
        .order_by(Group.created_at.desc())
        .all()
    )
    return {"items": [{"id": g.id, "name": g.name} for g in rows]}


@router.post("/teacher/groups")
def create_group(body: GroupCreateDto, db: Session = Depends(get_db), user: User = Depends(get_current_user), _=Depends(require_role(["teacher", "admin"]))):
    name = (body.name or '').strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    # ensure unique
    if db.query(Group).filter(Group.name == name).first():
        raise HTTPException(status_code=400, detail="name taken")
    g = Group(name=name)
    db.add(g)
    db.flush()
    db.add(TeacherGroup(group_id=g.id, teacher_user_id=user.id))
    db.commit()
    return {"id": g.id, "name": g.name}


class GroupMemberDto(BaseModel):
    user_id: int


@router.post("/teacher/groups/{group_id}/members")
def add_member(group_id: int, body: GroupMemberDto, db: Session = Depends(get_db), user: User = Depends(get_current_user), _=Depends(require_role(["teacher", "admin"]))):
    g = (
        db.query(Group)
        .join(TeacherGroup, TeacherGroup.group_id == Group.id)
        .filter(Group.id == group_id, TeacherGroup.teacher_user_id == user.id)
        .first()
    )
    if not g:
        raise HTTPException(status_code=404, detail="group not found")
    # add membership
    if not db.query(User).filter(User.id == body.user_id).first():
        raise HTTPException(status_code=400, detail="user not found")
    db.add(GroupMember(group_id=group_id, user_id=body.user_id))
    db.commit()
    return {"ok": True}


