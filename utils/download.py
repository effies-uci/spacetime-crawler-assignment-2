import requests
import cbor
import time
from threading import Lock
from tldextract import extract

from utils.response import Response

recently_requested = set()
domain_mutex = Lock()

def download(url, config, logger=None, time_delay = 1):
    host, port = config.cache_server

    ext = extract(url)
    domain = ext.fqdn

    # concurrency safety
    domain_mutex.acquire(True)

    if domain in recently_requested:
        domain_mutex.release()
        return None

    recently_requested.add(domain)
    domain_mutex.release()

    if logger:
        logger.info(f"Getting logs from {url}")

    while True:
        try:
            resp = requests.get(
                f"http://{host}:{port}/",
                params=[("q", f"{url}"), ("u", f"{config.user_agent}")], timeout=2)
            break
        except requests.exceptions.Timeout:
            if logger:
                logger.error("Get request timed out. Attempting again in 5 seconds.")
            time.sleep(5)

    try:
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
    except (EOFError, ValueError) as e:
        pass
    finally:
        # sleep to ensure that no other thread queries the domain
        # within the politeness delay
        time.sleep(time_delay)
        with domain_mutex:
            recently_requested.remove(domain)
    if logger:
        logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
