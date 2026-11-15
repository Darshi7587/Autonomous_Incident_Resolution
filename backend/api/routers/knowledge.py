from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
from backend.knowledge.chroma_store import get_chroma_store, DEFAULT_RUNBOOKS

router = APIRouter(prefix="/knowledge", tags=["Knowledge & RAG Intelligence"])

@router.get("/runbooks")
async def list_runbooks():
    """Retrieve catalog of enterprise operational runbooks stored in ChromaDB."""
    return DEFAULT_RUNBOOKS

@router.post("/search")
async def search_knowledge(
    query: str = Body(..., embed=True),
    category: Optional[str] = Body(default=None, embed=True),
    n_results: int = Body(default=3, embed=True)
):
    """
    Perform semantic vector similarity search across IT runbooks and historical incident RCAs.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query text cannot be empty")

    chroma_store = get_chroma_store()
    results = chroma_store.query_runbooks(query_text=query, n_results=n_results, category=category)
    return {
        "query": query,
        "results_count": len(results),
        "matches": results
    }
