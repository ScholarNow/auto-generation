import os
from api_helper import SectionEntity,parse_paper,gen_title,gen_keywords,gen_sections_verbose,gen_related_work,rephrase_paragraphs,animate_figures
from sql_helper import IConnect
import concurrent.futures
import timeit
from file_helper import get_json_content, get_pdf_content
from config import NEWS_TABLE, NEWS_LOGS_TABLE
import json
from models import NewsEntity, NewsLogsEntity

def main(path:str, basename:str, date:int):
    print(f"paper: {basename}")
    json_path = os.path.join(path, str(date), basename + ".json")
    pdf_path = os.path.join(path, str(date), basename + ".pdf")
    json_content = get_json_content(json_path)
    pdf_bites = get_pdf_content(pdf_path)
    pdf_name = basename + ".pdf"

    try:
        process_start = timeit.default_timer()
        parse_time, parse_result = parse_paper(pdf_bites, pdf_name)
        if parse_time == -1:
            raise Exception("parse paper failed")
        # multi-thread with gen title and abstract
        threads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            threads.append(executor.submit(gen_title, parse_result["data"]["abstract"]))
            threads.append(executor.submit(gen_keywords, parse_result["data"]["abstract"]))
        title_time, title_result = threads[0].result()
        keywords_time, keywords_result = threads[1].result()
        threads.clear()
        # multi-thread with gen 3 paragraphs and related work and gen animating gif
        threads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            threads.append(
                executor.submit(
                    gen_sections_verbose,
                    SectionEntity(
                        section_type="b",
                        section_name="Introduction",
                        section_content=parse_result["data"]["section_text"][
                            "Introduction"
                        ],
                        keywords=keywords_result["data"],
                    ),
                )
            )
            threads.append(
                executor.submit(
                    gen_sections_verbose,
                    SectionEntity(
                        section_type="m",
                        section_name="Method",
                        section_content=parse_result["data"]["section_text"]["Method"],
                        keywords=keywords_result["data"],
                    ),
                )
            )
            threads.append(
                executor.submit(
                    gen_sections_verbose,
                    SectionEntity(
                        section_type="e",
                        section_name="Conclusion",
                        section_content=parse_result["data"]["section_text"]["Conclusion"],
                        keywords=keywords_result["data"],
                    ),
                )
            )
            threads.append(
                executor.submit(
                    gen_related_work,
                    parse_result["data"]["title"],
                    keywords_result["data"],
                )
            )
            if parse_result["data"]["figures"] != []:
                threads.append(
                    executor.submit(
                        animate_figures,
                        parse_result["data"]["figures"],
                    )
                )
        intro_time, intro_result = threads[0].result()
        method_time, method_result = threads[1].result()
        conclusion_time, conclusion_result = threads[2].result()
        related_work_time, related_work_result = threads[3].result()
        animate_time, animate_result = -1, None
        if len(threads) == 5:
            animate_time, animate_result = threads[4].result()
        if method_time != -1 and conclusion_time != -1:
            rephrase_time, rephrase_result = rephrase_paragraphs(
                [
                    method_result["rephrase_result"]["data"],
                    conclusion_result["rephrase_result"]["data"],
                ]
            )
        else:
            rephrase_time, rephrase_result = -1, None
        process_end = timeit.default_timer()
        process_time = process_end - process_start
        if title_time == -1 or keywords_time == -1 or intro_time == -1 or method_time == -1 or conclusion_time == -1 or rephrase_time == -1:
            raise Exception("generate error")
        # save details to json
        process_result = {
            "totle_time": process_time,
            "parse_time": parse_time,
            "title_time": title_time,
            "keywords_time": keywords_time,
            "intro_time": intro_time,
            "method_time": method_time,
            "conclusion_time": conclusion_time,
            "related_work_time": related_work_time,
            "rephrase_time": rephrase_time,
            "animate_time": -1 if animate_time == -1 else animate_time,
            "parse_result": parse_result,
            "title_result": title_result,
            "keywords_result": keywords_result,
            "intro_result": intro_result,
            "method_result": method_result,
            "conclusion_result": conclusion_result,
            "related_work_result": related_work_result,
            "rephrase_result": rephrase_result,
            "animate_result": [] if animate_result == None else animate_result,
        }
    except Exception as e:
        print(e)
        return
    
    title = parse_result["data"]["title"] if "title" not in json_content else json_content["title"]
    doi = "" if "doi" not in json_content else json_content["doi"]
    abstract = parse_result["data"]["abstract"] if "abstract" not in json_content else json_content["abstract"]
    url = "" if "url" not in json_content else json_content["url"]
    publisher = "" if "publisher" not in json_content else json_content["publisher"]
    journal = "" if "journal" not in json_content else json_content["journal"]
    year = "" if "year" not in json_content else json_content["year"]
    license = "" if "license" not in json_content else json_content["license"]
    subject = "" if "subject" not in json_content else json_content["subject"]
    category = "" if "category" not in json_content else json_content["category"]
    authors = [] if "authors" not in json_content else json_content["authors"]
    figures = parse_result["data"]["figures"] if "figures" not in json_content else []
    news_title = title_result["data"]
    news_keywords = keywords_result["data"]
    news_intro = intro_result["rephrase_result"]["data"]
    news_method = method_result["rephrase_result"]["data"]
    news_conclusion = conclusion_result["rephrase_result"]["data"]
    news_related_work = related_work_result["data"]["paraphrase_result"]
    news_references = related_work_result["data"]["references"]
    news_rephrase = rephrase_result["data"]
    news_figures = process_result["animate_result"]

    news = NewsEntity(title=title,date=date, pdf=pdf_name, doi=doi, abstract=abstract, url=url,
                      publisher=publisher, journal=journal, year=year, license=license,
                      subject=subject, category=category, authors=authors, figures=figures,
                      news_title=news_title, news_keywords=news_keywords, news_intro=news_intro,
                      news_method=news_method, news_conclusion=news_conclusion,
                      news_related_work=news_related_work, news_references=news_references,
                      news_rephrase=news_rephrase, news_figures=news_figures)
    
    news_dict= news.__dict__
    del news_dict["id"]

    try:

        connect = IConnect()

        id = connect.insert(NEWS_TABLE, connect.loads(news_dict))
        
        newsLogs = NewsLogsEntity(id=id, details=json.dumps(process_result))

        connect.insert(NEWS_LOGS_TABLE, connect.loads(newsLogs.__dict__))
        
        print(f"paper done: {basename}")

    except Exception as e:
        print(e)
        return
    


    