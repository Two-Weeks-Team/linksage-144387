import os
from sqlalchemy import (Column, String, Integer, Boolean, DateTime,
                        JSON, ForeignKey, create_engine, text)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# Resolve DATABASE_URL with automatic scheme fixes
raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Add SSL args for remote Postgres (non‑localhost & not SQLite)
if not raw_url.startswith("sqlite") and "localhost" not in raw_url:
    engine = create_engine(raw_url, connect_args={"sslmode": "require"}, echo=False)
else:
    engine = create_engine(raw_url, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Prefix for all tables to avoid collisions
TABLE_PREFIX = "ls_"

class User(Base):
    __tablename__ = f"{TABLE_PREFIX}users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    dark_mode = Column(Boolean, default=False)
    # relationships
    links = relationship("Link", back_populates="owner")

class Link(Base):
    __tablename__ = f"{TABLE_PREFIX}links"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey(f"{TABLE_PREFIX}users.id"), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    # AI fields
    summary = Column(String)
    confidence_score = Column(Integer)
    # relationships
    owner = relationship("User", back_populates="links")
    tags = relationship("Tag", secondary=f"{TABLE_PREFIX}link_tags", back_populates="links")
    health = relationship("LinkHealth", uselist=False, back_populates="link")

class Tag(Base):
    __tablename__ = f"{TABLE_PREFIX}tags"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tag_type = Column(String, nullable=False)  # 'system' or 'user'
    confidence = Column(Integer, default=100)
    links = relationship("Link", secondary=f"{TABLE_PREFIX}link_tags", back_populates="tags")

class LinkTag(Base):
    __tablename__ = f"{TABLE_PREFIX}link_tags"
    link_id = Column(String, ForeignKey(f"{TABLE_PREFIX}links.id"), primary_key=True)
    tag_id = Column(String, ForeignKey(f"{TABLE_PREFIX}tags.id"), primary_key=True)
    applied_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    is_primary = Column(Boolean, default=False)

class LinkHealth(Base):
    __tablename__ = f"{TABLE_PREFIX}link_health"
    link_id = Column(String, ForeignKey(f"{TABLE_PREFIX}links.id"), primary_key=True)
    is_broken = Column(Boolean, default=False)
    domain_trust = Column(Integer, default=50)
    last_checked = Column(DateTime(timezone=True), server_default=text("NOW()"))
    version_history = Column(JSON)
    link = relationship("Link", back_populates="health")
