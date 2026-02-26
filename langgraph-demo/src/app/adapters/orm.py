import logging

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)

# from sqlalchemy.orm import mapper, relationship
from sqlalchemy.orm import registry, relationship

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
    Column("email", String(255), unique=True),
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
    Column("message_id", ForeignKey("messages.id")),
)

messages = Table(
    "messages",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("content", String()),
    Column("type", String()),
)

# NOTE: Invoice related tables

invoices = Table(
    "invoices",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", ForeignKey("users.id")),
    Column("amount", Float, nullable=False),
    Column("due_date", Date),
)

documents = Table(
    "documents",
    mapper_registry.metadata,
    Column("id", String(36), primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("content_type", String(100), nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column(
        "status",
        SAEnum(
            models.DocumentStatus,
            name="document_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        server_default=models.DocumentStatus.PENDING_UPLOAD.value,
    ),
    Column(
        "purpose",
        SAEnum(
            models.DocumentPurpose,
            name="document_purpose",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    ),
    Column("storage_key", String(512), nullable=True, unique=True),
    Column("checksum_sha256", String(512), nullable=True, unique=True),
    Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now()
    ),
    Column(
        "uploaded_at",
        DateTime(timezone=True),
        nullable=True,
    ),
    Column(
        "processed_at",
        DateTime(timezone=True),
        nullable=True,
    ),
    Column("chunk_count", Integer, nullable=True),
    Column("doc_metadata", JSON, nullable=False, server_default="{}"),
    Column("error_message", Text, nullable=True),
    CheckConstraint("size_bytes >= 0", name="ck_documents_size_non_negative"),
)


def start_mappers():
    logger.info("Starting mappers")
    ## TODO: Currently lacking the domain models
    # users_mapper = mapper()
    mapper_registry.map_imperatively(models.User, users)
    mapper_registry.map_imperatively(models.Invoice, invoices)
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
    mapper_registry.map_imperatively(models.Document, documents)
