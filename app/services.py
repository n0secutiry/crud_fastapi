from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.schemas import TaskCreate

# async def conn_db():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


async def get_all_task(session: AsyncSession):
    result = await session.execute(select(Task))
    return result.scalars().all()


async def get_task_by_id(id_task: int, session: AsyncSession):
    result = await session.execute(select(Task).where(Task.id == id_task))
    user = result.scalars().one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_new_task(user: TaskCreate, session: AsyncSession):
    new_task = Task(
        name=user.name,
        task=user.task,
    )

    session.add(new_task)

    try:
        await session.commit()
        await session.refresh(new_task)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return new_task


async def update_task_by_id(id_user: int, task_update, session: AsyncSession):
    result = await session.execute(select(Task).where(Task.id == id_user))
    task = result.scalars().one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.name = task_update.name
    task.task = task_update.task

    await session.commit()
    await session.refresh(task)

    return task


async def delete_task_by_id(id_task: int, session: AsyncSession):
    result = await session.execute(select(Task).where(Task.id == id_task))
    task = result.scalars().one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()

    return {"message": "Task deleted!"}