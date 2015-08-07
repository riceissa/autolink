#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import requests
import urllib3
import tld
from tld import get_tld
from bs4 import BeautifulSoup
import html

def main():
    # See https://blog.quora.com/Launched-Customizable-Links for Quora's launch post
    parser = argparse.ArgumentParser(description=("Get the linked title of " +
        "URLs (similar to Quora and Facebook)"))
    parser.add_argument("url", type=str, help="the URL")
    parser.add_argument("-v", "--verbose", action="store_const",
        dest="log_level", const=logging.DEBUG, help="enable debug messages")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    url = args.url
    logging.debug("Trying first attempt")
    attempt_1 = try_url(url)
    if attempt_1["exit"]:
        logging.debug("First attempt succeeded!")
        print(attempt_1["text"], end="")
    else:
        logging.debug("First attempt failed; trying second attempt")
        attempt_2 = try_url("http://" + url)
        if attempt_2["exit"]:
            print(attempt_2["text"], end="")
        else:
            print(attempt_1["text"], end="")

def try_url(url):
    '''
    Return (Str, True) if succeeded; (Str, False) otherwise.
    '''
    result = {}
    analyte = analyze_url(url)
    if analyte:
        return {"text": analyte, "exit": True}
    try:
        user_agent = ("Mozilla/5.0 (X11; Linux i686; rv:31.0) Gecko/20100101 " +
            "Firefox/31.0 Iceweasel/31.5.0")
        headers = {"User-Agent": user_agent}
        response = requests.get(url, stream=True, headers=headers)
        url = response.url
        if  "text/html" in response.headers["content-type"]:
            # <title> is probably in the first around 10MB
            doc = response.iter_content(chunk_size=10000)
            data = next(doc)
            result["text"] = get_filetype_link(
                get_link_text(url, response.headers["content-type"], data=data),
                url,
                "markdown"
            )
        else:
            result["text"] = get_filetype_link(
                get_link_text(url, response.headers["content-type"]),
                url,
                "markdown"
            )
        result["exit"] = True
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema, urllib3.exceptions.LocationParseError):
        result["text"] = "[{url}]({url})".format(url=url)
        result["exit"] = False
    return result

def analyze_url(url):
    """
    Look just at the URL to see if a suitable title text can be found.  This
    method is much faster than actually visiting the URL to find the title
    element in the downloaded file. We want to do this for special sites like
    Facebook, which doesn't allow anonymous downloading of certain pages, like
    group pages.

    Args:
        url: A string that is a URL

    Returns:
        A string that is the title text to be used. If no suitable title text
        can be produced, return the empty string, "".
    """
    try:
        tl = get_tld(url)
    except tld.exceptions.TldBadUrl:
        try:
            tl = get_tld("http://" + url)
        except tld.exceptions.TldBadUrl:
            return ""
    if tl == "facebook.com" and "facebook.com/groups/" in url:
            return "Facebook group page post"
    return ""

def get_filetype_link(link_text, url, filetype):
    """
    Put the pieces together and produce a valid hyperlink for given output
    filetype.

    Args:
        link_text: A string representing the displayed or linked text when
            linking to something, e.g. "hello" in <a
            href="http://example.org">hello<a>. This string should already be in
            the intended form; i.e. all HTML escapes should have been unescaped
            at this point.
        url: A string of the URL.
        filetype: A string of the output filetype. Accepted parameters are:
            "html", "markdown", "latex".

    Returns:
        A string that is a valid hyperlink for the specified output filetype.
    """
    if filetype == "markdown":
        # From http://pandoc.org/README.html#backslash-escapes
        special_chars = "\\`*_{}[]()>#+-.!"
        result = ""
        for c in link_text:
            if c in special_chars:
                result += "\\" + c
            else:
                result += c
        return "[{link_text}]({url})".format(link_text=result, url=url)
    if filetype == "html":
        return '<a href="{url}">{link_text}</a>'.format(url=url, link_text=html.escape(link_text))
    if filetype == "mediawiki":
        return "[{url} {link_text}]".format(url=url, link_text=link_text)

def get_link_text(url, mime_type, data=None):
    '''
    Take URL, MIME type, and optional data to produce the link text.
    '''
    tld = get_tld(url)
    result = "File on " + tld
    if mime_type.startswith("image"):
        result = "Image on " + tld
    elif mime_type == "application/pdf":
        result = "PDF on " + tld
    elif "text/html" in mime_type:
        try:
            soup = BeautifulSoup(data, 'html.parser')
            meta = soup.find_all("meta")
            possible = [i.get("content") for i in meta if i.get("property") == "og:title"]
            if possible:
                result = possible[0].strip()
            elif soup.title.string:
                result = messy_title_parse(soup.title.string)
            else:
                result = "Page on " + tld
        except AttributeError:
            # Probably just empty title when trying to get
            # soup.title.string
            result = "Page on " + tld
    if len(result) > 255:
        result = result[:253] + " …"

    return result

def messy_title_parse(title, url=None):
    # Even if nothing works, at least we'll have a whitespace-sanitized
    # title
    result = title.strip()
    hyphen_split = result.split(" - ")
    bar_split = result.split(" | ")
    em_dash_split = result.split(" — ")
    colon_split = result.split(": ")
    if len(hyphen_split) > 1:
        # So there is actually more than one part, so we just take the
        # first and we're done.  This is for titles like "Post Title -
        # Site Name"
        result = hyphen_split[0]
    elif len(em_dash_split) > 1:
        result = em_dash_split[0]
    elif len(bar_split) > 1:
        result = bar_split[0]
    elif len(colon_split) > 1:
        # For titles like "Site Name: Post Title"
        result = colon_split[-1]
    return result

if __name__ == "__main__":
    main()
