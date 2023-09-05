from config import NEWS_TABLE, NEWS_LOGS_TABLE
from sql_helper import IConnect
from job_helper import NewsEntity, NewsLogsEntity

news = NewsEntity(
    title="title",
    date="230904",
    pdf="pdf",
    doi="doi",
    abstract="abstract",
    url="url",
    publisher="publisher",
    journal="journal",
    year="year",
    license=["news_figures1", "news_figures2"],
    subject=["news_figures1", "news_figures2"],
    category="category",
    authors=["authors1", "authors2"],
    figures=["figures1", "figures2"],
    news_title="news_title",
    news_keywords="news_keywords",
    news_intro="news_intro",
    news_method="news_method",
    news_conclusion="news_conclusion",
    news_related_work="news_related_work",
    news_references=["news_figures1", "news_figures2"],
    news_rephrase="news_rephrase",
    news_figures=["news_figures1", "news_figures2"],
)

connect = IConnect()

#newsLogs = NewsLogsEntity(id=1, details="details")
#print(connect.loads(newsLogs.__dict__))
#connect.insert(NEWS_TABLE, connect.loads(news.__dict__))
result = connect.get(NEWS_TABLE, "id=2")
#logsid = connect.insert(NEWS_LOGS_TABLE, connect.loads(newsLogs.__dict__))

print(result[0].category)

