import sys
import re
import codecs
import os

def get_author(content):
    pattern = r'<META NAME="AUTOR" CONTENT="(.*?)">'
    r = re.compile(pattern, re.S)
    m = r.search(content)
    return m.group(1) if m is not None else 'undefined'


def get_section(content):
    pattern = r'<META NAME="DZIAL" CONTENT="(.*?)">'
    r = re.compile(pattern, re.S)
    m = r.search(content)
    return m.group(1) if m is not None else 'undefined'


def get_key_words(content):
    pattern = r'<META NAME="KLUCZOWE_\d+" CONTENT="(.*?)">'
    r = re.compile(pattern, re.S)
    return r.findall(content)


def get_content_p_to_meta(content):
    pattern = r'.*?<P.*?>(.*?)<META'
    r = re.compile(pattern, re.S)
    m = r.match(content)
    return m.group(1) if m is not None else 'undefined'

def get_number_of_integers(content):
    positive = r'[0-9]|[1-9]\d{1,3}|[1-2]\d{4}|3[0-1]\d{3}|32[0-6]\d{2}|327[0-5]\d|3276[0-7]'
    negative = r'-32768|-(?:' + positive + ')'
    integer = r'(?<!\d|\.|-|/)(' + negative + r'|' + positive + r')(?!\d|\.|-|/)'
    r = re.compile(integer)
    return set(r.findall(content))


def get_number_of_floats(content):
    before_dot = r'(?:0|[1-9]\d*)'
    after_dot = r'(?:\d+)'
    e_notation = r'e(?:\+|-)(?:[0-9]|[1-9]\d*)'
    number_with_e =  before_dot + r'?' + r'\.' + after_dot + e_notation
    number_without_e = ''
    number_without_e += before_dot + r'\.' + after_dot + r'?' + r'|'
    number_without_e += before_dot + r'?' + r'\.' + after_dot

    floats = r'(?<!\d|\.|-|/)(-?(?:' + number_with_e + r'|' + number_without_e + r'))(?!\d|\.|-|/)'

    r = re.compile(floats, re.S)
    return set(r.findall(content))


def get_emails(content):
    pattern = r"""(?<=\s|"|'|\(|\[|<|>)""" + r'((?:\w+\.)+\w+@\w+(?:\.\w+)+)' + r"""(?=\s|"|'|\)|\[|<|>)"""
    r = re.compile(pattern, re.S)
    return set(r.findall(content))


def get_shortcuts(content):
    pattern = r'(?<=\s|>)[a-zA-Z]{1,3}\.(?=\s|<)'
    r = re.compile(pattern)
    return set(r.findall(content))


def get_number_of_dates(content):
    def number(number): # generate regex matching 2-digt number between 01 and number
        n1, n2 = number/10, number%10
        result = '0[1-9]|'
        result += r'[1-' + str(n1-1) + r'][0-9]|'
        result += str(n1) + r'[0-' + str(n2) + r']'
        result = r'(?:' + result + r')'
        return result

    max_days = [
        (r'(?:01|03|05|07|08|10|12)', 31),
        (r'(?:04|06|09|11)', 30),
        (r'02', 29)
    ]

    # year = r'(?:[0-9]|[1-9]\d{1,3})'
    year = r'\d{4}'
    separators = [r'-', r'/', r'\.']

    date = ''
    for separator in separators:
        for (months, days) in max_days:
            date += number(days) + separator + months + separator + year + r'|'
            date += year + separator + number(days) + separator + months + r'|'

    date = date[:-1]

    pattern = r'(?<!\.|-|/|\d)(' + date + r')(?!\.|-|/|\d)'
    r = re.compile(pattern, re.S)
    results = r.findall(content)
    return get_unique_date(results)

def get_unique_date(dates):
    dates_set = set([])
    for date in dates:
        split_date = re.split(r'\.|-|/', date)
        if len(split_date[0]) == 4:
            dates_set.add((split_date[1], split_date[2], split_date[0]))
        else:
            dates_set.add(tuple(split_date))
    return dates_set

def get_number_of_sentences(content):
    # not checked
    pattern = r'([A-Za-z]{4}(?:(?:\.|\?|!)+|(?:<.+?>)*\s*\n))'
    r = re.compile(pattern)
    return r.findall(content)


def processFile(file_path):
    fp = codecs.open(file_path, 'rU', 'iso-8859-2')

    content = fp.read()
    p_to_meta_content = get_content_p_to_meta(content)


    fp.close()
    print "nazwa pliku:", file_path
    print "autor:", get_author(content)
    print "dzial:", get_section(content)
    print "slowa kluczowe:", get_key_words(content)
    print "liczba zdan:", len(get_number_of_sentences(p_to_meta_content))
    print "liczba skrotow:", len(get_shortcuts(p_to_meta_content))
    print "liczba liczb calkowitych z zakresu int:", len(get_number_of_integers(p_to_meta_content))
    print "liczba liczb zmiennoprzecinkowych:", len(get_number_of_floats(p_to_meta_content))
    print "liczba dat:", len(get_number_of_dates(p_to_meta_content))
    print "liczba adresow email:", len(get_emails(p_to_meta_content))
    print "\n"


try:
    path = sys.argv[1]
except IndexError:
    print("Brak podanej nazwy pliku")
    sys.exit(0)

tree = os.walk(path)

for root, dirs, files in tree:
    for f in files:
        if f.endswith(".html"):
            filepath = os.path.join(root, f)
            processFile(filepath)

