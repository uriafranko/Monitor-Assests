import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests
from bs4 import BeautifulSoup
from mailer import Mailer

mailer = Mailer(os.environ['TARGET_URL'], os.environ['SOURCE_EMAIL'], os.environ['DESTINATION_URL'],)
internal_urls = set()
external_urls = set()


def multi_threading(func, args, workers):
    with ThreadPoolExecutor(workers) as ex:
        res = ex.map(func, args)
    return list(res)


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def check_status(url):
    global mailer
    resp = requests.get(url)
    if resp.status_code > 399:
        mailer.assets.append(url)


def request_url(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.ConnectTimeout as err:
        errors = ['Connection timed out to your target']
        mailer.send_errors(errors)
        return False
    except requests.exceptions.ConnectionError as err:
        errors = [err]
        mailer.send_errors(errors)
        return False
    except requests.exceptions.HTTPError as err:
        errors = [f'Your target raised <strong>{response.status_code}</strong> status code']
        mailer.send_errors(errors)
        return False
    return soup


def get_all_website_links(url):
    urls = set()
    url_parsed = urlparse(url)
    domain_name = url_parsed.netloc
    soup = request_url(url)
    if soup is False:
        return False
    for a_tag in soup.findAll(["a", "link", "img", "script"]):
        source = 'src'
        if a_tag.name == "a" or a_tag.name == "link":
            source = 'href'
        href = a_tag.attrs.get(source)
        if href == "" or href is None or '#' in href:
            continue
        parsed_href = urlparse(href)
        if parsed_href.netloc == "":
            if href[0] == "/":
                href = url_parsed.scheme + "://" + domain_name + href
            else:
                href = url_parsed.scheme + "://" + domain_name + "/" + href
        if not is_valid(href):
            continue
        if href in internal_urls:
            continue
        if domain_name not in href:
            if href not in external_urls:
                external_urls.add(href)
            continue
        urls.add(href)
        internal_urls.add(href)
    return urls


def main(event, context):
    crawled_links = get_all_website_links(os.environ['TARGET_URL'])
    if crawled_links is False:
        response = {
            "statusCode": 500,
            "body": "Error raised trying to get the target"
        }
        return response
    multi_threading(check_status, crawled_links, 20)
    mailer.send_mail()
    response = {
        "statusCode": 200,
    }
    return response
