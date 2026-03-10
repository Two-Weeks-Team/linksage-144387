from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from models import SessionLocal, Link, Tag, LinkTag, LinkHealth
from ai_service import summarize_and_tag, get_top_reads
import uuid

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LinkCreate(BaseModel):
    url: HttpUrl = Field(..., max_length=2048)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class LinkResponse(BaseModel):
    id: str
    url: str
    summary: Optional[str] = None
    smart_tags: List[str] = []
    confidence_score: Optional[int] = None

class TopRead(BaseModel):
    id: str
    title: str
    summary: str
    relevance_score: float
    smart_tags: List[str]

class DashboardResponse(BaseModel):
    top_reads: List[TopRead]
    trending_topics: List[str]

class HealthResponse(BaseModel):
    is_broken: bool
    domain_trust: int
    version_history: Optional[dict] = None

@router.post("/api/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(payload: LinkCreate, db=Depends(get_db)):
    # Basic duplicate check (user_id omitted for demo – use a static placeholder)
    user_id = "demo_user"
    existing = db.query(Link).filter(Link.user_id == user_id, Link.url == str(payload.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Link already saved")

    # Call AI service to get summary and tags
    ai_result = await summarize_and_tag(str(payload.url), payload.notes or "")
    summary = ai_result.get("summary")
    tags = ai_result.get("tags", [])
    confidence = ai_result.get("confidence_score", 0)

    # Create Link record
    link = Link(
        id=str(uuid.uuid4()),
        user_id=user_id,
        url=str(payload.url),
        title=payload.url.split("//")[-1].split("/")[0],  # simple title fallback
        notes=payload.notes,
        summary=summary,
        confidence_score=int(confidence * 100) if isinstance(confidence, float) else confidence,
    )
    db.add(link)
    db.flush()  # obtain link.id for FK relationships

    # Create Tag records (system tags only for demo)
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.name == tag_name, Tag.tag_type == "system").first()
        if not tag:
            tag = Tag(id=str(uuid.uuid4()), name=tag_name, tag_type="system", confidence=100)
            db.add(tag)
            db.flush()
        link_tag = LinkTag(link_id=link.id, tag_id=tag.id, is_primary=False)
        db.add(link_tag)

    db.commit()
    return LinkResponse(
        id=link.id,
        url=link.url,
        summary=summary,
        smart_tags=tags,
        confidence_score=link.confidence_score,
    )

@router.get("/api/dashboard", response_model=DashboardResponse)
async def dashboard():
    # For demo purposes we ignore auth and user context
    data = await get_top_reads()
    return DashboardResponse(**data)

@router.get("/api/links/{link_id}/health", response_model=HealthResponse)
async def link_health(link_id: str, db=Depends(get_db)):
    health = db.query(LinkHealth).filter(LinkHealth.link_id == link_id).first()
    if not health:
        raise HTTPException(status_code=404, detail="Health data not found")
    return HealthResponse(
        is_broken=health.is_broken,
        domain_trust=health.domain_trust,
        version_history=health.version_history,
    )
