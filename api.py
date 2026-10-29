
import os
import secrets

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Header,
    Depends,
)
from pydantic import BaseModel

from engine.core import (
    extract,
    ingest_text,
    documents,
    delete_document,
    search,
    investigate,
)


app = FastAPI(
    title="AI Investigation Engine",
    version="0.1",
)


# ----------------------------------------
# ADMIN AUTHENTICATION
# ----------------------------------------

def require_admin(x_admin_key: str | None = Header(default=None)):
    expected = os.getenv("ADMIN_API_KEY")

    if (
        not expected
        or not x_admin_key
        or not secrets.compare_digest(x_admin_key, expected)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


# ----------------------------------------
# REQUEST MODELS
# ----------------------------------------

class Query(BaseModel):
    question: str
    k: int = 8


class TextDocument(BaseModel):
    name: str
    text: str
    strategy: str = "characters"


# ----------------------------------------
# HEALTH CHECK
# ----------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------------------
# DOCUMENT MANAGEMENT
# ----------------------------------------

@app.get("/documents")
def list_docs():
    return documents()


@app.post(
    "/documents/upload",
    dependencies=[Depends(require_admin)],
)
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()

        print(
            f"UPLOAD: {file.filename}, "
            f"{len(content)} bytes"
        )

        extracted = extract(file.filename, content)

        print(
            f"EXTRACTED: {len(extracted)} characters"
        )

        result = ingest_text(
            file.filename,
            extracted,
        )

        print("UPLOAD SUCCESS:", result)

        return result

    except ValueError as e:
        print("UPLOAD VALIDATION ERROR:", repr(e))

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        print("UPLOAD INTERNAL ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Document upload failed",
        )


@app.post(
    "/documents/text",
    dependencies=[Depends(require_admin)],
)
def add_text(doc: TextDocument):
    try:
        return ingest_text(
            doc.name,
            doc.text,
            doc.strategy,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.delete(
    "/documents/{doc_id}",
    dependencies=[Depends(require_admin)],
)
def delete(doc_id: str):
    delete_document(doc_id)

    return {"deleted": doc_id}


# ----------------------------------------
# DOCUMENT RETRIEVAL
# ----------------------------------------

@app.post(
    "/search",
    dependencies=[Depends(require_admin)],
)
def retrieve(q: Query):
    return search(q.question, q.k)


# ----------------------------------------
# AI INVESTIGATION
# ----------------------------------------

@app.post(
    "/investigate",
    dependencies=[Depends(require_admin)],
)
def answer(q: Query):
    try:
        return investigate(
            q.question,
            q.k,
        )

    except Exception as e:
        print("GEMINI ERROR:", repr(e))

        raise HTTPException(
            status_code=502,
            detail=(
                "Investigation failed: "
                f"{type(e).__name__}"
            ),
        )
