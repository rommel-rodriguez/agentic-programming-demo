import logging

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    column,
    event,
)

# from sqlalchemy.orm import mapper, relationship
from sqlalchemy.orm import declarative_base, registry, relationship

from app.domain import models

logger = logging.getLogger(__name__)

# metadata = MetaData()
mapper_registry = registry()

logger = logging.getLogger(__name__)


users = Table(
    "users",
    mapper_registry.metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
    ),
    Column("name", String(255)),
    Column("email", String(255)),
)

threads = Table(
    "threads",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("thread_id", Integer),
    Column("user_id", ForeignKey("users.id")),
    ## NOTE:  Assuming we are not using a NoSQL database, we would store on message per
    ## row for each thread, and all threads for all users in the same table.
    ## Note that this might change if using a document database in which case
    ## I would store all messages for the same thread inside an attribute
    ## (list of messages).
    # Column("message", String()),
)

thread_messages = Table(
    "thread_messages",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("thread_id", ForeignKey("threads.id")),
)

messages = Table(
    "messages",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("content", String()),
)


def start_mappers():
    logger.info("Starting mappers")
    ## TODO: Currently lacking the domain models
    # users_mapper = mapper()
    mapper_registry.map_imperatively(models.User, users)
    ## NOTE: Need to capture the mapper returned by map_imperatively in order to use
    ## it in the following relationship. Tho, reading the documentation for v2, I  think
    ## this can be achieved in other ways as well.
    messages_mapper = mapper_registry.map_imperatively(models.Message, messages)
    mapper_registry.map_imperatively(
        models.Thread,
        threads,
        properties={
            "messages": relationship(
                messages_mapper, secondary=thread_messages, collection_class=list
            )
        },
    )
