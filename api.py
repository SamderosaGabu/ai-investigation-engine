from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from engine.core import extract, ingest_text, documents, delete_document, search, investigate
app=FastAPI(title='AI Investigation Engine',version='0.1')
class Query(BaseModel):
    question:str
    k:int=8
class TextDocument(BaseModel):
    name:str
    text:str
    strategy:str='characters'
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/documents')
def list_docs(): return documents()

@app.post("/documents/upload")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        print(f"UPLOAD: {file.filename}, {len(content)} bytes")

        extracted = extract(file.filename, content)
        print(f"EXTRACTED: {len(extracted)} characters")

        result = ingest_text(file.filename, extracted)
        print("UPLOAD SUCCESS:", result)

        return result

    except ValueError as e:
        print("UPLOAD VALIDATION ERROR:", repr(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("UPLOAD INTERNAL ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}",
        )
@app.post('/documents/text')
def add_text(doc:TextDocument):
    try: return ingest_text(doc.name,doc.text,doc.strategy)
    except ValueError as e: raise HTTPException(400,str(e))
@app.delete('/documents/{doc_id}')
def delete(doc_id:str): delete_document(doc_id); return {'deleted':doc_id}
@app.post('/search')
def retrieve(q:Query): return search(q.question,q.k)
@app.post('/investigate')
def answer(q:Query):
    try: return investigate(q.question,q.k)
    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        raise HTTPException(status_code=502, detail=f"Investigation failed: {type(e).__name__}")
