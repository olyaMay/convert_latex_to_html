# coding: utf8
import re
import os
import sys
import glob
from xml.dom import minidom


def create_tag(name: str = None, text: str = None, attributes: dict = None, *, cdata: bool = False):
    #Функция создания тэга XML
    doc = minidom.Document()

    if name is None:
        return doc

    tag = doc.createElement(name)

    if text is not None:
        if cdata is True:
            tag.appendChild(doc.createCDATASection(text))
        else:
            tag.appendChild(doc.createTextNode(text))

    if attributes is not None:
        for k, v in attributes.items():
            tag.setAttribute(k, str(v))

    return tag



#Поиск файла msm_jrnn*.tex для определения номера журнала
filenames = glob.glob("*")
filenames_to_string = ' '.join(filenames)
number_journal = re.findall(r'msm_jrn_n([^.tex]*)', filenames_to_string, re.DOTALL)
with open('msm_jrn_n' + number_journal[0] + '.tex') as jrn: tex = jrn.read()
with open('msm_jrn_n' + number_journal[0] + '.aux') as jrn: aux = jrn.read()


dell_comments = re.sub(r'[^\\]?%.*\n', '', tex)
dell_comments = dell_comments.replace('~', ' ')
dell_comments = dell_comments.replace('<<', '"')
dell_comments = dell_comments.replace('>>', '"')
dell_comments = dell_comments.replace('<', '\\lt')
dell_comments = dell_comments.replace('>', '\\gt')
dell_comments = dell_comments.replace('---', '-')
dell_comments = dell_comments.replace('\\_', '_')

doc = create_tag()



#           JOURNAL             #
root = create_tag('journal')
doc.appendChild(root)
#           JOURNAL             #


#           OPERCARD            #
opercard = create_tag('operCard')

operator = create_tag('operator', 'Articulus_1911')
pid = create_tag('pid', '0')
date = create_tag('date', '0')

filenames_authors = re.findall(r'\\Input{([^}]*)}', dell_comments, re.DOTALL)
filenames_authors.remove('authors')
filenames_authors.remove('title2')
cntArticle = create_tag('cntArticle', str(len(filenames_authors)))

cntNode = create_tag('cntNode', '0')
cs = create_tag('cs', '0')
opercard.appendChild(operator.cloneNode(True))
opercard.appendChild(pid.cloneNode(True))
opercard.appendChild(date.cloneNode(True))
opercard.appendChild(cntArticle.cloneNode(True))
opercard.appendChild(cntNode.cloneNode(True))
opercard.appendChild(cs.cloneNode(True))

root.appendChild(opercard)
#           OPERCARD            #


#           JOURNAL             #
titleid = create_tag('titleid', '32419')
issn = create_tag('issn', '2222-8772')
eissn = create_tag('eissn', '2222-8799')

root.appendChild(titleid)
root.appendChild(issn)
root.appendChild(eissn)
#           JOURNAL             #


#           JOURNALINFO         #
atr = {'lang': 'RUS'}
journalInfo = create_tag('journalInfo', None, atr)
journalInfo.setAttribute('lang', 'RUS')
title = create_tag('title', 'Математические структуры и моделирование')
journalInfo.appendChild(title.cloneNode(True))
root.appendChild(journalInfo)
#           JOURNALINFO         #

num = re.findall(r'\\num{([^}]*)}', dell_comments, re.DOTALL)
dateUn = re.findall(r'\\yearpub{([^}]*)}', dell_comments, re.DOTALL)
altNum = re.findall(r'\\volume{([^}]*)}', dell_comments, re.DOTALL)
pagess = re.findall(r'\\newlabel{endofsborn}{{[^}]*}{([^}]*)}}', aux, re.DOTALL)

#           ISSUE               #
issue = create_tag('issue')

volume = create_tag('volume', '')
number = create_tag('number', num[0])
altNumber = create_tag('altNumber', altNum[0])
part = create_tag('part', '')
dateUni = create_tag('dateUni', dateUn[0])
issTitle = create_tag('issTitle', '')
pages = create_tag('pages', ('1-'+pagess[0]))


#           ISSUE/ARTICLES           #
articles = create_tag('articles')


def create_article(filename):
    with open(filename) as f: data = f.read()
    dellcomment = re.sub(r'[^\\]?%.*\n', '', data, re.DOTALL)
    dellcomment = dellcomment.replace('~', ' ')
    dellcomment = dellcomment.replace('<<', '"')
    dellcomment = dellcomment.replace('>>', '"')
    dellcomment = dellcomment.replace('<', '\\lt')
    dellcomment = dellcomment.replace('>', '\\gt')
    dellcomment = dellcomment.replace('---', '-')
    dellcomment = dellcomment.replace('--', '-')
    dellcomment = dellcomment.replace('\\_', '_')


    #           ISSUE/ARTILES/SECTION       #
    langRU = {'lang': 'RUS'}
    langEN = {'lang': 'ENG'}
    secTitle_list = re.findall(r'\\(?:addcontentsline{toc}{sect}){([^{}]*)}\s*$', dell_comments, re.MULTILINE)
    secTitle_listEN = re.findall(r'\\addcontentsline{toc}{sectEng}{([^}]*)}', dell_comments, re.DOTALL)
    secTitle_listRUEN_auth = re.findall(r'\\(?:addcontentsline{toc}{sect}|addcontentsline{toc}{sectEng}|Input){([^{}]*)}\s*$', dell_comments, re.MULTILINE)
    k = 0
    while k < len(secTitle_list):

        start_secTitle = dell_comments.find(secTitle_list[k])
        if k + 1 == len(secTitle_list):
            end_secTitle = dell_comments.find(secTitle_listRUEN_auth[-1])
        else:
            end_secTitle = dell_comments.find(secTitle_list[k + 1])

        section_authors = re.findall(r'\\(?:addcontentsline{toc}{sect}|Input){([^{}]*)}\s*$', dell_comments[start_secTitle:end_secTitle], re.MULTILINE)
        if section_authors.count(filename[:-4]) > 0:
            section = create_tag('section')
            secTitleRU = create_tag('secTitle', secTitle_list[k], langRU)
            section.appendChild(secTitleRU)
            secTitleEN = create_tag('secTitle', secTitle_listEN[k], langEN)
            section.appendChild(secTitleEN)
            articles.appendChild(section.cloneNode(True))
        k = k + 1
    #           ISSUE/ARTICLES/SECTION      #

    #           ISSUE/ARTICLES/ARTICLE      #
    article = create_tag('article')


    #           ISSUE/ARTICLES/ARTICLE/PAGES    #

    begNameAuthor = r"\\@writefile{filepages}{\\contentsline {" + filename + "}{startpage}{([^}]*)}}"
    pagesArtStart = re.findall(begNameAuthor, aux, re.DOTALL)
    endNameAuthor = r"\\@writefile{filepages}{\\contentsline {" + filename + "}{endpage}{([^}]*)}}"
    pagesArtEnd = re.findall(endNameAuthor, aux, re.DOTALL)
    pages_article = create_tag('pages', pagesArtStart[0] + '-' + pagesArtEnd[0])

    #           ISSUE/ARTICLES/ARTICLE/PAGES    #

    artType = create_tag('artType', 'RAR')

    #           ISSUE/ARTICLES/ARTICLE/AUTHORS  #
    authors = create_tag('authors')

    #           ISSUE/ARTICLE/ARTICLE/AUTHORS/AUTHOR        #
    authors_full = re.findall(r'\\author{([^}]*)}{[^}]*}{([^}]*)}', dellcomment, re.DOTALL)
    authors_full_en = re.findall(r'\\authorEng\[[^\]]*\]{[^}]*}{[^}]*}{[^}]*}', dellcomment, re.DOTALL)
    authors_name_and_surname_ru = re.findall(r'\\author{([^}]*)}{[^}]*}{[^}]*}', dellcomment, re.DOTALL)
    authors_email = re.findall(r'\\author{[^}]*}{[^}]*}{([^}]*)}', dellcomment, re.DOTALL)
    authors_email_en = re.findall(r'\\authorEng\[[^\]]*\]{[^}]*}{[^}]*}{([^},]*)', dellcomment)
    author_email_en = re.findall(r'\\authorEng{[^}]*}{[^}]*}{([^}]*)\b[^}]*}', dellcomment)
    affil_RU = re.findall(r'\\affil{([^}]*)}', dellcomment, re.DOTALL)
    affil_EN = re.findall(r'\\affilEng\[[^\]]*\]{([^}]*)}', dellcomment, re.DOTALL)
    affil_RU_some = re.findall(r'\\affil\[[^\]]*\]{([^}]*)}', dellcomment, re.DOTALL)
    affil_EN_one = re.findall(r'\\affilEng{([^}]*)}', dellcomment, re.DOTALL)
    affil_RU_one = re.findall(r'\\affil{([^}]*)}', dellcomment, re.DOTALL)
    authors_Initial_EN = re.findall(r'\\authorEng\[[^\]]*\]{([^}]*)\b\w+}{[^}]*}{[^}]*}', dellcomment)
    authors_Initial_RU = re.findall(r'\\author\[[^\]]*\]{([^}]*)\b\w+}{[^}]*}{[^}]*}', dellcomment)
    author_Initial_EN = re.findall(r'\\authorEng{([^}]+?)[\w\']*}', dellcomment)
    author_Initial_RU = re.findall(r'\\author{([^}]*)\b\w+[^}]*}{[^}]*}{[^}]*}', dellcomment)
    authors_Surname_en = re.findall(r'\\authorEng\[[^\]]*\]{[^}]*\b(\w+)}{[^}]*}{[^}]*}', dellcomment)
    authors_Surname_ru = re.findall(r'\\author\[[^\]]*\]{[^}]*\b(\w+)}{[^}]*}{[^}]*}', dellcomment)
    author_Surname_en = re.findall(r'\\authorEng{[^}]*?([\w\']+)}{[^}]*}{[^}]*}', dellcomment)
    author_Surname_ru = re.findall(r'\\author{[^}]*\b(\w+)[^}]*}{[^}]*}{[^}]*}', dellcomment)
    authors_Index_en = re.findall(r'\\authorEng\[([^\]]*)\]{[^}]*}{[^}]*}{[^}]*}', dellcomment, re.DOTALL)
    language_Article_en = dellcomment.count('\\selectlanguage{english}')

    langRU = {'lang': 'RUS'}
    langEN = {'lang': 'ENG'}
    i = 0
    j = 0
    if language_Article_en == 0:
        while i < len(authors_full):
            atr_author = {'id': '0', 'num': i + 1}
            author = create_tag('author', None, atr_author)
            individInfoRU = create_tag('individInfo', None, langRU)
            individInfoEN = create_tag('individInfo', None, langEN)
            while j <= i:
                surnameRU = create_tag('surname', authors_name_and_surname_ru[j][5:])
                initialsRU = create_tag('initials', authors_name_and_surname_ru[j][0:4])
                surnameEN = create_tag('surname', author_Surname_en[j])
                initialsEN = create_tag('initials', author_Initial_EN[j][0:4])
                emailRU = create_tag('email', authors_email[j])
                emailEN = create_tag('email', authors_email[j])
                orgNameRU = create_tag('orgName', affil_RU[0])
                orgNameEN = create_tag('orgName', affil_EN_one[0])
                individInfoEN.appendChild(surnameEN)
                individInfoEN.appendChild(initialsEN)
                individInfoRU.appendChild(surnameRU)
                individInfoRU.appendChild(initialsRU)
                individInfoEN.appendChild(emailEN)
                individInfoRU.appendChild(emailRU)
                individInfoRU.appendChild(orgNameRU)
                individInfoEN.appendChild(orgNameEN)
                author.appendChild(individInfoRU)
                author.appendChild(individInfoEN)
                j = j + 1
            authors.appendChild(author)
            i = i + 1
    else:
        if not authors_full_en:
            countAuth = len(authors_full)
        else:
            countAuth = len(authors_full_en)
        while i < countAuth:
            atr_author = {'id': '0', 'num': i + 1}
            author = create_tag('author', None, atr_author)
            individInfoEN = create_tag('individInfo', None, langEN)
            individInfoRU = create_tag('individInfo', None, langRU)
            while j <= i:
                if not authors_Surname_en:
                    surnameEN = create_tag('surname', author_Surname_en[j])
                    surnameRU = create_tag('surname', author_Surname_ru[j])
                else:
                    surnameEN = create_tag('surname', authors_Surname_en[j])
                    surnameRU = create_tag('surname', authors_Surname_ru[j])
                individInfoEN.appendChild(surnameEN)
                individInfoRU.appendChild(surnameRU)
                if not authors_Initial_EN:
                    initialsEN = create_tag('initials', author_Initial_EN[j])
                    initialsRU = create_tag('initials', author_Initial_RU[j])
                else:
                    initialsEN = create_tag('initials', authors_Initial_EN[j])
                    initialsRU = create_tag('initials', authors_Initial_RU[j])
                individInfoEN.appendChild(initialsEN)
                individInfoRU.appendChild(initialsRU)
                if not authors_email_en:
                    emailEN = create_tag('email', author_email_en[j])
                    emailRU = create_tag('email', author_email_en[j])
                else:
                    emailEN = create_tag('email', authors_email_en[j])
                    emailRU = create_tag('email', authors_email_en[j])
                individInfoEN.appendChild(emailEN)
                individInfoRU.appendChild(emailRU)

                if not affil_EN:
                    orgNameEN = create_tag('orgName', affil_EN_one[0])
                    orgNameRU = create_tag('orgName', affil_RU_one[0])
                else:
                    ind = authors_Index_en[j][0:1]
                    ind = int(ind) - 1
                    orgNameEN = create_tag('orgName', affil_EN[int(ind)])
                    orgNameRU = create_tag('orgName', affil_RU_some[int(ind)])
                individInfoEN.appendChild(orgNameEN)
                individInfoRU.appendChild(orgNameRU)
                author.appendChild(individInfoEN)
                author.appendChild(individInfoRU)
                j = j + 1
            authors.appendChild(author)
            i = i + 1

    #           ISSUE/ARTICLES/ARTICLE/ARTTITLE
    artTitles = create_tag('artTitles')
    titleRU = re.findall(r'\\title{((?:[^{}]|{[^}]*})*)}', dellcomment, re.DOTALL)
    titleEN = re.findall(r'\\titleEng{((?:[^{}]|{[^}]*})*)}', dellcomment, re.DOTALL)
    artTitleRU = create_tag('artTitle', titleRU[0], langRU)
    artTitleEN = create_tag('artTitle', titleEN[0], langEN)
    artTitles.appendChild(artTitleRU.cloneNode(True))
    artTitles.appendChild(artTitleEN.cloneNode(True))

    #           ISSUE/ARTICLES/ARTICLE/ABSTRACTS
    abstracts = create_tag('abstracts')
    abstrRU = re.findall(r'\\abstract{((?:[^{}]|{[^}]*})*)}', dellcomment, re.DOTALL)
    abstrEN= re.findall(r'\\abstractEng{((?:[^{}]|{[^}]*})*)}', dellcomment, re.DOTALL)
    abstractRU = create_tag('abstract', abstrRU[0], langRU)
    abstractEN = create_tag('abstract', abstrEN[0], langEN)
    abstracts.appendChild(abstractRU.cloneNode(True))
    abstracts.appendChild(abstractEN.cloneNode(True))
    #           ISSUE/ARTICLES/ARTICLE/ABSTRACT

    #           ISSUE/ARTICLES/ARTICLE/TEXT
    atrText = {'lang': 'RUS'}
    beg = dellcomment.find('\\maketitle') + 10
    end = dellcomment.find('\\begin{thebibliography}') - 1
    text_art = create_tag('text', dellcomment[beg:end].strip(), atrText)
    #           ISSUE/ARTICLES/ARTICLE/TEXT


    #           ISSUE/ARTICLES/ARTICLE/CODES
    codes = create_tag('codes')
    udc = re.findall(r'\\udc{([^}]*)}', dellcomment, re.DOTALL)
    udk = create_tag('udk', udc[0])
    codes.appendChild(udk.cloneNode(True))
    #           ISSUE/ARTICLES/ARTICLE/CODES


    #           ISSUE/ARTICLES/ARTICLE/KEYWORDS
    kwdAtrRUS = {'lang': 'RUS'}
    kwdAtrENG = {'lang': 'ENG'}
    keywords = create_tag('keywords')
    kwdGroupRUS = create_tag('kwdGroup', None, kwdAtrRUS)


    keywords_all = re.findall(r'\\keywords{([^}]*)}', dellcomment, re.DOTALL)
    keywords_grouped = keywords_all[0].split(',')
    i = 0
    while i < len(keywords_grouped):
        keyword = str(keywords_grouped[i])
        keyword = keyword.strip('\n')
        keyword = keyword.strip()
        keyword = create_tag('keyword', keyword)
        kwdGroupRUS.appendChild(keyword.cloneNode(True))
        i = i + 1


    kwdGroupENG = create_tag('kwdGroup', None, kwdAtrENG)
    keywords_all = re.findall(r'\\keywordsEng{([^}]*)}', dellcomment, re.DOTALL)
    keywords_grouped = keywords_all[0].split(', ')
    i = 0
    while i < len(keywords_grouped):
        keyword = str(keywords_grouped[i])
        keyword = keyword.strip('\n')
        keyword = keyword.strip()
        keyword = create_tag('keyword', keyword)
        kwdGroupENG.appendChild(keyword.cloneNode(True))
        i = i + 1

    keywords.appendChild(kwdGroupRUS.cloneNode(True))
    keywords.appendChild(kwdGroupENG.cloneNode(True))
#                ISSUE/ARTICLES/ARTICLE/KEUWORDS


    #           ISSUE/ARTICLES/ARTICLE/REFERENCES
    bBeg = dellcomment.find('begin{thebibliography}')
    bEnd = dellcomment.find('\\end{thebibliography}') - 2
    bibitems_all = re.split(r'\\bibitem{.*}', dellcomment[bBeg:bEnd])
    references = create_tag('references')
    i = 1
    while i < len(bibitems_all):
        bibitem = str(bibitems_all[i])
        bibitem = bibitem.strip('\n')
        bibitem = bibitem.strip()
        bibitem = bibitem.replace('\\url{', '')
        bibitem = bibitem.replace('{', '')
        bibitem = bibitem.replace('}', '')
        reference = create_tag('reference', bibitem)
        references.appendChild(reference.cloneNode(True))
        i = i + 1


    #           ISSUE/ARTICLES/ARTICLE/REFERENCES


    #           ISSUE/ARTICLES/ARTICLE/FILES
    nameURL = 'http://msm.omsu.ru/jrns/jrn' + altNum[0] + '/' + filename.replace('.tex', '.pdf')
    files = create_tag('files')
    furl = create_tag('furl', nameURL)
    file = create_tag('file', filename.replace('.tex', '.pdf'))
    files.appendChild(furl.cloneNode(True))
    files.appendChild(file.cloneNode(True))
    #           ISSUE/ARTICLES/ARTICLE/FILES



    #           ISSUE/ARTICLES/ARTICLE/ARTTITLE

    #authors.appendChild(author.cloneNode(True))
    article.appendChild(pages_article.cloneNode(True))
    article.appendChild(artType.cloneNode(True))
    article.appendChild(authors.cloneNode(True))
    article.appendChild(artTitles.cloneNode(True))
    article.appendChild(abstracts.cloneNode(True))
    article.appendChild(text_art.cloneNode(True))
    article.appendChild(codes.cloneNode(True))
    article.appendChild(keywords.cloneNode(True))
    article.appendChild(references.cloneNode(True))
    article.appendChild(files.cloneNode(True))
    #           ISSUE/ARTICLES/ARTICLE      #
    articles.appendChild(article.cloneNode(True))
    #           ISSUE/ARTICLES              #
    f.close()

ext = '.tex'            # Расширение файла
EXT = '.TEX'

file_dir = os.getcwd()  # Текущая директория
print('Текущий каталог: {}'.format(file_dir))

file_list = filenames_authors
for file in file_list:
   print('Имя файла: {}'.format(file))
   create_article(str(file) + '.tex')

issue.appendChild(volume.cloneNode(True))
issue.appendChild(number.cloneNode(True))
issue.appendChild(altNumber.cloneNode(True))
issue.appendChild(part.cloneNode(True))
issue.appendChild(dateUni.cloneNode(True))
issue.appendChild(issTitle.cloneNode(True))
issue.appendChild(pages.cloneNode(True))
issue.appendChild(articles.cloneNode(True))
root.appendChild(issue)
#           ISSUE               #




xml_str = doc.toprettyxml(indent="  ")

endFileName = '22228772_' + dateUn[0] + '_-_' + num[0] + '(' + altNum[0] + ')_unicode.xml'

with open(endFileName, "w", encoding='utf-16BE') as f:
    f.write('\uFEFF' + xml_str)
    f.close()
