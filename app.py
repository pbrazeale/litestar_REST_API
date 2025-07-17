from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar import Litestar

class Base(DeclarativeBase):
    pass

class ToDo(Base):
    __tablename__ = "todo_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    user_id: Mapped[int]

db_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///db.sqlite",
    metadata=Base.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler,
)

app = Litestar([], plugins=[SQLAlchemyPlugin(db_config)])