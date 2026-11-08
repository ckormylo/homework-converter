"""FastAPI backend for the accessible homework converter."""
import asyncio,base64,os
from dataclasses import asdict,replace
import fitz
from fastapi import FastAPI,UploadFile,File,Form,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import DEFAULTS
from ai import interpret,verify
from renderer import render
MAX_BYTES=8*1024*1024
app=FastAPI(title="Homework Converter",docs_url=None,redoc_url=None)
origins=[s.strip() for s in os.getenv("ALLOWED_ORIGINS","http://localhost:8000").split(",") if s.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=["GET","POST"],allow_headers=["Content-Type"])
@app.get("/health")
def health(): return {"ok":True}
@app.get("/config")
def config(): return asdict(DEFAULTS)
def process(pdf,profile):
    worksheet=interpret(pdf,profile.simplify)
    questions=worksheet.get("questions",[])
    if not 1<=len(questions)<=150: raise ValueError("No plausible question list")
    adapted,warnings=render(pdf,worksheet,profile)
    warnings=list(worksheet.get("warnings",[]))+warnings
    with fitz.open(stream=adapted,filetype="pdf") as document:
        if not len(document): raise ValueError("Empty generated PDF")
        text="\n".join(p.get_text() for p in document)
        for q in questions:
            label="Problem "+str(q.get("number",""))
            if label not in text: warnings.append("Missing label: "+label)
    review=verify(pdf,adapted)
    warnings.extend(review.get("warnings",[]))
    if review.get("missing_or_changed_question_numbers"):
        warnings.append("Questions needing comparison: "+", ".join(map(str,review["missing_or_changed_question_numbers"])))
    warnings=list(dict.fromkeys(warnings))
    return adapted,{"passed":bool(review.get("passed")) and not warnings,"question_count":len(questions),"reviewed":True,"warnings":warnings}
@app.post("/convert")
async def convert(file:UploadFile=File(...),problems_per_page:int=Form(3),font_pt:int=Form(18),page_color:str=Form("cream"),highlight:bool=Form(True),simplify:bool=Form(False)):
    if not file.filename or not file.filename.lower().endswith(".pdf"): raise HTTPException(400,"Please upload a PDF.")
    if problems_per_page not in (2,3,4) or font_pt not in (16,18,20) or page_color not in ("white","cream","blue"): raise HTTPException(400,"Invalid setting")
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise HTTPException(413,"PDF exceeds 8 MB")
    try:
        with fitz.open(stream=data,filetype="pdf") as source:
            if not 1<=len(source)<=10: raise HTTPException(400,"PDF must have 1–10 pages")
            if source.needs_pass: raise HTTPException(400,"Password-protected PDFs not supported")
    except HTTPException: raise
    except Exception: raise HTTPException(400,"Unable to read PDF")
    profile=replace(DEFAULTS,problems_per_page=problems_per_page,font_pt=font_pt,page_color=page_color,highlight=highlight,simplify=simplify)
    try: adapted,review=await asyncio.to_thread(process,data,profile)
    except Exception as error:
        print("Conversion failed:",type(error).__name__)
        raise HTTPException(502,"Conversion failed. Please try again or contact the site owner.")
    return {"pdf_base64":base64.b64encode(adapted).decode("ascii"),"review":review}
