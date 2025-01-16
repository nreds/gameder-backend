from .models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

__all__ = [
    "check_username_exists",
    "check_email_exists",
    "create_account",
    "get_account"
]

async def check_username_exists(username: str, session: AsyncSession) -> bool:
    account = (await session.scalars(select(AccountData).filter(AccountData.username == username))).first()
    return account is not None

async def check_email_exists(email: str, session: AsyncSession) -> bool:
    account = (await session.scalars(select(AccountData).filter(AccountData.email == email))).first()
    return account is not None

async def create_account(account: AccountDataBase = None, session: AsyncSession = None, **kwargs):
    db_account = AccountData(**(account.model_dump() if AccountData is not None else kwargs))

    try:
        await session.execute(text("CALL `new_user` (:uid, :username, :email);"), {"uid": account.uid, "username": account.username, "email": account.email})
        await session.commit()

    except IntegrityError:
        return {"success": False, "error": "duplicate", "message": "Exists in database"}
    
    except Exception as e:
        return {"success": False, "error": e, "message": "An unknown error has occurred, please try again later"}

    return {"success": True, "account": db_account}

async def get_account(account: AccountRequest, session: AsyncSession) -> AccountDataBase:
    account = (await session.scalars(select(AccountData).filter_by(**account.dict()))).first()
    return AccountDataBase(**account.__dict__) if account is not None else None