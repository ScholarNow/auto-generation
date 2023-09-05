from pydantic import BaseModel
from typing import List, Optional
from config import NEWS_TABLE, NEWS_LOGS_TABLE

def tuple_to_news_entity(result_tuple):
    return NewsEntity(
        id=result_tuple[0],
        date=str(result_tuple[1]),
        pdf=result_tuple[2],
        title=result_tuple[3],
        doi=result_tuple[4],
        abstract=result_tuple[5],
        url=result_tuple[6],
        publisher=result_tuple[7],
        journal=result_tuple[8],
        year=result_tuple[9],
        license=eval(result_tuple[10]),
        subject=eval(result_tuple[11]),
        category=result_tuple[12],
        authors=eval(result_tuple[13]),
        figures=eval(result_tuple[14]),
        news_title=result_tuple[15],
        news_keywords=result_tuple[16],
        news_intro=result_tuple[17],
        news_method=result_tuple[18],
        news_conclusion=result_tuple[19],
        news_rephrase=result_tuple[20],
        news_related_work=result_tuple[21],
        news_figures=eval(result_tuple[22]),
        news_references=eval(result_tuple[23])
    )

class NewsEntity(BaseModel):
    id: Optional[int] = None
    date: str = ""
    pdf: str = ""
    title: str = ""
    doi: str = ""
    abstract: str = ""
    url: str = ""
    publisher: str = ""
    journal: str = ""
    year: str = ""
    license: List[str] = []
    subject: List[str] = []
    category: str = ""
    authors: List[object] = []
    figures: List[object] = []
    news_title: str = ""
    news_keywords: str = ""
    news_intro: str = ""
    news_method: str = ""
    news_conclusion: str = ""
    news_related_work: str = ""
    news_references: List[str] = []
    news_rephrase: str = ""
    news_figures: List[str] = []

class NewsLogsEntity(BaseModel):
    id: Optional[int] = None
    details: str = ""

TABLE_FUN_MAP = {NEWS_TABLE: tuple_to_news_entity, NEWS_LOGS_TABLE: None}
TABLE_MODEL_MAP = {NEWS_TABLE: NewsEntity, NEWS_LOGS_TABLE: None}