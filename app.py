from collections.abc import AsyncGenerator

from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from litestar import Litestar, get, post
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

class Base(DeclarativeBase):
    pass

class ToDo(Base):
    __tablename__ = "todo_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    user_id: Mapped[int]

# extrapolaote out post to prevent Async conflicts
async def provide_transaction(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    async with db_session.begin():
        yield db_session


@post("/todo")
async def create_todo(data: ToDo, transaction: AsyncSession) -> ToDo:
    transaction.add(data)
    return data

@get("/todos")
async def get_todos(transaction: AsyncSession) -> list[ToDo]:
    query = select(ToDo)
    result = await transaction.execute(query)
    return result.scalars().all()

db_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///db.sqlite",
    metadata=Base.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler,
)

app = Litestar(
    route_handlers=[get_todos, create_todo],
    dependencies={"transaction": provide_transaction}, 
    plugins=[SQLAlchemyPlugin(db_config)])