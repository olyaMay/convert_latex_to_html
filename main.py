import re
import glob
import dominate

from dominate.tags import *

def clear_file(file):
    file = re.sub(r'[^\\]?%.*\n', '', file)
    file = file.replace('~', ' ')
    file = file.replace('<<', '"')
    file = file.replace('>>', '"')
    file = file.replace('<', '\\lt')
    file = file.replace('>', '\\gt')
    file = file.replace('---', '-')
    file = file.replace('\clearpage', '')
    file = file.replace('{\\bf', '')
    file = file.replace('\medskip', '')
    file = file.replace('\smallskip', '')
    file = file.replace('\hspace*{1cm}', '  ')
    file = file.replace('\{', '{')
    file = file.replace('\}', '}')
    file = file.replace('newpage', '')
    # удалить картинки
    # заменить ссылки
    return file.replace('\\_', '_')


def make_file_for_article():
    file_for_article = open('fileForArticle.txt', 'w')
    for s in article_clear:
        file_for_article.write(s)
    file_for_article.close()
    return open('fileForArticle.txt', 'r')


def make_text_begin_end(key):
    file_for_article = make_file_for_article()
    text = ''
    flag = 0
    for line in file_for_article:
        if flag == 1 and (line.__contains__('\\section') or line.__contains__('\\begin{thebibliography}')):
            flag = 0
        if flag == 1:
            text += str(line)
        if line.__contains__('\\section*{'+key+'}'):
            flag = 1
    return text


def make_text(keys):
    file_for_article = make_file_for_article()
    text = ''
    flag = 0
    current_key = 0
    for line in file_for_article:
        if flag == 1 and line.__contains__('\\section'):
            flag = 0
            text += ' >'
        if flag == 1:
            text += str(line)
        if line.__contains__('\\section{'+keys[current_key]+'}'):
            flag = 1
            if (current_key + 1) != keys.__len__():
                current_key += 1
    return text


def pretty_text_begin_end(text):
    text_list = []
    last_letter = ''
    line = ''
    flag = 0
    for t in text:
        if t.__eq__('\n'):
            if (not last_letter.__eq__('.')) or last_letter.__eq__(''):
                flag = 0
                line += ' '
            elif flag >= 1:
                pass
            else:
                text_list.append(line)
                flag = 1
                line = ''
        else:
            flag = 0
            line += t
        last_letter = t
    return text_list


def pretty_text(text):
    text_list = []
    last_letter = ''
    line = ''
    flag = 0
    for t in text:
        if t.__eq__('>'):
            text_list.append(line)
            text_list.append('>')
            line = ''
        else:
            if t.__eq__('\n'):
                if (last_letter.__eq__('.') or not(last_letter.__eq__(''))) and not(last_letter.__eq__('>')):
                    text_list.append(line)
                    line = ''
                    flag = 1
                    last_letter = '>'
                elif flag >= 1 or last_letter.__eq__('>'):
                    last_letter = t
                else:
                    flag = 0
                    last_letter = t
            else:
                flag = 0
                line += t
                last_letter = t

    return text_list


def make__bibliography(key):
    file_for_article = make_file_for_article()
    text = ''
    flag = 0
    for line in file_for_article:
        if flag == 1 and (line.__contains__('\\bibitem{') or line.__contains__('\\end{thebibliography}')):
            flag = 0
            return text
        if flag == 1:
            text += str(line)
        if line.__contains__('\\bibitem{'+key+'}'):
            flag = 1


# open journal and clear from comments
filenames = glob.glob("latex_files/*")
filenames_to_string = ' '.join(filenames)
number_journal = re.findall(r'msm_jrn_n([^.tex]*)', filenames_to_string, re.DOTALL)[0]
journal_file = open('latex_files/msm_jrn_n' + number_journal + '.tex', 'r', encoding='cp1251')
journal_text = journal_file.read()
journal_clear = clear_file(journal_text)

# open article and clear from comments
article_file = open('latex_files/GuMatush.tex', 'r', encoding='cp1251')
article_text = article_file.read()
article_clear = clear_file(article_text)

article_numbers_left_text = 'Математические структуры и моделирование ' + \
                            re.findall(r'\\yearpub{([^}]*)}', journal_clear, re.DOTALL)[0] + '. №' + \
                            re.findall(r'\\num{([^}]*)}', journal_clear, re.DOTALL)[0] + '(' +\
                            re.findall(r'\\volume{([^}]*)}', journal_clear, re.DOTALL)[0] + ').'
article_numbers_right_text = 'УДК     ' + re.findall(r'\\udc{([^}]*)}', article_clear, re.DOTALL)[0]
article_title = re.findall(r'\\title{([^}]*)}', article_clear, re.DOTALL)[0]
article_authors = re.findall(r'\\author{([^}]*)}{([^}]*)}{([^}]*)}', article_clear, re.DOTALL)
article_omsu = re.findall(r'\\affil{([^}]*)}', article_clear, re.DOTALL)[0]
article_annotation = re.findall(r'\\abstract{([^}]*)}', article_clear, re.DOTALL)[0]
article_keywords = re.findall(r'\\keywords{([^}]*)}', article_clear, re.DOTALL)[0]

begin_and_end = re.findall(r'\\section\*{([^}]*)}', article_clear, re.DOTALL)
begin_text = pretty_text_begin_end(make_text_begin_end(begin_and_end[0]))
end_text = pretty_text_begin_end(make_text_begin_end(begin_and_end[1]))

plain_text_titles = re.findall(r'\\section\{([^}]*)}', article_clear, re.DOTALL)
plain_text = make_text(plain_text_titles)
plain_text = pretty_text(plain_text)

bibliography_amounty = re.findall(r'\\bibitem{([^}]*)}', article_clear, re.DOTALL)
bibliography_index = int(bibliography_amounty.__len__()/2)
bibliography_amounty = bibliography_amounty[:bibliography_index]

bibliography_list = []
for i in bibliography_amounty:
    bibliography_list.append(make__bibliography(i))

plain_text = plain_text.replace('')

# find_cite = re.findall(r'\\cite{gum([^}])+,?}', article_clear, re.DOTALL)

doc = dominate.document(title='Математические структуры и моделирование')

with doc.head:
    link(rel='stylesheet', href='style.css')


with doc:
    with div():
        attr(cls='wrapper')
        with div():
            attr(cls='header')
            with div():
                attr(cls='numbers_left')
                span(article_numbers_left_text)
            with div():
                attr(cls='numbers_right')
                span(article_numbers_right_text)
        with div():
            attr(cls='title')
            span(article_title)
        with div():
            attr(cls='authors')
            for i in article_authors:
                with div():
                    attr(cls='author')
                    span(i[0])
                with div():
                    attr(cls='contact')
                    span(i[1] + ',')
                    span('e-mail:  ' + i[2])
        with div():
            attr(cls='omsu')
            span(article_omsu)
        with div():
            attr(cls='article__info')
            with div():
                attr(cls='annotation')
                span('Аннотация. ', cls='bold')
                span(article_annotation)
            with div():
                attr(cls='annotation')
                span('Ключевые слова: ', cls='bold')
                span(article_keywords)
        with div():
            attr(cls='article__title')
            span(begin_and_end[0])
        for i in begin_text:
            with div():
                attr(cls='article__text')
                span(i)
        for i in plain_text_titles:
            with div():
                attr(cls='article__title')
                span(i)
            for j in plain_text:
                if j.__eq__('>'):
                    pass
                else:
                    with div():
                        attr(cls='article__text')
                        span(j)
        with div():
            attr(cls='article__title')
            span(begin_and_end[1])
        for i in end_text:
            with div():
                attr(cls='article__text')
                span(i)
        with div():
            attr(cls='article__title')
            span('Литература')
        with div():
            attr(cls='article__text')
            list = ul()
            num = 1
            for i in bibliography_list:
                str_for_li = str(num) + '. ' + str(i)
                list += li(str_for_li)
                num += 1


# print(doc)

output = open('output.html', 'w')
for i in doc:
   output.write(str(i))
output.close()
