from dataclasses import dataclass
@dataclass(frozen=True)
class Accommodations:
    problems_per_page:int=3
    font_pt:int=18
    line_height:float=2.0
    page_color:str="cream"
    highlight:bool=True
    simplify:bool=False
DEFAULTS=Accommodations()
PAGE_COLORS={"cream":"#fff9eb","white":"#ffffff","blue":"#f1f7ff"}
