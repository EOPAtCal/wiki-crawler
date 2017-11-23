import re


def is_not_tag_link(link):
    return 'system:page-tags/tag/' not in link


def is_not_an_attachment_link(link):
    attachments = ['.pdf', '.doc', '.docx']
    for i in attachments:
        if i in link:
            return False
    return True


def is_not_javascript_link(link):
    return 'javascript' not in link


def is_wiki_link(link):
    return 'http://eop.wikidot.com/' in link


def clean_links(link, patterns):
    for pattern in patterns:
        link = clean_link(link, pattern)
    return link


def clean_link(link, pattern):
    return re.sub(pattern, "", link)


def print_a_line():
    print "#" * 80
