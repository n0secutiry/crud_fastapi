from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.router import router as auth_router

from app.database import async_engine, Base, get_async_session
from app.schemas import TaskInDB, TaskCreate, UserInDB
from app.services import get_all_task, get_task_by_id, create_new_task, update_task_by_id, delete_task_by_id



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

@app.get("/")
async def main():
    return "Hello World!"


@app.get("/all_task")
async def show_all_task(session: AsyncSession = Depends(get_async_session)):
    try:
        all_tasks = await get_all_task(session)
        return all_tasks
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/task/{id_task}", response_model=TaskInDB)
async def show_task_by_id(
        id_task: int, session: AsyncSession = Depends(get_async_session),
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        task = await get_task_by_id(id_task, session)
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/create", response_model=TaskInDB)
async def create_new_task_in_db(
        user: TaskCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        new_task = await create_new_task(user, session)
        return new_task
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.put("/update/{id_task}", response_model=TaskInDB)
async def update_task_by(
        id_task: int,
        update_task_arg: TaskCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        update_task = await update_task_by_id(id_task, update_task_arg, session)
        return update_task
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.delete("/delete/{id_task}")
async def delete_task(
        id_task: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserInDB = Depends(get_current_user)
):
    try:
        del_task = await delete_task_by_id(id_task, session)
        return del_task
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
