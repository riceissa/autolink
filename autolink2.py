
def soup2dict(soup, url=""):
    """
    Extract info from a BeautifulSoup soup into a dictionary.  Return a new
    dictionary containing metadata fields.
    """
    result = dict()
    if url:
        result["url"] = url

def markdown_citation(dictionary, reference_style=False):
    pass

def markdown_hyperlink(dictionary):
    pass

def mediawiki_citation(dictionary):
    pass

def mediawiki_hyperlink(dictionary):
    pass

if __name__ == "__main__":
    main()
