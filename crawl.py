from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from collections import deque
from collections import OrderedDict
import json
import os
import shutil
from utils import *


def dir_join(dir, files):
    return map(lambda f: os.path.join(dir, f), files)


# global vars
driver = None
base_url = "https://www.wikidot.com"
canary_path = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
num_pages = 0
g_visited_links, g_failed_links = [], []
g_path = {}

# directories
logs = "logs"
files = "files"
screenshots = "screenshots"

# files
bfs_success, dfs_success = dir_join(
    logs, ["visited-links.bfs", "visited-links.dfs"])

bfs_fail, dfs_fail = dir_join(
    logs, ["failed-links.bfs", "failed-links.dfs"])

bfs_path, dfs_path = dir_join(
    logs, ["path.bfs", "path.dfs"])


def setup_dirs():
    dirs = [files, logs, screenshots]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            shutil.rmtree(dir)
            os.makedirs(dir)


def initialize_drivers(mode):
    global driver
    if mode == "head":
        driver = webdriver.Chrome()
    else:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = canary_path
        driver = webdriver.Chrome(
            executable_path='/usr/local/bin/chromedriver',
            chrome_options=chrome_options)
    print "%s mode selected" % mode

    driver.set_window_size(1920, 1080)
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
    driver.implicitly_wait(5)

    setup_dirs()


def run(search):
    print "%s search selected" % search
    try:
        driver.get(base_url)
        assert "wikidot" in driver.title.lower()
        driver.find_element_by_css_selector(
            ".loginStatus > .login-status-sign-in").click()
        driver.switch_to_window(driver.window_handles[1])
        username_input = driver.find_element_by_css_selector(
            "input[name=login]")
        password_input = driver.find_element_by_css_selector(
            "input[name=password]")
        username, password = get_username_and_password()
        assert username and password
        username_input.send_keys(username)
        password_input.send_keys(password)
        driver.find_element_by_css_selector("button[type=submit]").click()
        driver.switch_to_window(driver.window_handles[0])
        driver.find_element_by_css_selector("div.button > a").click()
        driver.find_element_by_css_selector("li.tab.sites > a").click()
        driver.find_element_by_link_text("EOPKI").click()
        driver.switch_to_window(driver.window_handles[1])

        main = get_main_content_elem()
        f_name = base_url
        write_to_file(get_main_content(main), f_name)
        write_to_file(get_main_html(main), f_name, False)

        links = get_all_links(main)
        wiki_links = get_all_wiki_links(links)
        print "Begin..\n"
        if search == "dfs":
            parse_dfs(wiki_links)
        else:
            parse_bfs(wiki_links)
    except Exception as e:
        print str(e)
        driver.save_screenshot("screenshots/error.png")
    finally:
        try:
            driver.save_screenshot("screenshots/final.png")
            driver.close()
            driver.quit()
        except Exception as e:
            print str(e)


def parse(link):
    driver.get(link)
    main_element = get_main_content_elem()
    wiki_links = []
    if main_element:
        links = get_all_links(main_element)
        wiki_links = get_all_wiki_links(links)
        f_name = link.split('.com/')[1]
        write_to_file(get_main_content(main_element), f_name)
        write_to_file(get_main_html(main_element), f_name, False)
        print "wrote to file %s" % f_name
    else:
        print "could not extract content from %s" % link
    return wiki_links


def update_pages(url):
    global num_pages
    num_pages += 1


def parse_dfs(wiki_links):
    print "dfs traversal started..."
    fringe = wiki_links
    visited = []
    setup_paths(wiki_links)
    while fringe:
        url = fringe.pop()
        urls = parse(url)
        visited.append(url)
        update_pages(url)
        for u in urls:
            if u not in visited:
                fringe.append(u)
                append_parent_path(u, url)

    print "dfs traversal complete"


def parse_bfs(wiki_links):
    print "bfs traversal started..."
    fringe = deque()
    map(fringe.append, wiki_links)
    visited = []
    global g_path
    setup_paths(wiki_links)
    while fringe:
        url = fringe.popleft()
        if url not in visited:
            urls = parse(url)
            visited.append(url)
            update_pages(url)
            for u in urls:
                fringe.append(u)
                append_parent_path(u, url)

    print "bfs traversal complete"


def get_main_html(main_elem):
    remove_unwanted_elems_by_id([
        "action-area-top",
        "page-info-break",
        "page-options-container",
        "action-area"
    ])
    return get_inner_html(main_elem)


def remove_unwanted_elems_by_id(elems):
    for elem in elems:
        try:
            driver.execute_script("""
                var main = document.getElementById('main-content');
                return main.removeChild(document.getElementById(arguments[0]))
                """, elem)
        except Exception:
            print "could not remove %s" % elem


def get_inner_html(elem):
    return elem.get_attribute('innerHTML')


def get_main_content_elem():
    return driver.find_element_by_id("main-content")


def get_main_content(elem):
    return get_title(elem) + get_body(elem)


def get_title(elem):
    result = ""
    try:
        result = elem.find_element_by_id("page-title").text + "\n"
        log_link_success(driver.current_url)
    except Exception as e:
        print "Error" + str(e)
        log_link_fail(driver.current_url)
    finally:
        return result


def get_body(elem):
    result = ""
    try:
        result = elem.find_element_by_id("page-content").text
        log_link_success(driver.current_url)
    except Exception as e:
        print "Error: " + str(e)
        log_link_fail(driver.current_url)
    finally:
        return result


def append_parent_path(url, parent):
    global g_path
    g_path.update({
        url: g_path[parent] + " > " + parent
    })


def setup_paths(wiki_links):
    map(lambda link: g_path.update({link: " / "}), wiki_links)


def get_all_wiki_links(links):
    return filter(lambda x: is_wiki_link(x), links)


def get_all_links(elem):
    return extract_link_sources(elem.find_elements_by_tag_name('a'))


def extract_link_sources(elems):
    return filter_links(map(lambda elem: elem.get_attribute('href'), elems))


def filter_links(links):
    return filter(lambda link: is_not_tag_link(link),
                  filter(lambda link: is_not_an_attachment_link(link),
                         filter(lambda link: is_not_javascript_link(link), links)
                         )
                  )


def write_to_file(content, filename, txt=True):
    content = content.encode('ascii', 'ignore')
    filename = check_filename(filename)
    if txt:
        f_path = files + '/' + filename + '.txt'
    else:
        f_path = files + '/' + filename + '.html'
    with open(f_path, "w") as f:
        f.write(content)
        f.close


def write_array_to_file(arr, filename, sort=True):
    arr = set(arr)
    if sort:
        arr = sorted(arr)
    with open(filename, 'w') as f:
        for item in arr:
            f.write("%s\n" % item)


def write_dict_to_file(d, filename):
    d = OrderedDict(sorted(d.items()))
    with open(filename, 'w') as f:
        for key, value in d.iteritems():
            f.write("%s : %s\n" % (key, value))


def check_filename(filename):
    filename_exceptions = ['/']
    for i in filename:
        if i in filename_exceptions:
            return filename.split(i)[0]
    return filename


def get_username_and_password():
    with open('secrets.json') as secrets:
        f = json.load(secrets)
        return f["username"], f["password"]


def log_link_success(link):
    global g_visited_links
    g_visited_links.append(link)


def log_link_fail(link):
    global g_failed_links
    g_failed_links.append(link)


def log_results(search):
    if g_visited_links:
        f_name = dfs_success if search == "dfs" else bfs_success
        write_array_to_file(g_visited_links, f_name)
        print "wrote visted links to file %s" % f_name
    if g_failed_links:
        f_name = dfs_fail if search == "dfs" else bfs_fail
        write_array_to_file(g_failed_links, f_name)
        print "wrote failed links to file %s" % f_name
    if g_path:
        f_name = dfs_path if search == "dfs" else bfs_path
        write_dict_to_file(g_path, f_name)
        print "wrote failed links to file %s" % f_name


def main(mode="headless", search="bfs"):
    print "Starting setup..."
    initialize_drivers(mode)
    run(search)
    print "%d pages have been written" % num_pages
    log_results(search)
    print_a_line()
