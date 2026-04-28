import re
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlencode, parse_qsl
import tldextract

from nltk.corpus.reader.markdown import comma_separated_string_args

import reports
from tokenizer import tokenize_html, count_words

ALLOWED_DOMAINS = {"www.ics.uci.edu","www.cs.uci.edu","www.informatics.uci.edu","www.stat.uci.edu",
                   "ics.uci.edu"}
BANNED_LIST = {"https://ics.uci.edu/~eppstein/pix/"}

TRAP_REGEX = [".*grape.ics.uci.edu.*version=.*",
              ".*ics.uci.edu/~wscacchi/presentations/.*",
              ".*ics.uci.edu/~wscacchi/papers/.*",
              ".*grape.ics.uci.edu.*/zip-attachment/.*",
              ".*grape.ics.uci.edu.*/raw-attachment/.*",
              ".*grape.ics.uci.edu.*/attachment/.*",
              ".*grape.ics.uci.edu.*/timeline.*",
              ".*flamingo.ics.uci.edu.*/src/.*",
              ".*ics.uci.edu/~peymano/dynamic-arch/.*index.htm",
              r".*sld\d{3}.htm",
              ".*/events/.*", ".*/makefile", ".*format=txt.*",
              ".*action=history.*", ".*/gitignore", ".*/doku.php/.*"]

#########################################
visited = set()

unique_urls: set = set()
word_freq: dict = defaultdict(int)
page_lens: dict = dict() # url key, value int
unique_subdomains: dict = defaultdict(int)
compiled_regex: list[re.Pattern] = list()

#########################################

def scraper(url, resp, logger = None):
    """called by crawler for each fetched page. returns only valid links"""
    links = extract_next_links(url, resp, logger)
    return [link for link in links if is_valid(link, logger)]

def extract_next_links(url, resp, logger = None):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    """
    returns any subdomains found in link. does NOT check if valid (thats in the scraper !!!)
    
    1. defrag and normalize link
    2. add to unique_urls
    3. check if this page is the longest page (compared to previously visited ones)
    4. add word frequencies
    5. find the <a> tags, defrag and normalize, add to url_list
    
    """

    url_list = []

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        if logger:
            logger.info('raw response is None' if not resp.raw_response else 'raw response exists')
        return url_list

    if logger:
        logger.info('response exists!')

    try:
        content = resp.raw_response.content
        actual_url = resp.raw_response.url

        canonical_url = defrag_and_normalize(actual_url)

        if logger:
            logger.info(f"extracting url {canonical_url}")

        # add link to unique links
        unique_urls.add(canonical_url)

        # get word count
        page_lens[canonical_url] = count_words(content)

        # word frequency
        page_word_freq = defaultdict(int)
        for token in tokenize_html(content):
            page_word_freq[token] += 1
            word_freq[token] += 1

        # find subdomain
        unique_subdomains[tldextract.extract(canonical_url).subdomain] += 1

        # write to report
        reports.write_page_report(page_word_freq, canonical_url)

        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        html_links = soup.findAll('a', href=True)

        for tag in html_links:
            # get link in href
            href = tag["href"].strip()

            # resolves any relative paths
            absolute_url = urljoin(resp.raw_response.url, href)

            # get rid of any fragments
            defragged = defrag_and_normalize(absolute_url)

            url_list.append(defragged)

    except Exception as e:
        print(f'Error parsing {url}:{e}')

    return url_list

#### Helpers :D #############################################################

def defrag_and_normalize(url):
    """
    removes fragments, sorts the query params, strips trailing slash
    """

    parsed = urlparse(url)

    no_frag = url.split('#')[0]
    parsed = urlparse(no_frag)

    # qsl so not to lose duplicate query keys
    sorted_query = urlencode(sorted(parse_qsl(parsed.query)))
    normalize = parsed._replace(query = sorted_query).geturl()

    return normalize.rstrip('/')

def get_url_pattern(url):
    parsed = urlparse(url)
    gen_path = re.sub(r'\d+', "NUM", parsed.path)
    gen_path = re.sub(r'[a-f0-9]{8,}', "HASH", gen_path)
    return parsed.netloc + gen_path

def is_trap(url, logger = None):
    """
    more detailed regex-based trap detection
    """

    if not compiled_regex:
        if logger:
            logger.info("Compiling regex for the first time.")
        for trap in TRAP_REGEX:
            compiled_regex.append(re.compile(trap, re.IGNORECASE))

    for pattern in compiled_regex:
        if pattern.match(url):
            return True

    return False

def in_ban_list(parse_url):
    for ban_url in BANNED_LIST:
        if parse_url.startswith(ban_url):
            return True

    return False


#### Validity checker :3 ##################################################

def is_valid(url, logger = None):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # check if valid domain
        if not any(
            parsed.netloc == domain or
            parsed.netloc.endswith("." + domain) 
            for domain in ALLOWED_DOMAINS):
            
            return False
        
        # check if we already visited
        normalize = defrag_and_normalize(url)
        if normalize in unique_urls:
            return False
        
        # check if url is a trap
        if is_trap(url, logger):
            return False

        if in_ban_list(url):
            return False

        # page content hashing here maybe idk lololol?

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ova"
              r"|py|h|cc|zip|dirs|path|cpp|tgz|defs|txt"
              r"|sh|svg|cls|fig|java|sql|war|xml|conf|class)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except ValueError:
        print ("ValueError for ", parsed)
        raise
