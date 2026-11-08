"""Deterministic layout and PDF generation; document strings are HTML escaped."""
import base64,html,re
import fitz
from weasyprint import HTML
from config import PAGE_COLORS
def esc(value): return html.escape(str(value or ""),quote=True)
def highlighted(text,spans,enabled):
    if not enabled:return esc(text).replace("\n","<br>")
    spans=sorted({s.strip() for s in spans if s and s.strip() and s in text},key=len,reverse=True)
    if not spans:return esc(text).replace("\n","<br>")
    pattern=re.compile("("+"|".join(re.escape(x) for x in spans)+")")
    return "".join("<mark>"+esc(part)+"</mark>" if part in spans else esc(part) for part in pattern.split(text)).replace("\n","<br>")
def figure_html(source,spec,warnings):
    try:
        n=int(spec["page"])-1
        coords=spec["bbox"]
        if not 0<=n<len(source) or len(coords)!=4: raise ValueError("invalid page/box")
        x0,y0,x1,y1=map(float,coords)
        if min(x0,y0,x1,y1)<0 or max(x0,y0,x1,y1)>1000 or x1<=x0 or y1<=y0: raise ValueError("invalid box")
        page=source[n]; rect=page.rect
        crop=fitz.Rect(rect.x0+x0/1000*rect.width,rect.y0+y0/1000*rect.height,rect.x0+x1/1000*rect.width,rect.y0+y1/1000*rect.height)
        pix=page.get_pixmap(matrix=fitz.Matrix(2,2),clip=crop,alpha=False)
        if pix.width*pix.height>12_000_000:raise ValueError("oversized image")
        data=base64.b64encode(pix.tobytes("png")).decode("ascii")
        return '<figure><img src="data:image/png;base64,'+data+'" alt="'+esc(spec.get("description","Worksheet figure"))+'"></figure>'
    except Exception:
        warnings.append("A source figure could not be reproduced; teacher review required")
        return '<p class="error">Original figure requires teacher review.</p>'
def render(original,worksheet,profile):
    warnings=[]
    with fitz.open(stream=original,filetype="pdf") as source:
        questions=worksheet.get("questions",[])
        if not questions:raise ValueError("No questions found")
        panels=[]
        for i,q in enumerate(questions):
            num=q.get("number",str(i+1))
            figs="".join(figure_html(source,f,warnings) for f in q.get("figures",[]))
            if q.get("uncertainty"):warnings.append("Question "+str(num)+": "+q["uncertainty"])
            try:lines=max(1,min(6,int(q.get("answer_lines",2))))
            except (ValueError,TypeError):lines=2
            clazz="question page-break" if i and i%profile.problems_per_page==0 else "question"
            body=highlighted(q.get("text",""),q.get("highlights",[]),profile.highlight)
            panels.append('<section class="'+clazz+'"><div class="q-number">Problem '+esc(num)+'</div><div class="q-body">'+body+'</div>'+figs+'<div class="answer">'+('<div class="answer-line"></div>'*lines)+'</div></section>')
    color=PAGE_COLORS[profile.page_color]
    css="""@page{size:letter;margin:.63in .7in}html,body{background:COLOR}body{font-family:Arial,"DejaVu Sans",sans-serif;font-size:SIZEpt;line-height:2;color:#172334}h1{font-size:1.25em;line-height:1.25}.directions{font-size:.88em;line-height:1.45;background:#eef2ed;padding:9pt;margin-bottom:17pt}.question{break-inside:avoid;padding:10pt 0 12pt;border-bottom:1px solid #d6d9d8}.page-break{break-before:page}.q-number{font-size:.79em;font-weight:bold;line-height:1.25;color:#1e3d5c;margin-bottom:6pt}mark{background:#fff1a6;color:inherit}figure{margin:8pt 0}figure img{max-width:100%;max-height:2.6in}.answer-line{border-bottom:1px solid #b5bfc7;height:21pt}.error{color:#a43d28;font-size:12pt}footer{position:fixed;bottom:-.36in;font-size:9pt;color:#687580}""".replace("COLOR",color).replace("SIZE",str(profile.font_pt))
    directions=worksheet.get("instructions","")
    note='<div class="directions">'+esc(directions).replace("\n","<br>")+'</div>' if directions else ""
    doc='<!doctype html><html><head><meta charset="utf-8"><style>'+css+'</style></head><body><h1>'+esc(worksheet.get("title") or "Accessible Worksheet")+'</h1>'+note+"".join(panels)+'<footer>Adapted layout · Check against original before assigning</footer></body></html>'
    return HTML(string=doc).write_pdf(),warnings
