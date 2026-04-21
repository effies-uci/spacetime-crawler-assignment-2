import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlencode, parse_qsl

ALLOWED_DOMAINS = {"www.ics.uci.edu","www.cs.uci.edu","www.informatics.uci.edu","www.stat.uci.edu"}
PATTERN_THRESHOLD = 10

visited = set()
pattern_count = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    url_list = []

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return url_list
    
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        html_links = soup.findAll('a', href=True)

        for tag in html_links:
            # get link in href
            href = tag["href"].strip()

            # resolves any relative paths
            absolute_url = urljoin(resp.raw_response.url, href)

            # get rid of any fragments
            defragged = absolute_url.split('#')[0]

            normalize = normalize_url(defragged)
            if is_valid(normalize) and normalize not in visited:
                visited.add(defragged)
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

def normalize_url(url):
    """
    sorts the url's query
    use returned url to check with other urls
    """

    parsed = urlparse(url)

    # qsl so not to lose duplicate query keys
    sorted_query = urlencode(sorted(parse_qsl(parsed.query)))
    normalize = parsed._replace(query=sorted_query).geturl()
    return normalize.rstrip("/")

def get_url_pattern(url):
    parsed = urlparse(url)
    gen_path = re.sub(r'\d+', "NUM", parsed.path)
    gen_path = re.sub(r'[a-f0-9]{8,}', "HASH", gen_path)
    return parsed.netloc + gen_path

def is_trap(url):
    """catches same patterned paths"""

    pattern = get_url_pattern(url)
    pattern_count[pattern] += 1
    return pattern_count[pattern] > PATTERN_THRESHOLD


#### Validity checker :3 ##################################################

def is_valid(url):
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
        normalize = normalize_url(url)
        if normalize in visited:
            return False
        
        visited.add(normalize)

        # check if url is a trap
        if is_trap(url):
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
