import re
import nltk
import html
import pymorphy2
import bs4
import pyphen
import math
import fnmatch
import os
import copy
import logging
import shutil

from natsort import natsorted
from functools import reduce
from PIL import Image
from time import time
from nltk.tokenize import RegexpTokenizer
from . import settings


def read_files(source, only_these=None):
    res = []
    all_html = bs4.BeautifulSoup(
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Title</title></head><body></body></html>',
        'html.parser'
    )
    all_content = ''
    all_pages_number = 0
    for file_name in natsorted(os.listdir(source), key=lambda y: y.lower()):
        dir_path = os.path.join(source, file_name)
        if os.path.isdir(dir_path):
            dir_path = os.path.join(dir_path, 'HTML')
            if file_name in only_these if only_these is not None else True:
                mod_html = bs4.BeautifulSoup(
                    '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Title</title></head><body></body></html>',
                    'html.parser'
                )
                mod_content = ''
                mod_pages_number = 0
                for file_name in os.listdir(dir_path):
                    mod_pages_number += 1
                    file_path = os.path.join(dir_path, file_name)
                    if os.path.isfile(file_path) and re.match(fnmatch.translate('*.html'), file_path, re.IGNORECASE):
                        f = open(file_path, 'r', encoding='utf-8')
                        c = f.read()
                        soup = bs4.BeautifulSoup(c, 'html.parser')
                        imgs = soup.find_all('img')
                        for img in imgs:
                            img['src'] = os.path.join(dir_path, img['src'])
                        for element in soup.body.contents:
                            mod_html.body.append(copy.copy(element))
                        f.close()
                        tockens = re.split(r'<[^>]+>', c)
                        text = ' '.join(list(filter(lambda x: not re.fullmatch(r'\s*', x), tockens)))
                        mod_content += ' ' + html.unescape(text)
                res.append({
                    'dir_path': os.path.dirname(dir_path),
                    'html': str(mod_html),
                    'txt': mod_content,
                    'pgs_num': mod_pages_number
                })
                for element in mod_html.body.contents:
                    all_html.body.append(copy.copy(element))
                all_content += mod_content
                all_pages_number += mod_pages_number
        else:
            if re.match(fnmatch.translate('*.html'), os.path.basename(dir_path), re.IGNORECASE) and (file_name in only_these if only_these is not None else True):
                f = open(dir_path, 'r', encoding='utf-8')
                c = f.read()
                f.close()
                mod_html = bs4.BeautifulSoup(c, 'html.parser')
                tockens = re.split(r'<[^>]+>', c)
                text = ' '.join(list(filter(lambda x: not re.fullmatch(r'\s*', x), tockens)))
                mod_content = ' ' + html.unescape(text)
                res.append({
                    'dir_path': os.path.dirname(dir_path),
                    'html': str(mod_html),
                    'txt': mod_content,
                    'pgs_num': 1
                })
                for element in mod_html.body.contents:
                    all_html.body.append(copy.copy(element))
                all_content += mod_content
                all_pages_number += 1
    res.insert(0, {
        'dir_path': os.path.dirname(source),
        'html': str(all_html),
        'txt': all_content,
        'pgs_num': all_pages_number
    })
    clear_dir(os.path.join(settings.BASE_DIR, 'log', os.path.basename(source)))
    return res


def text_characteristics(file):
    log_path = os.path.join(settings.BASE_DIR, 'log')
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    dir_name = os.path.basename(os.path.dirname(file["dir_path"]))
    log_path = os.path.join(log_path, dir_name)
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_name = os.path.basename(file["dir_path"])
    log_path = os.path.join(log_path, log_name + '.log')
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info(f'Text characteristics for {file["dir_path"]}:')

    res = {}

    soup = bs4.BeautifulSoup(file['html'], 'html.parser')

    logger.info('The calculation of new concepts number...')
    start = time()

    italic_elements = soup.find_all('i')

    definitions = soup.find_all('div', 'definition')

    buf = []
    for italic_element in italic_elements:
        if re.fullmatch(r'<i>\s*[a-zA-Zа-яА-Я]\s*</i>', str(italic_element)):
            continue
        buf.append(italic_element)
        for definition in definitions:
            def_italic_elements = definition.find_all('i')
            for def_italic_element in def_italic_elements:
                if italic_element == def_italic_element:
                    buf.pop(len(buf) - 1)
                    break
            if italic_element not in buf:
                break

    new_concepts_number = reduce(
        lambda x, y: x + y,
        [len(definition.find_all('p')) for definition in definitions]
    ) if len(definitions) > 0 else 0

    new_concepts_number += len(buf)

    res['new_concepts_number'] = new_concepts_number
    finish = time()
    logger.info(f'New concepts number: {new_concepts_number}')
    logger.info(f'Time spent: {finish - start}')

    txt = file['txt']

    logger.info('Partitioning into tokens...')
    start = time()
    tokenizer = RegexpTokenizer(r'[a-zA-Zа-яА-Я-]+')
    tockens = list(map(lambda x: x.lower(), tokenizer.tokenize(txt)))
    finish = time()
    logger.info(f'Tockens: {tockens}')
    logger.info(f'Time spent: {finish - start}')

    morph = pymorphy2.MorphAnalyzer()
    logger.info('Parsing words...')
    start = time()
    words_objects = [morph.parse(tocken)[0] for tocken in tockens]
    finish = time()
    logger.info(f'Words objects: {words_objects}')
    logger.info(f'Time spent: {finish - start}')

    logger.info('Deletion of non-existent words...')
    start = time()
    filtered_words_objects = list(filter(lambda x: x.tag.POS is not None, words_objects))
    finish = time()
    logger.info(f'Filtered words objects: {filtered_words_objects}')
    logger.info(f'Time spent: {finish - start}')

    logger.info('Normalization of words...')
    start = time()
    norm_words = list([word.normal_form for word in filtered_words_objects])
    # unic_norm_words = list(sorted(set(norm_words)))
    finish = time()
    logger.info(f'Normalized russian words: {norm_words}')
    # logger.info(f'Unique normalized russian words: {unic_norm_words}')
    logger.info(f'Time spent: {finish - start}')

    ru_norm_words = []
    en_norm_words = []

    logger.info('Separation into Russian and English normal words...')
    start = time()
    for word in norm_words:
        if re.fullmatch(r'[a-z0-9-/]+', word):
            en_norm_words.append(word)
        else:
            ru_norm_words.append(word)
    res['ru_norm_words'] = ru_norm_words
    res['en_norm_words'] = en_norm_words
    ru_uniq_norm_words = list(sorted(set(ru_norm_words)))
    en_uniq_norm_words = list(sorted(set(en_norm_words)))
    res['ru_uniq_norm_words'] = ru_uniq_norm_words
    res['en_uniq_norm_words'] = en_uniq_norm_words
    finish = time()
    logger.info(f'Russian normal words: {ru_norm_words}')
    logger.info(f'Russian unique normal words: {ru_uniq_norm_words}')
    logger.info(f'English normal words: {en_norm_words}')
    logger.info(f'English unique normal words: {en_uniq_norm_words}')
    logger.info(f'Time spent: {finish - start}')

    logger.info('Getting russian and english stop words...')
    start = time()
    ru_stop_words = set(nltk.corpus.stopwords.words('russian'))
    en_stop_words = set(nltk.corpus.stopwords.words('english'))
    finish = time()
    logger.info(f'Russian stop words: {ru_stop_words}')
    logger.info(f'English stop words: {en_stop_words}')
    logger.info(f'Time spent: {finish - start}')

    logger.info('Removal of Russian and English stop words...')
    start = time()
    ru_filtered_words = [word for word in ru_norm_words if word not in ru_stop_words]
    en_filtered_words = [word for word in en_norm_words if word not in en_stop_words]
    finish = time()
    logger.info(f'Russian filtered words: {ru_filtered_words}')
    logger.info(f'English filtered words: {en_filtered_words}')
    logger.info(f'Time spent: {finish - start}')

    res['ru_filtered_words'] = ru_filtered_words
    res['en_filtered_words'] = en_filtered_words

    logger.info('Calculation of the stop words number in the text...')
    start = time()
    ru_stop_words_number = len(list(set(ru_norm_words))) - len(list(set(ru_filtered_words)))
    en_stop_words_number = len(list(set(en_norm_words))) - len(list(set(en_filtered_words)))
    finish = time()
    logger.info(f'Russian stop words number: {ru_stop_words_number}')
    logger.info(f'English stop words number: {en_stop_words_number}')
    logger.info(f'Time spent: {finish - start}')

    """
    logger.info('Normalization of English words...')
    start = time()
    lemmatizer = nltk.stem.WordNetLemmatizer()
    en_norm_words = list([lemmatizer.lemmatize(word) for word in en_filtered_words])
    en_unic_norm_words = list(sorted(set(en_norm_words)))
    res['en_norm_words'] = en_norm_words
    res['en_unic_norm_words'] = en_unic_norm_words
    finish = time()
    logger.info(f'Normalized English words: {en_norm_words}')
    logger.info(f'Unique normalized English words: {en_unic_norm_words}')
    logger.info(f'Time spent: {finish - start}')
    """

    ru_words_number = len(ru_norm_words)
    ru_uniq_words_number = len(ru_uniq_norm_words)
    logger.info(f'Russian words number: {ru_words_number}')
    logger.info(f'Russian unique words number: {ru_uniq_words_number}')
    en_words_number = len(en_norm_words)
    en_uniq_words_number = len(en_uniq_norm_words)
    logger.info(f'English words number: {en_words_number}')
    logger.info(f'English unique words number: {en_uniq_words_number}')
    total_words_number = ru_words_number + en_words_number
    total_uniq_words_number = ru_uniq_words_number + en_uniq_words_number
    logger.info(f'Total words number: {total_words_number}')
    logger.info(f'Total unique words number: {en_uniq_words_number}')

    inf_saturation = (new_concepts_number / total_uniq_words_number) * 100
    res['inf_saturation'] = round(inf_saturation, 2)
    logger.info(f'Information saturation: {res["inf_saturation"]}')

    logger.info('Getting a list of abstract words...')
    start = time()
    abstract_words = list(
        filter(
            lambda x:
            re.fullmatch(r'.*(ость|есть|мость|ность|нность|емость|енность|ие|ье|ание|изм|ура|ано|ота|еств|ество|ет|ета|изн|изна|овизна|ин|ина|щин|щина|чин|чина|льщин|льщина|честв|чество|ств|ство|овств|овство|ничеств|ничество|тельств|тельство|енств|енство|шеств|шество|ур|ни|ние|нь|нье|ени|ение|тие|тье|овк|овка|еж|ёж|ежк|ежка|ёжк|ёжка|б|ба|об|оба|еб|еба|ёб|ёба|аци|ация|яци|яция|фукаци|фукация|инфикаци|инфикация|аж|от|н|ня|отн|отня|ын|ыня|ев|ева|знь|ьё|ьо|ец|ок|ёк|чик|ик|иц|ица|к|ка|инк|инка|ушк|ушка|очк|очка|юшк|юшка|ушко|юшко|ышк|ышко|ишк|ишка|ишко|оньк|онька|еньк|енька|онк|онка|ёнк|ёнка|ц|це|цо|ице|ецо|ца|ашк|ашка|ищ|ище|ища|очек|ечк|ечко|ушек|ышек)', x),
            ru_norm_words
        )
    )
    abstract_uniq_words = list(sorted(set(abstract_words)))
    res['abstract_uniq_words'] = abstract_uniq_words
    finish = time()
    logger.info(f'Abstract words: {abstract_words}')
    logger.info(f'Unique abstract words: {abstract_uniq_words}')
    logger.info(f'Time spent: {finish - start}')

    abstract_words_number = len(abstract_uniq_words)
    logger.info(f'Unique abstract words number: {abstract_words_number}')

    abstractness = (abstract_words_number / total_uniq_words_number) * 100
    res['abstractness'] = round(abstractness, 2)
    logger.info(f'Text abstractness: {res["abstractness"]}')

    logger.info('Splitting text into sentences...')
    start = time()
    sent_tockens = nltk.tokenize.sent_tokenize(txt)
    finish = time()
    logger.info(f'Sentences: {sent_tockens}')
    logger.info(f'Time spent: {finish - start}')
    sent_number = len(sent_tockens)
    logger.info(f'Sentences number: {sent_number}')

    res['sent_number'] = sent_number

    logger.info('Getting the number of compound words...')
    start = time()
    dic = pyphen.Pyphen(lang='ru')
    compound_words_number = 0
    for word in ru_uniq_norm_words:
        if len(dic.inserted(word).split('-')) > 4:
            compound_words_number += 1
    finish = time()
    logger.info(f'Compound words number: {compound_words_number}')
    logger.info(f'Time spent: {finish - start}')

    ganning_index = 0.4 * (0.78 * ru_uniq_words_number / sent_number + 100 * compound_words_number / ru_uniq_words_number)
    res['ganning_index'] = round(ganning_index, 2)
    logger.info(f'Text readability: {res["ganning_index"]}')

    wateriness = ((ru_stop_words_number + en_stop_words_number) / total_words_number) * 100
    res['wateriness'] = round(wateriness, 2)
    logger.info(f'Text wateriness: {res["wateriness"]}')

    logger.info('Calculation of frequencies of Russian and English words...')
    start = time()
    ru_frequencies = [math.sqrt(ru_norm_words.count(word)) for word in ru_uniq_norm_words]
    en_frequencies = [math.sqrt(en_norm_words.count(word)) for word in en_uniq_norm_words]
    finish = time()
    logger.info(f'Russian frequencies: {ru_frequencies}')
    logger.info(f'English frequencies: {en_frequencies}')
    logger.info(f'Time spent: {finish - start}')

    density = max(ru_frequencies + en_frequencies)
    res['density'] = round(density, 2)
    logger.info(f'Text density: {res["density"]}')

    logger.info('Calculation of textual characterization...')
    start = time()
    creolized_text_volume = 0
    bg_creolization = soup.find_all(['span', 'p', 'div'], {'style': re.compile(r'.*background-image: .+')})
    for element in bg_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    italics_creolization = soup.find_all('i')
    for element in italics_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    bold_creolization = soup.find_all('b')
    for element in bold_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    underline_creolization = soup.find_all('u')
    for element in underline_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    border_creolization = soup.find_all(
        ['span', 'p', 'div'],
        {'style': re.compile(r'.*border(-left|-right|-top|-bottom)?: .+')}
    )
    for element in border_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    pictogram_creolization = soup.find_all('div', {'class': ['definition', 'ex_head', 'cn_head']})
    for element in pictogram_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    link_creolization = soup.find_all('a')
    for element in link_creolization:
        creolized_text_volume += len(''.join(re.split(r'<[^>]+>', str(element))))
    creolization_vector = [
        len(bg_creolization),
        len(italics_creolization),
        len(bold_creolization),
        len(underline_creolization),
        len(border_creolization),
        len(pictogram_creolization),
        len(link_creolization)
    ]
    all_text_volume = len(txt)
    creolization_degree = round(creolized_text_volume / all_text_volume, 2) * 100
    res['creolization_vector'] = creolization_vector
    res['all_text_volume'] = all_text_volume
    res['creolized_text_volume'] = creolized_text_volume
    res['creolization_degree'] = creolization_degree
    finish = time()
    logger.info(f'Background creolization: {creolization_vector[0]}')
    logger.info(f'Italics creolization: {creolization_vector[1]}')
    logger.info(f'Bold creolization: {creolization_vector[2]}')
    logger.info(f'Underline creolization: {creolization_vector[3]}')
    logger.info(f'Border creolization: {creolization_vector[4]}')
    logger.info(f'Pictogram creolization: {creolization_vector[5]}')
    logger.info(f'Link creolization: {creolization_vector[6]}')
    logger.info(f'All text volume: {all_text_volume}')
    logger.info(f'Creolized text volume: {creolized_text_volume}')
    logger.info(f'Creolization degree: {creolization_degree}')
    logger.info(f'Time spent: {finish - start}')

    logger.info('Text Characterization Completed.')
    return res


def text_characteristics_all_files(files):
    res = {
        'new_concepts_number': 0,
        'ru_filtered_words': [],
        'en_filtered_words': [],
        'ru_norm_words': [],
        'ru_uniq_norm_words': [],
        'en_norm_words': [],
        'en_uniq_norm_words': [],
        'abstract_uniq_words': [],
        'sent_number': 0,
        'creolization_vector': [0, 0, 0, 0, 0, 0, 0],
        'all_text_volume': 0,
        'creolized_text_volume': 0,
        'creolization_degree': 0
    }
    for file in files:
        res['new_concepts_number'] += file['txt_ch']['new_concepts_number']
        res['ru_filtered_words'] += file['txt_ch']['ru_filtered_words']
        res['en_filtered_words'] += file['txt_ch']['en_filtered_words']
        res['ru_norm_words'] += file['txt_ch']['ru_norm_words']
        res['ru_uniq_norm_words'] += file['txt_ch']['ru_uniq_norm_words']
        res['en_norm_words'] += file['txt_ch']['en_norm_words']
        res['en_uniq_norm_words'] += file['txt_ch']['en_uniq_norm_words']
        res['abstract_uniq_words'] += file['txt_ch']['abstract_uniq_words']
        res['sent_number'] += file['txt_ch']['sent_number']
        for i in range(len(file['txt_ch']['creolization_vector'])):
            res['creolization_vector'][i] += file['txt_ch']['creolization_vector'][i]
        res['all_text_volume'] += file['txt_ch']['all_text_volume']
        res['creolized_text_volume'] += file['txt_ch']['creolized_text_volume']

    n = len(files)
    m = len(res['creolization_vector'])
    median = []
    for i in range(m):
        median.append(res['creolization_vector'][i] / n)
    res['creole_txt_uni_distr'] = [0 for _ in range(m)]
    for file in files:
        for i in range(len(file['txt_ch']['creolization_vector'])):
            res['creole_txt_uni_distr'][i] += math.pow(file['txt_ch']['creolization_vector'][i] - median[i], 2)
    for i in range(m):
        res['creole_txt_uni_distr'][i] = round(res['creole_txt_uni_distr'][i] / n, 2)

    res['ru_uniq_norm_words'] = list(sorted(set(res['ru_uniq_norm_words'])))
    res['en_uniq_norm_words'] = list(sorted(set(res['en_uniq_norm_words'])))

    ru_words_number = len(res['ru_uniq_norm_words'])
    en_words_number = len(res['en_uniq_norm_words'])
    total_words_number = ru_words_number + en_words_number

    inf_saturation = (res['new_concepts_number'] / total_words_number) * 100

    res['inf_saturation'] = round(inf_saturation, 2)

    res['abstract_uniq_words'] = list(sorted(set(res['abstract_uniq_words'])))

    abstract_words_number = len(res['abstract_uniq_words'])

    abstractness = (abstract_words_number / total_words_number) * 100

    res['abstractness'] = round(abstractness, 2)

    dic = pyphen.Pyphen(lang='ru')
    compound_words_number = 0
    for word in res['ru_uniq_norm_words']:
        if len(dic.inserted(word).split('-')) > 4:
            compound_words_number += 1

    ganning_index = 0.4 * (0.78 * ru_words_number / res['sent_number'] + 100 * compound_words_number / ru_words_number)

    res['ganning_index'] = round(ganning_index, 2)

    ru_stop_words_number = len(list(set(res['ru_norm_words']))) - len(list(set(res['ru_filtered_words'])))
    en_stop_words_number = len(list(set(res['en_norm_words']))) - len(list(set(res['en_filtered_words'])))

    wateriness = ((ru_stop_words_number + en_stop_words_number) / total_words_number) * 100

    res['wateriness'] = round(wateriness, 2)

    ru_frequences = [math.sqrt(res['ru_norm_words'].count(word)) for word in res['ru_uniq_norm_words']]
    en_frequences = [math.sqrt(res['en_norm_words'].count(word)) for word in res['en_uniq_norm_words']]

    density = max(ru_frequences + en_frequences)

    res['density'] = round(density, 2)

    res['creolization_degree'] = round(res['creolized_text_volume'] / res['all_text_volume'], 2) * 100

    return res


def get_points_brightness(img):
    width = img.size[0]
    height = img.size[1]
    px = img.load()

    res = []
    for i in range(width):
        for j in range(height):
            pixel = px[i, j]
            if type(pixel) == int:
                pixel = (pixel, pixel, pixel)
            R = pixel[0]
            G = pixel[1]
            B = pixel[2]
            res.append(0.299 * R + 0.587 * G + 0.114 * B)

    return res


def get_img_brightness(file_path):
    img = Image.open(file_path)
    width = img.size[0]
    height = img.size[1]

    psb = get_points_brightness(img)

    res = sum(psb) / (width * height)

    return res


def get_rel_img_brightness(file_path):
    img = Image.open(file_path)
    width = img.size[0]
    height = img.size[1]

    psb = get_points_brightness(img)

    res = sum(psb) / (width * height * max(psb))

    return res


def get_points_contrast(img):
    width = img.size[0]
    height = img.size[1]

    psb = get_points_brightness(img)

    imb = sum(psb) / (width * height)

    res = [(pb - imb) * (pb - imb) for pb in psb]

    return res


def get_img_contrast(file_path):
    img = Image.open(file_path)
    width = img.size[0]
    height = img.size[1]

    psc = get_points_contrast(img)

    res = sum(psc) / (width * height)

    return res


def get_rel_img_contrast(file_path):
    img = Image.open(file_path)
    width = img.size[0]
    height = img.size[1]

    psc = get_points_contrast(img)

    res = 2 * sum(psc) / (width * height * max(psc))

    return res


def img_characteristics(file):
    res = {}

    soup = bs4.BeautifulSoup(file['html'], 'html.parser')
    img_list = soup.find_all('img')
    img_number = len(img_list)
    aver_img_in_pg_num = img_number / file['pgs_num']

    # print(f'Количество изображений: {img_number}')
    # print(f'Среднее число иллюстраций на страницу: {aver_img_in_pg_num}\r\n')
    res['img_number'] = img_number
    res['pgs_num'] = file['pgs_num']
    res['aver_img_in_pg_num'] = aver_img_in_pg_num

    res['images'] = []
    for img in img_list:

        try:
            brightness = get_img_brightness(img['src'])
            rel_brightness = get_rel_img_brightness(img['src'])
            contrast = get_img_contrast(img['src'])
            rel_contrast = get_rel_img_contrast(img['src'])

            # print(f'Путь к файлу: {img_path}')
            # print(f'Яркость изображения: {brightness}')
            # print(f'Относительная яркость изображения: {rel_brightness}')
            # print(f'Контраст изображения: {contrast}')
            # print(f'Относительный контраст изображения: {rel_contrast}\r\n')
            res['images'].append({
                'img_path': '/' + img['src'][img['src'].index('media'):],
                'brightness': brightness,
                'rel_brightness': rel_brightness,
                'contrast': contrast,
                'rel_contrast': rel_contrast
            })
        except Exception as e:
            print('--------------')
            print(img['src'])
            print(e)
            print('--------------')

    return res


def img_characteristics_all_files(files):
    res = {
        'img_number': 0,
        'pgs_num': 0,
        'images': []
    }

    for file in files:
        res['img_number'] += file['img_ch']['img_number']
        res['pgs_num'] += file['img_ch']['pgs_num']
        res['images'] += file['img_ch']['images']

    res['aver_img_in_pg_num'] = res['img_number'] / res['pgs_num']

    return res


def search_and_nav_characteristics(file):
    res = {
        'glossary': 0,
        'tables': 0,
        'images': 0,
        'literature': 0,
        'formula': 0,
        'litlist': 0
    }

    soup = bs4.BeautifulSoup(file['html'], 'html.parser')
    h1_list = soup.find_all('h1')
    for h1 in h1_list:
        if re.fullmatch(r'глоссарий', str(h1.string), re.I):
            res['glossary'] = 1
        if re.fullmatch(r'литература', str(h1.string), re.I):
            res['litlist'] = 1
    txt = file['txt']
    tables = re.findall(
        r'(табл[а-я.]*\s*\d+(?:\.\d+)*(?:\s(?!\s*[-–](?!\s*(?:табл[а-я.]*\s*)?\d+(?:\.\d+)*))(?:[-–]\s*(?:табл[а-я.]*\s*)?\d+(?:\.\d+)*)?|[-–]\s*(?:табл[а-я.]*\s*)?\d+(?:\.\d+)*|(?=[.,:!?)](?!\d+))))',
        txt, re.I)
    if len(tables) != 0:
        res['tables'] += len(tables)
    images = re.findall(
        r'(рис[а-я.]*\s*\d+(?:\.\d+)*(?:\s(?!\s*[-–](?!\s*(?:рис[а-я.]*\s*)?\d+(?:\.\d+)*))(?:[-–]\s*(?:рис[а-я.]*\s*)?\d+(?:\.\d+)*|\s*(?:(?:,\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*)(?:,\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*)*|(?:\(\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*\))(?:\s*,\s*\(\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*\))*))?|[-–]\s*(?:рис[а-я.]*\s*)?\d+(?:\.\d+)*|(?=[,])(?:,\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*)*|(?=[.:!?)](?!\d+))))',
        txt, re.I)
    if len(images) != 0:
        res['images'] += len(images)
        """
        for img in images:
            if (re.fullmatch(r'рис[а-я.]*\s*\d+(\.\d+)*(\s*,\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z]))+\s*', img, re.I)):
                res['images'] += len(img.split(',')) - 1
            elif (re.fullmatch(r'рис[а-я.]*\s*\d+(\.\d+)*\s*(\(\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*\))(\s*,\s*\(\s*[а-яА-Яa-zA-Z](?![а-яА-Яa-zA-Z])\s*\))*\s*', img, re.I)):
                res['images'] += len(img.split(','))
            else:
                matches = re.fullmatch(r'рис[а-я.]*\s*\d+(\.(?P<from>\d+))*\s*[-–]\s*(?:рис[а-я.]*\s*)?\d+(?:\.(?P<to>\d+))\s*', img, re.I)
                if matches is not None:
                    res['images'] += int(matches.group('to')) - int(matches.group('from'))
                else:
                    res['images'] += 1
        """
    literature = re.findall(r'(\[\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*\])', txt, re.I)
    if len(literature) != 0:
        res['literature'] += len(literature)
    formula = re.findall(r'((?<=[а-я]\s)\s*\(\s*\d+(?:.\d+)*(?:\s*[-–]\s*\d+(?:.\d+)*)?\s*\))', txt, re.I)
    if len(formula) != 0:
        res['formula'] += len(formula)

    return res


def search_and_nav_characteristics_all_files(files):
    res = {
        'glossary': 0,
        'tables': 0,
        'images': 0,
        'literature': 0,
        'formula': 0,
        'litlist': 0
    }

    for file in files:
        res['glossary'] = file['san_ch']['glossary'] if file['san_ch']['glossary'] == 1 else res['glossary']
        res['tables'] += file['san_ch']['tables']
        res['images'] += file['san_ch']['images']
        res['literature'] += file['san_ch']['literature']
        res['formula'] += file['san_ch']['formula']
        res['litlist'] = file['san_ch']['litlist'] if file['san_ch']['litlist'] == 1 else res['litlist']

    return res


def clear_dir(dir_path):
    if os.path.exists(dir_path):
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
