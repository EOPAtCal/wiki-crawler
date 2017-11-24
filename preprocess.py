from bs4 import BeautifulSoup
import re
import os
import shutil
from utils import *

source_dir = "files"
results_dir = "clean"
base_url = "https://ce3-wiki.herokuapp.com/"
wiki_url = "http://eop.wikidot.com/"


def setup_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        shutil.rmtree(directory)
        os.makedirs(directory)


def trim_link(link):
    result = link
    try:
        result = base_url + link.split(wiki_url)[1]
    except Exception:
        print "unable to trim %s" % link
    finally:
        return result


def remove_targetblank(a):
    target = a.get("target")
    if target and target == "_blank":
        a["target"] = "_self"


def ensure_targetblank(a):
    target = a.get("target")
    if target:
        if target != "_blank":
            a["target"] = "_blank"
    else:
        a["target"] = "_blank"


def array_subtract(big, small):
    results = big
    for item in small:
        results.remove(item)
    return results


def clean_link(a):
    a["href"] = a.get("href").strip("/")


def clean_links(links):
    return map(lambda a: clean_link(a), links)


def main():
    print "Setting up directory"
    setup_dir(results_dir)
    counter = 0
    for f_name in os.listdir(source_dir):
        if f_name.endswith(".html"):
            with open(os.path.join(source_dir, f_name), 'r') as f:
                soup = BeautifulSoup(f, 'html5lib')
                f.close()

            all_links = soup.find_all('a')
            clean_links(all_links)
            wiki_links = soup.find_all('a', href=re.compile(wiki_url))

            for link in wiki_links:
                link['href'] = trim_link(link['href'])
                link = remove_targetblank(link)

            all_links = soup.find_all('a')
            external_links = array_subtract(all_links, wiki_links)
            map(lambda link: ensure_targetblank(link), external_links)

            soup.html.unwrap()
            soup.head.unwrap()
            soup.body.unwrap()

            result_path = os.path.join(results_dir, f_name)
            with open(result_path, 'w') as f:
                print "wrote to file %s" % f_name
                f.write(soup.prettify('ascii'))
            counter += 1
    print "%d files written. Preprocess complete!" % counter
    print_a_line()
