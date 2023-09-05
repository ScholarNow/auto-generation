import argparse
import concurrent.futures
import json
import os
import shutil
import timeit
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from config import BACKEND_URL, ML_URL
# load_dotenv("./debug.env")
# BACKEND_URL = os.getenv("BACKEND_URL")
# ML_URL = os.getenv("ML_URL")


class SectionEntity(BaseModel):
    section_type: str = ""
    section_name: str = ""
    section_content: str = ""
    keywords: str = ""


def parse_paper(pdf_bites, pdf_name, figures: bool = True):
    parser_start = timeit.default_timer()

    resp = requests.post(
        f"{ML_URL}/api/paper_parser",
        files={"pdf_file": (pdf_name, pdf_bites, "application/pdf")},
        params={"figure_detect": figures},
    )

    parser_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None
    return parser_end - parser_start, result


def parse_crawler(title, keywords):
    crawler_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/paper_crawler", json={"title": title, "keywords": keywords}
    )

    crawler_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None
    return crawler_end - crawler_start, result


def gen_keywords(paper_abstract, verbose: bool = True):
    keywords_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/keyword",
        json={"abstract": paper_abstract},
        params={"verbose": verbose},
    )

    keywords_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None
    return keywords_end - keywords_start, result


def gen_title(paper_abstract, verbose: bool = True):
    title_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/title",
        json={"abstract": paper_abstract},
        params={"verbose": verbose},
    )

    title_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None

    return title_end - title_start, result


def gen_sections(section_entity: SectionEntity, verbose: bool = True):
    sections_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/section",
        json=section_entity.dict(),
        params={"verbose": verbose},
    )

    sections_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 and result["code"] != 200:
        return -1, None

    return sections_end - sections_start, result


def gen_sections_extract(section_entity: SectionEntity, verbose: bool = True):
    sections_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/section/part/points",
        json=section_entity.dict(),
        params={"verbose": verbose},
    )

    sections_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 or result["code"] != 200:
        return -1, None

    return sections_end - sections_start, result


def gen_sections_link(extract_points: str, verbose: bool = True):
    sections_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/section/part/paragraph",
        json={"extracted_points": extract_points},
        params={"verbose": verbose},
    )

    sections_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 or result["code"] != 200:
        return -1, None

    return sections_end - sections_start, result


def gen_section_rephrase(paragraph: str, type: str, verbose: bool = True):
    sections_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/section/part/rephrase",
        json={"section_type": type, "linked_paragraph": paragraph},
        params={"verbose": verbose},
    )

    sections_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 or result["code"] != 200:
        return -1, None

    return sections_end - sections_start, result


def gen_rl(prior_papers, derivative_papers, verbose: bool = True):
    rl_start = timeit.default_timer()

    resp = requests.post(
        f"{BACKEND_URL}/api/gen/related_work",
        json={"prior_papers": prior_papers, "derivative_papers": derivative_papers},
        params={"verbose": verbose},
    )

    rl_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None

    return rl_end - rl_start, result


def gen_gif(images_name: List[str]):
    gif_start = timeit.default_timer()

    resp = requests.post(
        "http://121.4.252.17:8000/api/gen/gif", json={"images_name": images_name}
    )

    gif_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None

    if resp.status_code != 200 and result["code"] != 200:
        return -1, None

    return gif_end - gif_start, result


def gen_related_work(paper_title, paper_keywords, verbose: bool = True):
    related_work_start = timeit.default_timer()

    crawler_time, crawler_result = parse_crawler(paper_title, paper_keywords)

    if crawler_time == -1:
        return -1, None

    gen_rl_time, gen_rl_result = gen_rl(
        crawler_result["data"]["prior_papers"],
        crawler_result["data"]["derivative_papers"],
        verbose,
    )

    if gen_rl_time == -1:
        return -1, None

    related_work_end = timeit.default_timer()

    return related_work_end - related_work_start, gen_rl_result


def gen_sections_verbose(section_entity: SectionEntity, verbose: bool = True):
    sections_start = timeit.default_timer()

    extract_time, extract_result = gen_sections_extract(section_entity, verbose)
    if extract_time == -1:
        return -1, None
    link_time, link_result = gen_sections_link(extract_result["data"], verbose)
    if link_time == -1:
        return -1, None
    rephrase_time, rephrase_result = gen_section_rephrase(
        link_result["data"], section_entity.section_type, verbose
    )

    sections_end = timeit.default_timer()

    if extract_time == -1 or link_time == -1 or rephrase_time == -1:
        return -1, None

    section_token = (
        extract_result["verbose"]["total_tokens"]
        + link_result["verbose"]["total_tokens"]
        + rephrase_result["verbose"]["total_tokens"]
    )

    result = {
        "extract_result": extract_result,
        "link_result": link_result,
        "rephrase_result": rephrase_result,
        "verbose": {
            "total_tokens": section_token,
        },
    }

    return sections_end - sections_start, result


def rephrase_paragraphs(paragraphs: List[str], verbose: bool = True):
    rephrase_start = timeit.default_timer()

    paragraphs = f"{'  '.join(paragraphs)}"

    resp = requests.post(
        f"{BACKEND_URL}/api/rephrase/sections",
        json={"paragraphs": paragraphs},
        params={"verbose": verbose},
    )

    rephrase_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 or result["code"] != 200:
        return -1, None

    return rephrase_end - rephrase_start, result

def animate_figures(figures: List[str]):
    animate_start = timeit.default_timer()

    resp = requests.post(
        f"{ML_URL}/api/figure_animation",
        json={
            "images_name": figures
        }
    )

    animate_end = timeit.default_timer()

    try:
        result = resp.json()
    except Exception:
        return -1, None
    if resp.status_code != 200 or result["code"] != 200:
        return -1, None
    
    return animate_end - animate_start, result

def main_test(test_folder, file, out_folder):
    print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Processing {file} ")
    process_start = timeit.default_timer()
    shutil.copy(os.path.join(test_folder, file), out_folder)
    # read paper
    with open(os.path.join(test_folder, file), 'rb') as f:
        pdf_bites = f.read()
        pdf_name = f.name
    # parse paper
    parse_time, parse_result = parse_paper(pdf_bites, pdf_name)
    if parse_time == -1:
        return {"parse_time": -1}
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
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
    intro_time, intro_result = threads[0].result()
    method_time, method_result = threads[1].result()
    conclusion_time, conclusion_result = threads[2].result()
    related_work_time, related_work_result = threads[3].result()
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
        "parse_result": parse_result,
        "title_result": title_result,
        "keywords_result": keywords_result,
        "intro_result": intro_result,
        "method_result": method_result,
        "conclusion_result": conclusion_result,
        "related_work_result": related_work_result,
        "rephrase_result": rephrase_result,
    }
    with open(
        os.path.join(out_folder, file.replace(".pdf", ".json")),
        'w',
        encoding='utf-8',
    ) as f:
        f.write(json.dumps(process_result))
    return process_result


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--test_folder', type=str, required=True)
    argparser.add_argument('--out', type=str, default='.')
    args = argparser.parse_args()
    test_folder = args.test_folder
    out = args.out
    assert os.path.isdir(test_folder) is True, "test_folder must be a folder"
    base_folder_name = os.path.basename(test_folder)
    base_folder_name = base_folder_name + "_out"
    out_folder = os.path.join(out, base_folder_name)
    os.makedirs(out_folder, exist_ok=True)
    pdf_files = [file for file in os.listdir(test_folder) if file.endswith(".pdf")]
    process_results = []
    threads = []
    total_start = timeit.default_timer()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for file in pdf_files:
            threads.append(executor.submit(main_test, test_folder, file, out_folder))
    for thread in threads:
        process_results.append(thread.result())
    total_end = timeit.default_timer()
    total_time = total_end - total_start
    # visualize time cost
    avg_total_time = 0
    avg_parse_time = 0
    avg_title_time = 0
    avg_keywords_time = 0
    avg_intro_time = 0
    avg_method_time = 0
    avg_conclusion_time = 0
    avg_related_work_time = 0
    avg_rephrase_time = 0
    count = process_results.__len__()
    failed_list = []
    for index, process_result in enumerate(process_results):
        if (
            process_result["parse_time"] == -1
            or process_result["title_time"] == -1
            or process_result["keywords_time"] == -1
            or process_result["intro_time"] == -1
            or process_result["method_time"] == -1
            or process_result["conclusion_time"] == -1
            or process_result["related_work_time"] == -1
            or process_result["rephrase_time"] == -1
        ):
            count -= 1
            failed_list.append(pdf_files[index])
            continue
        avg_total_time += process_result["totle_time"]
        avg_parse_time += process_result["parse_time"]
        avg_title_time += process_result["title_time"]
        avg_keywords_time += process_result["keywords_time"]
        avg_intro_time += process_result["intro_time"]
        avg_method_time += process_result["method_time"]
        avg_conclusion_time += process_result["conclusion_time"]
        avg_related_work_time += process_result["related_work_time"]
        avg_rephrase_time += process_result["rephrase_time"]
    avg_total_time /= count
    avg_parse_time /= count
    avg_title_time /= count
    avg_keywords_time /= count
    avg_intro_time /= count
    avg_method_time /= count
    avg_conclusion_time /= count
    avg_related_work_time /= count
    avg_rephrase_time /= count
    avg_threads1_time = max([avg_title_time, avg_keywords_time])
    avg_threads2_time = max(
        [avg_intro_time, avg_method_time, avg_conclusion_time, avg_related_work_time]
    )

    fig = plt.figure(figsize=(30, 10))
    ax1 = fig.add_subplot(1, 3, 1)
    time_pie = np.array(
        [avg_parse_time, avg_threads1_time, avg_threads2_time, avg_rephrase_time]
    )
    ax1.pie(
        time_pie,
        labels=["parse", "threads1", "threads2", "rephrase"],
        autopct='%1.1f%%',
    )
    ax1.set_title(
        f"avg_total_time: {avg_total_time:.2f}s\n total_time: {total_time:.2f}s"
    )

    ax2 = fig.add_subplot(1, 3, 2)
    time_bar1 = np.array([avg_title_time, avg_keywords_time])
    ax2.bar(range(len(time_bar1)), time_bar1, tick_label=["title", "keywords"])
    ax2.set_title(f"avg_threads1_time: {avg_threads1_time:.2f}s")

    ax3 = fig.add_subplot(1, 3, 3)
    time_bar2 = np.array(
        [avg_intro_time, avg_method_time, avg_conclusion_time, avg_related_work_time]
    )
    ax3.bar(
        range(len(time_bar2)),
        time_bar2,
        tick_label=["intro", "method", "conclusion", "related_work"],
    )
    ax3.set_title(f"avg_threads2_time: {avg_threads2_time:.2f}s")

    plt.savefig(f"{out_folder}/time_result.png")
    plt.show()
    # visualize token cost
    avg_total_token = 0
    avg_title_token = 0
    avg_keywords_token = 0
    avg_intro_token = 0
    avg_method_token = 0
    avg_conclusion_token = 0
    avg_related_work_token = 0
    avg_rephrase_token = 0
    for index, process_result in enumerate(process_results):
        if (
            process_result["parse_time"] == -1
            or process_result["title_time"] == -1
            or process_result["keywords_time"] == -1
            or process_result["intro_time"] == -1
            or process_result["method_time"] == -1
            or process_result["conclusion_time"] == -1
            or process_result["related_work_time"] == -1
        ):
            continue
        avg_title_token += process_result["title_result"]["verbose"]["total_tokens"]
        avg_keywords_token += process_result["keywords_result"]["verbose"][
            "total_tokens"
        ]
        avg_intro_token += process_result["intro_result"]["verbose"]["total_tokens"]
        avg_method_token += process_result["method_result"]["verbose"]["total_tokens"]
        avg_conclusion_token += process_result["conclusion_result"]["verbose"][
            "total_tokens"
        ]
        avg_related_work_token += process_result["related_work_result"]["verbose"][
            "total_tokens"
        ]
        avg_rephrase_token += process_result["rephrase_result"]["verbose"][
            "total_tokens"
        ]
    avg_title_token /= count
    avg_keywords_token /= count
    avg_intro_token /= count
    avg_method_token /= count
    avg_conclusion_token /= count
    avg_related_work_token /= count
    avg_total_token = (
        avg_title_token
        + avg_keywords_token
        + avg_intro_token
        + avg_method_token
        + avg_conclusion_token
        + avg_related_work_token
        + avg_rephrase_token
    )
    fig = plt.figure(figsize=(10, 10))
    token_label = [
        "title",
        "keywords",
        "intro",
        "method",
        "conclusion",
        "related_work",
        "rephrase",
    ]
    token_datas = [
        avg_title_token,
        avg_keywords_token,
        avg_intro_token,
        avg_method_token,
        avg_conclusion_token,
        avg_related_work_token,
        avg_rephrase_token,
    ]
    plt.bar(token_label, token_datas, color='blue', width=0.5)
    plt.title(
        f"avg_total_token: {avg_total_token:.2f} with $0.002/1K tokens.\navg_cost: {avg_total_token * 0.002 * 0.001:.4f}$"
    )
    plt.savefig(f"{out_folder}/token_result.png")
    plt.show()
    with open(f"{out_folder}/result.json", 'w') as f:
        f.write(
            json.dumps(
                {
                    "total_time": total_time,
                    "avg_total_time": avg_total_time,
                    "avg_parse_time": avg_parse_time,
                    "avg_title_time": avg_title_time,
                    "avg_keywords_time": avg_keywords_time,
                    "avg_intro_time": avg_intro_time,
                    "avg_method_time": avg_method_time,
                    "avg_conclusion_time": avg_conclusion_time,
                    "avg_related_work_time": avg_related_work_time,
                    "failed_list": failed_list,
                    "avg_total_token": avg_total_token,
                    "avg_title_token": avg_title_token,
                    "avg_keywords_token": avg_keywords_token,
                    "avg_intro_token": avg_intro_token,
                    "avg_method_token": avg_method_token,
                    "avg_conclusion_token": avg_conclusion_token,
                    "avg_related_work_token": avg_related_work_token,
                    "avg_rephrase_token": avg_rephrase_token,
                }
            )
        )
