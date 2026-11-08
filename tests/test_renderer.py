import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
import fitz
from config import DEFAULTS
from renderer import highlighted,render
def test_escape():
    assert "&lt;script&gt;" in highlighted("<script>",[],True)
def test_highlight():
    assert "<mark>not</mark>" in highlighted("Do not circle",["not"],True)
def test_pdf():
    source=fitz.open()
    source.new_page()
    original=source.tobytes()
    worksheet={"title":"Practice","instructions":"Solve each problem","questions":[{"number":str(i),"text":f"What is {i}+1?","highlights":[str(i)],"figures":[],"answer_lines":1,"uncertainty":""} for i in range(1,7)]}
    pdf,warnings=render(original,worksheet,DEFAULTS)
    with fitz.open(stream=pdf,filetype="pdf") as adapted:
        assert len(adapted)>=2
        text="\n".join(page.get_text() for page in adapted)
        assert "Problem 1" in text and "Problem 6" in text
    assert not warnings
