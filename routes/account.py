from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import *
from database import get_db_session

account_router = APIRouter(
    prefix="/account"
)

@account_router.post("/create")
async def _add_account(account: AccountDataBase, session: AsyncSession = Depends(get_db_session)):
    if await check_username_exists(username=account.username, session=session):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"success": False, "error": "Username is already taken"})

    if await check_email_exists(email=account.email, session=session):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"success": False, "error": "Email is already taken"})

    resp = await create_account(account=account, session=session)
    
    if resp["success"] is not True:
        if resp["error"] == "duplicate":
            return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"success": False, "error": "Account detail is invalid"})
        
        else:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"success": False, "error": "idk man"})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True})

@account_router.get("/check/username")
async def _username_exists(username: str, session: AsyncSession = Depends(get_db_session)):
    return {"exists": await check_username_exists(username=username, session=session)}

@account_router.get("/check/email")
async def _email_exists(email: str, session: AsyncSession = Depends(get_db_session)):
    return {"exists": await check_email_exists(email=email, session=session)}

@account_router.get("/get-account")
async def _get_account(username: str = None, email: str = None, uid: str = None, session: AsyncSession = Depends(get_db_session)):
    account = await get_account(account=AccountRequest(username=username, email=email, uid=uid), session=session)
    if account is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"success": False})

    return JSONResponse(status_code=status.HTTP_200_OK, content=
                        {"success": True, "account": account.model_dump()})

# @account_router.get("/is_username_registered_for_email")
# async def is_username_registered_for_email(email: str, session: AsyncSession = Depends(get_db_session)):
#     return {"exists": True}