import os
import re
import shutil
import sys
import bs4
import datetime
import html
# import MySQLdb as sql
import pandas as pd
import json
import requests
import django
django.setup()

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render
from . import forms
from . import settings
from pyunpack import Archive
from natsort import natsorted
from . import analyzer
from time import time
from multiprocessing.pool import ThreadPool
from concurrent.futures import ProcessPoolExecutor
from . import models
from django.shortcuts import redirect
from django.contrib import auth
from functools import reduce


def index(request):
    user = auth.get_user(request)
    clear_media()
    request.session.create()
    session = models.Session(id=request.session.session_key, active=True)
    session.save()
    os.mkdir(os.path.join(settings.MEDIA_ROOT, request.session.session_key))
    template = loader.get_template('index.html')
    context = {
        'username': user.username if not user.is_anonymous else 'Anonymous',
        'is_superuser': user.is_superuser,
        'is_anonymous': user.is_anonymous,
    }
    return HttpResponse(template.render(context, request))


def upload_file(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        media_root = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
        for file in files:
            file_path = os.path.join(media_root, file.name)
            write_file(file, file_path)
        return redirect('/uploaded-files/')
    return render(request, 'index.html', {})


def uploaded_files(request):
    media_root = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    user = auth.get_user(request)
    files = list(filter(lambda file_name: os.path.isfile(os.path.join(media_root, file_name)), os.listdir(media_root)))
    context = {
        'username': user.username,
        'is_superuser': user.is_superuser,
        'is_anonymous': user.is_anonymous,
        'files': files
    }
    return render(request, 'uploaded-files.html', context)


def delete_uploaded_file(request):
    media_root = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    trash_dir = os.path.join(media_root, 'trash')
    if not os.path.exists(trash_dir):
        os.mkdir(trash_dir)
    file_name = request.GET.get('file-name')
    src = os.path.join(media_root, file_name)
    dst = os.path.join(trash_dir, file_name)
    models.File(
        uid=request.session.session_key,
        src=dst
    ).save()
    shutil.move(src, dst)
    files = list(filter(lambda file_name: os.path.isfile(os.path.join(media_root, file_name)), os.listdir(media_root)))
    if len(files) == 0:
        return redirect('/')
    user = auth.get_user(request)
    context = {
        'username': user.username,
        'is_superuser': user.is_superuser,
        'is_anonymous': user.is_anonymous,
        'files': files
    }
    return render(request, 'uploaded-files.html', context)


def restore_deleted_uploaded_files(request):
    files_names = request.POST.getlist('files-names[]')
    media_root = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    for file_name in files_names:
        file_path = os.path.join(media_root, file_name)
        if not os.path.exists(file_path):
            files = models.File.objects.all()
            for file in files:
                if file.uid == request.session.session_key and os.path.basename(file.src) == file_name:
                    shutil.move(file.src, file_path)
                    file.delete()
    for file_name in os.listdir(media_root):
        file_path = os.path.join(media_root, file_name)
        if os.path.isdir(file_path) and file_name != 'trash':
            shutil.rmtree(file_path)
    return JsonResponse({'res': True})


def unpack_files(request):
    media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    tmp_path = os.path.join(media_path, 'tmp')
    zip_path = os.path.join(tmp_path, 'zip')
    trash_path = os.path.join(media_path, 'trash')
    if not os.path.exists(trash_path):
        os.mkdir(trash_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
        os.mkdir(zip_path)
    for file_name in os.listdir(media_path):
        file_path = os.path.join(media_path, file_name)
        if os.path.isfile(file_path):
            name, extension = os.path.splitext(file_name)
            if re.fullmatch(
                    r'\.(7z|ace|alz|a|arc|arj|bz2|cab|Z|cpio|deb|dms|gz|lrz|lha|lzh|lz|lzma|lzo|rpm|rar|rz|tar|xz|zip|jar|zoo)',
                    extension, re.I
            ):
                mod_path = os.path.join(zip_path, name)
                if not os.path.exists(mod_path):
                    os.mkdir(mod_path)
                Archive(file_path).extractall(mod_path)
                if not os.path.exists(os.path.join(mod_path, 'HTML')):
                    for file in os.listdir(mod_path):
                        shutil.move(os.path.join(mod_path, file), os.path.join(zip_path, file))
                    shutil.rmtree(mod_path)
                dst = os.path.join(trash_path, file_name)
                models.File(
                    uid=request.session.session_key,
                    src=dst
                ).save()
                shutil.move(file_path, dst)
                check_input_files(media_path, tmp_path, zip_path)
            else:
                shutil.move(file_path, os.path.join(tmp_path, file_name))
    shutil.rmtree(zip_path)
    tmp_files = os.listdir(tmp_path)
    if len(tmp_files) != 0:
        return redirect('/files/')
    else:
        pass
        shutil.rmtree(tmp_path)
        return redirect('/modules/')


def files(request):
    tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
    tmp_files = os.listdir(tmp_path)
    context = {'files': natsorted(tmp_files, key=lambda y: y.lower())}
    return render(request, 'files.html', context)


def check_input_files(media_path, tmp_path, zip_path):
    html_files = []
    for file_name in os.listdir(zip_path):
        file_path = os.path.join(zip_path, file_name)
        if os.path.isdir(file_path):
            for sub_file_name in os.listdir(file_path):
                sub_file_path = os.path.join(file_path, sub_file_name)
                if os.path.isdir(sub_file_path):
                    if re.fullmatch(r'html', sub_file_name, re.I):
                        is_html = False
                        for html_file_name in os.listdir(sub_file_path):
                            html_file_path = os.path.join(sub_file_path, html_file_name)
                            if os.path.isfile(html_file_path):
                                name, extension = os.path.splitext(html_file_name)
                                if re.fullmatch(r'\.html', extension, re.I):
                                    shutil.move(file_path, os.path.join(media_path, file_name))
                                    is_html = True
                                    break
                        if not is_html:
                            shutil.rmtree(sub_file_path)
                        else:
                            break
                    elif re.fullmatch(r'slides', sub_file_name, re.I):
                        is_img = False
                        for img_file_name in os.listdir(sub_file_path):
                            img_file_path = os.path.join(sub_file_path, img_file_name)
                            if os.path.isfile(img_file_path):
                                name, extension = os.path.splitext(img_file_name)
                                if re.fullmatch(r'\.(jpg|jpeg|png)', extension, re.I):
                                    shutil.move(file_path, os.path.join(media_path, file_name))
                                    is_img = True
                                    break
                        if not is_img:
                            shutil.rmtree(sub_file_path)
                        else:
                            break
                else:
                    name, extension = os.path.splitext(sub_file_name)
                    if re.fullmatch(r'\.html', extension, re.I):
                        dst = os.path.join(tmp_path, sub_file_name)
                        n = 1
                        while os.path.exists(dst):
                            sub_file_name = name + ' (' + str(n) + ')' + extension
                            dst = os.path.join(tmp_path, sub_file_name)
                            n += 1
                        shutil.move(sub_file_path, dst)
                        html_files.append(sub_file_name)
                    elif re.fullmatch(r'\.(jpg|jpeg|png)', extension, re.I):
                        dst = os.path.join(tmp_path, sub_file_name)
                        n = 1
                        while os.path.exists(dst):
                            sub_file_name = name + ' (' + str(n) + ')' + extension
                            dst = os.path.join(tmp_path, sub_file_name)
                            n += 1
                        shutil.move(sub_file_path, dst)
                    elif re.fullmatch(r'\.(avi|mp4|mkv|flac|midi|amr|ogg|aiff|mp3|wav|ppt|pptx|doc|docx|xls|xlsx|pdf)', extension, re.I):
                        dst = os.path.join(tmp_path, sub_file_name)
                        n = 1
                        while os.path.exists(dst):
                            sub_file_name = name + ' (' + str(n) + ')' + extension
                            dst = os.path.join(tmp_path, sub_file_name)
                            n += 1
                        shutil.move(sub_file_path, dst)
                    elif re.fullmatch(r'\.xml', extension, re.I):
                        dst = os.path.join(media_path, file_name)
                        n = 1
                        while os.path.exists(dst):
                            file_name = file_name + ' (' + str(n) + ')'
                            dst = os.path.join(media_path, file_name)
                            n += 1
                        shutil.move(file_path, dst)
                        break
                    else:
                        os.unlink(sub_file_path)
        else:
            name, extension = os.path.splitext(file_name)
            if re.fullmatch(r'\.(7z|ace|alz|a|arc|arj|bz2|cab|Z|cpio|deb|dms|gz|lrz|lha|lzh|lz|lzma|lzo|rpm|rar|rz|tar|xz|zip|jar|zoo)', extension, re.I):
                dir_path = os.path.join(zip_path, name)
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)
                Archive(file_path).extractall(dir_path)
                os.unlink(file_path)
                return check_input_files(media_path, tmp_path, zip_path)
            elif re.fullmatch(r'\.html', extension, re.I):
                dst = os.path.join(tmp_path, file_name)
                n = 1
                while os.path.exists(dst):
                    file_name = name + ' (' + str(n) + ')' + extension
                    dst = os.path.join(tmp_path, file_name)
                    n += 1
                shutil.move(file_path, dst)
                html_files.append(file_name)
            elif re.fullmatch(r'\.(jpg|jpeg|png)', extension, re.I):
                dst = os.path.join(tmp_path, file_name)
                n = 1
                while os.path.exists(dst):
                    file_name = name + ' (' + str(n) + ')' + extension
                    dst = os.path.join(tmp_path, file_name)
                    n += 1
                shutil.move(file_path, dst)
            elif re.fullmatch(r'\.(avi|mp4|mkv|xml|flac|midi|amr|ogg|aiff|mp3|wav|ppt|pptx|doc|docx|xls|xlsx|pdf)', extension, re.I):
                dst = os.path.join(tmp_path, file_name)
                n = 1
                while os.path.exists(dst):
                    file_name = name + ' (' + str(n) + ')' + extension
                    dst = os.path.join(tmp_path, file_name)
                    n += 1
                shutil.move(file_path, dst)
            else:
                os.unlink(file_path)
    return html_files


def join(request):
    template = loader.get_template('modules.html')
    context = {}
    if request.method == 'POST':
        form = forms.Join(request.POST)
        if form.is_valid():
            checked = request.POST.getlist('checked')
            files = request.POST.getlist('files')
            mod_name = request.POST['module-name']
            mod_type = request.POST['module-type']
            mod_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, mod_name)
            if not os.path.exists(mod_path):
                os.mkdir(mod_path)
                module = models.Module(
                    uid=request.session.session_key,
                    mod_name=mod_name,
                    mod_type=mod_type
                )
                module.save()

                if mod_type == 'theory' or mod_type == 'self-test':
                    os.mkdir(os.path.join(mod_path, 'HTML'))
                    os.mkdir(os.path.join(mod_path, 'HTML', 'img'))
                    for file in checked:
                        if re.fullmatch(r'.*\.html', file, re.I):
                            src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', file)
                            dst = os.path.join(mod_path, 'HTML', file)
                            shutil.move(src, dst)
                            f = open(dst, 'r', encoding='utf-8')
                            c = f.read()
                            f.close()
                            soup = bs4.BeautifulSoup(c, 'html.parser')
                            imgs = soup.find_all('img')
                            for img in imgs:
                                img_name = os.path.basename(img['src'])
                                img['src'] = os.path.join('img', img_name)
                                img_src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', img_name)
                                img_dst = os.path.join(mod_path, 'HTML', 'img', img_name)
                                if os.path.exists(img_src):
                                    shutil.move(img_src, img_dst)
                            f = open(dst, 'w', encoding='utf-8')
                            f.write(str(soup))
                            f.close()
                            files.remove(file)
                elif mod_type == 'control-test' or mod_type == 'exam-test':
                    os.mkdir(os.path.join(mod_path, 'img'))
                    for file in checked:
                        src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', file)
                        dst = None
                        if re.fullmatch(r'.*\.xml', file, re.I):
                            dst = os.path.join(mod_path, file)
                        elif re.fullmatch(r'.*\.(png|jpeg|jpg)', file, re.I):
                            dst = os.path.join(mod_path, 'img', file)
                        if dst is not None:
                            shutil.move(src, dst)
                elif mod_type == 'video-file' or mod_type == 'video-lecture' or mod_type == 'audio-file' or \
                    mod_type == 'audio-lecture' or mod_type == 'webinar':
                    for file in checked:
                        src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', file)
                        dst = os.path.join(mod_path, file)
                        shutil.move(src, dst)
                elif mod_type == 'presentation':
                    os.mkdir(os.path.join(mod_path, 'slides'))
                    for file in checked:
                        src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', file)
                        dst = None
                        if re.fullmatch(r'.*\.(xml|html)', file, re.I):
                            dst = os.path.join(mod_path, file)
                        elif re.fullmatch(r'.*\.(png|jpeg|jpg)', file, re.I):
                            dst = os.path.join(mod_path, 'slides', file)
                        if dst is not None:
                            shutil.move(src, dst)
            else:
                context['msg'] = 'Такое имя модуля уже существует. Введите другое имя модуля.'
                context['checked'] = checked
                context['mod_name'] = mod_name
            tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
            files = os.listdir(tmp_path)
            if len(files) != 0:
                template = loader.get_template('files.html')
                context['files'] = natsorted(files, key=lambda y: y.lower())
            else:
                shutil.rmtree(tmp_path)
                return redirect('/modules/')
    return HttpResponse(template.render(context, request))


def clear_media():
    if os.path.exists(settings.MEDIA_ROOT):
        for file_name in os.listdir(settings.MEDIA_ROOT):
            if not models.Session.objects.get(id=file_name).active:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT, file_name))
    else:
        os.mkdir(settings.MEDIA_ROOT)


def write_file(file, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def get_modules(request):
    res = []
    dir_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    for file_name in natsorted(os.listdir(dir_path), key=lambda y: y.lower()):
        if file_name != 'trash' and file_name != 'tmp':
            if re.fullmatch(r'theory\d*', file_name, re.I):
                file_type = 'theory'
            elif re.fullmatch(r'test\d*', file_name, re.I):
                file_type = 'self-test'
            elif re.fullmatch(r'control\d*', file_name, re.I):
                file_type = 'control-test'
            elif re.fullmatch(r'exam\d*', file_name, re.I):
                file_type = 'exam-test'
            elif re.fullmatch(r'presentation\d*', file_name, re.I):
                file_type = 'presentation'
            elif re.fullmatch(r'webinar\d*', file_name, re.I):
                file_type = 'webinar'
            elif re.fullmatch(r'audiofile\d*', file_name, re.I):
                file_type = 'audio-file'
            elif re.fullmatch(r'audiolecture\d*', file_name, re.I):
                file_type = 'audio-lecture'
            elif re.fullmatch(r'videofile\d*', file_name, re.I):
                file_type = 'video-file'
            elif re.fullmatch(r'videolecture\d*', file_name, re.I):
                file_type = 'video-lecture'
            else:
                file_type = 'unknown-file'
            res.append({
                'name': file_name,
                'type': file_type
            })
    return res


def linear_analyze_file(file):
    txt_ch = analyzer.text_characteristics(file)
    img_ch = analyzer.img_characteristics(file)
    san_ch = analyzer.search_and_nav_characteristics(file)

    res = {
        'txt_ch': txt_ch,
        'img_ch': img_ch,
        'san_ch': san_ch
    }

    return res


def parallel_analyze_file(file):
    p = ThreadPool(processes=os.cpu_count())

    txt_ch = p.apply_async(analyzer.text_characteristics, (file,))
    img_ch = p.apply_async(analyzer.img_characteristics, (file,))
    san_ch = p.apply_async(analyzer.search_and_nav_characteristics, (file,))

    p.close()
    p.join()

    res = {
        'txt_ch': txt_ch.get(),
        'img_ch': img_ch.get(),
        'san_ch': san_ch.get()
    }

    return res


def parallel_analyze_file_with_futures(file, indicators):

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        txt_ch = executor.submit(analyzer.text_characteristics, file, indicators)
        img_ch = executor.submit(analyzer.img_characteristics, file, indicators)
        san_ch = executor.submit(analyzer.search_and_nav_characteristics, file, indicators)

    res = {
        'txt_ch': txt_ch.result(),
        'img_ch': img_ch.result(),
        'san_ch': san_ch.result()
    }

    return res


def linear_analyze(files):
    files.pop(0)

    start_time = time()

    results = [linear_analyze_file(file) for file in files]

    txt_ch = analyzer.text_characteristics_all_files(results)
    img_ch = analyzer.img_characteristics_all_files(results)
    san_ch = analyzer.search_and_nav_characteristics_all_files(results)

    results.insert(0, {
        'txt_ch': txt_ch,
        'img_ch': img_ch,
        'san_ch': san_ch
    })

    finish_time = time()

    print(f'Linear analyze: {finish_time - start_time}')

    return results


def parallel_analyze(files):
    files.pop(0)

    start_time = time()

    p = ThreadPool(processes=os.cpu_count())
    res = p.map(parallel_analyze_file, files)
    p.close()
    p.join()

    p = ThreadPool(processes=os.cpu_count())

    txt_ch = p.apply_async(analyzer.text_characteristics_all_files, (res,))
    img_ch = p.apply_async(analyzer.img_characteristics_all_files, (res,))
    san_ch = p.apply_async(analyzer.search_and_nav_characteristics_all_files, (res,))

    p.close()
    p.join()

    res.insert(0, {
        'txt_ch': txt_ch.get(),
        'img_ch': img_ch.get(),
        'san_ch': san_ch.get()
    })

    finish_time = time()
    print(f'Parallel analyze: {finish_time - start_time}')
    return res


def parallel_analyze_with_futures(files, indicators):
    files.pop(0)

    start_time = time()

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(parallel_analyze_file_with_futures, file, indicators) for file in files]

    results = [future.result() for future in futures]

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        txt_ch = executor.submit(analyzer.text_characteristics_all_files, results, indicators)
        img_ch = executor.submit(analyzer.img_characteristics_all_files, results, indicators)
        san_ch = executor.submit(analyzer.search_and_nav_characteristics_all_files, results, indicators)

    results.insert(0, {
        'txt_ch': txt_ch.result(),
        'img_ch': img_ch.result(),
        'san_ch': san_ch.result()
    })

    finish_time = time()

    print(f'Parallel analyze with futures: {finish_time - start_time}')

    return results


def theory_analysis_results(request):
    if request.method == 'POST':
        indicators = request.POST.getlist('indicators')
        media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
        theory_path = os.path.join(media_path, 'theory')
        theory_modules = os.listdir(theory_path)
        if len(theory_modules) > 0:
            files = analyzer.read_files(theory_path, theory_modules)
            # results = linear_analyze(files)
            # results = parallel_analyze(files)
            results = parallel_analyze_with_futures(files, indicators)
            context = {
                'modules': list(zip(
                    ['all'] + [os.path.splitext(module)[0] for module in theory_modules],
                    ['Анализ всего текста'] + ['Анализ модуля ' + module for module in theory_modules],
                    results
                )),
                'indicators': indicators
            }
            return render(request, 'theory-analysis-results.html', context)
        else:
            return render(request, 'theory-analysis-results.html', {'modules': []})
    else:
        return render(request, 'modules.html', {'modules': get_modules(request)})


def del_last_module(request):
    module_name = request.POST['module_name']
    dir_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, module_name)
    if os.path.exists(dir_path):
        modules = models.Module.objects.all()
        module = None
        for mod in modules:
            if mod.uid == request.session.session_key and mod.mod_name == module_name:
                module = mod
        if module is not None:
            tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
            if not os.path.exists(tmp_path):
                os.mkdir(tmp_path)
            move_file_to_tmp(dir_path, tmp_path)
            shutil.rmtree(dir_path)
            module.delete()
        return JsonResponse({'res': True})
    return JsonResponse({'res': False})


def move_file_to_tmp(dir_path, tmp_path):
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            src = file_path
            dst = os.path.join(tmp_path, file)
            shutil.move(src, dst)
        else:
            move_file_to_tmp(file_path, tmp_path)


def module_exist(request, files_names, module_name):
    module_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, module_name)
    if os.path.exists(module_path):
        html_path = os.path.join(module_path, 'HTML')
        for file_name in os.listdir(html_path):
            file_path = os.path.join(html_path, file_name)
            if not os.path.isdir(file_path):
                if file_name not in files_names:
                    return False
        return True
    return False


def modules(request):
    template = loader.get_template('modules.html')
    modules = get_modules(request)
    context = {'modules': modules}
    return HttpResponse(template.render(context, request))


def unload(request):
    session = models.Session.objects.get(id=request.session.session_key)
    session.active = False
    session.save()
    return JsonResponse({'res': True})


def load(request):
    session = models.Session.objects.get(id=request.session.session_key)
    session.active = True
    session.save()
    return JsonResponse({'res': True})


def self_test_analysis(request):
    self_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'self-test')
    modules = os.listdir(self_test_path)
    questions = []
    for module in modules:
        dir_path = os.path.join(self_test_path, module, 'HTML')
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                questions.append(get_questions(file_path))
    context = {
        'modules': list(zip(
            [os.path.splitext(module)[0] for module in modules],
            ['Анализ модуля ' + module for module in modules],
            questions
        ))
    }
    return render(request, 'self-test-analysis.html', context)


def get_questions(html_path):
    f = open(html_path, 'r', encoding='utf-8')
    c = f.read()
    f.close()
    soup = bs4.BeautifulSoup(c, 'html.parser')
    questions = soup.find_all('div', 'qheader')
    res = []
    for question in questions:
        p = question.find('p')
        if p is not None and p.string is not None:
            res.append(p.string)
    return res


def self_test_analysis_results(request):
    pass


def control_test_analysis(request):
    control_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'control-test')
    exam_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'exam-test')
    control_test_modules = os.listdir(control_test_path)
    exam_test_modules = os.listdir(exam_test_path)
    all_questions = []
    for module in control_test_modules:
        dir_path = os.path.join(control_test_path, module)
        questions = []
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                questions += get_control_questions(file_path)
        all_questions.append(questions)
    for module in exam_test_modules:
        dir_path = os.path.join(exam_test_path, module)
        questions = []
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                questions += get_control_questions(file_path)
        all_questions.append(questions)
    context = {
        'modules': list(zip(
            [os.path.splitext(module)[0] for module in control_test_modules + exam_test_modules],
            ['Анализ модуля ' + module for module in control_test_modules + exam_test_modules],
            all_questions
        ))
    }
    return render(request, 'control-test-analysis.html', context)


def get_control_questions(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    c = f.read()
    f.close()
    soup = bs4.BeautifulSoup(c, 'html.parser')
    questions = soup.find_all('questiontext')
    res = []
    for question in questions:
        text = question.find('text')
        if text is not None:
            m = re.match(r'<text><!\[CDATA\[\s*(?P<text>(.|\s)+(?!\]\]>))\s*\]\]></text>', str(text))
            if m is not None:
                soup = bs4.BeautifulSoup(m.group('text'), 'html.parser')
                imgs = soup.find_all('img')
                for img in imgs:
                    try:
                        idx = file_path.index('\media')
                        if idx >= 0:
                            img['src'] = os.path.join(os.path.dirname(file_path)[idx:], img['src'])
                    except Exception as e:
                        print(e)
                res.append(str(soup))
            #soup = bs4.BeautifulSoup(text.string, 'html.parser')
            #fragments = re.split(r'</?[^>]+>', text.string)
            #res.append(html.unescape(' '.join(fragments)))
            #res.append(str(soup))
    return res


def control_test_analysis_results(request):
    return redirect('/videofile-modules/')


def video_file_analysis(request):
    video_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-file')
    modules = []
    for dir_name in os.listdir(video_file_path):
        dir_path = os.path.join(video_file_path, dir_name)
        for file_name in os.listdir(dir_path):
            modules.append(os.path.join('/media', request.session.session_key, 'video-file', dir_name, file_name))

    names = []
    extensions = []
    src = []
    for module in modules:
        name, extension = os.path.splitext(os.path.basename(module))
        names.append(name)
        extensions.append(extension[1:])
        src.append(module)

    context = {
        'modules': list(zip(
            names,
            extensions,
            src
        ))
    }

    return render(request, 'video-file-analysis.html', context)


def video_lecture_analysis(request):
    video_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-lecture')
    theory_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'theory')
    modules = []
    for dir_name in os.listdir(video_lecture_path):
        dir_path = os.path.join(video_lecture_path, dir_name)
        for file_name in os.listdir(dir_path):
            modules.append(os.path.join('/media', request.session.session_key, 'video-lecture', dir_name, file_name))

    names = []
    extensions = []
    src = []
    for module in modules:
        name, extension = os.path.splitext(os.path.basename(module))
        names.append(name)
        extensions.append(extension[1:])
        src.append(module)

    context = {
        'modules': list(zip(
            names,
            extensions,
            src
        )),
        'sections': os.listdir(theory_path)
    }

    return render(request, 'video-lecture-analysis.html', context)


def admin_settings(request):
    user = auth.get_user(request)
    template = loader.get_template('admin-settings.html')
    context = {'username': user.username}

    scales = models.Scale.objects.all()
    if len(scales) != 0:
        context['scales'] = scales

    indicators = models.Indicator.objects.all()
    if len(indicators) != 0:
        context['indicators'] = indicators

    return HttpResponse(template.render(context, request))


def add_scale(request):
    user = auth.get_user(request)
    context = {'username': user.username}
    if request.method == 'POST':
        scale_name = request.POST.get('scale-name')
        scale_type = request.POST.get('scale-type')
        if scale_type == 'ordinal-scale':
            min_val = request.POST.get('min-val')
            max_val = request.POST.get('max-val')
            step = request.POST.get('step')
            scale_attr = {
                'min': min_val,
                'max': max_val,
                'step': step
            }
        elif scale_type == 'interval-scale':
            values = request.POST.getlist('values') or request.POST.getlist('values[]')
            scale_attr = natsorted(values, key=lambda y: y.lower())
        else:
            scale_attr = None
        scale = models.Scale(
            name=scale_name,
            type=scale_type,
            attr=json.dumps(scale_attr)
        )
        scale.save()
    return render(request, 'add-scale.html', context)


def moodle(request):
    user = auth.get_user(request)
    context = {
        'username': user.username if not user.is_anonymous else 'Anonymous',
        'is_superuser': user.is_superuser,
        'is_anonymous': user.is_anonymous,
    }
    if request.method == 'POST':
        moodle = request.POST.get('moodle')
        course_id = request.POST.get('course-id')
        response = requests.get(f'https://online.tusur.ru/local/filemap/?courseid={course_id}&key=cea17f418fc4227b647f75fe66fe859bd24ea752')
        if response.status_code == 200:
            modules = response.json()
            media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
            futures = []

            for module in modules:
                fragments = re.findall(r'[a-zA-Zа-яА-Я0-9_\s]+', module['name'])
                module_path = os.path.join(media_path, ''.join(fragments) + ' ' + module['contextid'])
                print(module_path)
                if not os.path.exists(module_path):
                    os.mkdir(module_path)
                    if module['plugin'] == 'mod_imscp':
                        html_path = os.path.join(module_path, 'html')
                        img_path = os.path.join(module_path, 'html', 'img')
                        os.mkdir(html_path)
                        os.mkdir(img_path)
                    elif module['plugin'] == 'mod_resource':
                        img_path = os.path.join(module_path, 'slides')
                        os.mkdir(img_path)
                with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                    futures += [executor.submit(download_file, file, module, module_path) for file in module['files']]

            for future in futures:
                future.result()

        context['modules'] = get_modules(request)
        return render(request, 'modules.html', context)
    else:
        return render(request, 'index.html', context)


def download_file(file, module, module_path):
    file_paath = os.path.join(module_path, file['name'])
    if module['plugin'] == 'mod_imscp':
        html_path = os.path.join(module_path, 'html')
        img_path = os.path.join(module_path, 'html', 'img')
        if re.fullmatch(r'.+\.html', file['name'], re.I):
            file_paath = os.path.join(html_path, file['name'])
        elif re.fullmatch(r'.+\.(png|jpeg|jpg)', file['name'], re.I):
            file_paath = os.path.join(img_path, file['name'])
    elif module['plugin'] == 'mod_resource':
        img_path = os.path.join(module_path, 'slides')
        if re.fullmatch(r'.+\.(png|jpeg|jpg)', file['name'], re.I):
            file_paath = os.path.join(img_path, file['name'])
    response = requests.get(file['url'])
    if response.status_code == 200:
        with open(file_paath, 'w', encoding='utf-8') as f:
            f.write(response.text)


def get_files_from_moodle(request):
    moodle = request.POST.get('moodle')
    course_id = request.POST.get('course-id')
    if moodle == 'online':
        connection = sql.connect(
            host='172.16.8.31',
            port=3306,
            user='aio',
            passwd='acw-6l8q',
            db='online',
            charset='utf8',
            init_command='SET NAMES UTF8'
        )
    elif moodle == 'new-online':
        connection = sql.connect(
            host='172.16.9.53',
            port=3306,
            user='aio',
            passwd='acw-6l8q',
            db='moodle_online',
            charset='utf8',
            init_command='SET NAMES UTF8'
        )
    elif moodle == 'sdo':
        connection = sql.connect(
            host='172.16.9.65',
            port=3306,
            user='aio',
            passwd='acw-6l8q',
            db='edu',
            charset='utf8',
            init_command='SET NAMES UTF8'
        )
    elif moodle == 'mooc':
        connection = sql.connect(
            host='172.16.8.31',
            port=3306,
            user='aio',
            passwd='acw-6l8q',
            db='mooc',
            charset='utf8',
            init_command='SET NAMES UTF8'
        )
    else:
        connection = None

    if connection is not None:
        res = pd.read_sql(
            """
            """,
            connection,
            params=[course_id]
        )


def move_files_to_tmp(request):
    files = models.File.objects.all()
    for file in files:
        if file.uid == request.session.session_key:
            src = file.src
            dst = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', os.path.basename(src))
            shutil.move(src, dst)
            file.delete()
    return JsonResponse({'res': True})


def audio_file_analysis(request):
    audio_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-file')
    modules = []
    for dir_name in os.listdir(audio_file_path):
        dir_path = os.path.join(audio_file_path, dir_name)
        for file_name in os.listdir(dir_path):
            modules.append(os.path.join('/media', request.session.session_key, 'audio-file', dir_name, file_name))

    names = []
    extensions = []
    src = []
    for module in modules:
        name, extension = os.path.splitext(os.path.basename(module))
        names.append(name)
        extensions.append(extension[1:])
        src.append(module)

    context = {
        'modules': list(zip(
            names,
            extensions,
            src
        ))
    }

    return render(request, 'audio-file-analysis.html', context)


def audio_lecture_analysis(request):
    audio_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-lecture')
    theory_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'theory')
    modules = []
    for dir_name in os.listdir(audio_lecture_path):
        dir_path = os.path.join(audio_lecture_path, dir_name)
        for file_name in os.listdir(dir_path):
            modules.append(os.path.join('/media', request.session.session_key, 'audio-lecture', dir_name, file_name))

    names = []
    extensions = []
    src = []
    for module in modules:
        name, extension = os.path.splitext(os.path.basename(module))
        names.append(name)
        extensions.append(extension[1:])
        src.append(module)

    context = {
        'modules': list(zip(
            names,
            extensions,
            src
        )),
        'sections': os.listdir(theory_path)
    }

    return render(request, 'audio-lecture-analysis.html', context)


def webinar_analysis(request):
    webinar_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'webinar')
    modules = os.listdir(webinar_path)

    names = []
    all_videos = []
    all_pictures = []
    all_audios = []
    all_presentations = []
    all_documents = []
    all_tables = []
    all_pdfs = []
    all_others = []
    for module in modules:
        names.append(module)
        videos = []
        pictures = []
        audios = []
        presentations = []
        documents = []
        tables = []
        pdfs = []
        others = []
        dir_path = os.path.join(webinar_path, module)
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                name, extension = os.path.splitext(file_name)
                if re.fullmatch(r'\.(avi|mp4|mkv)', extension):
                    videos.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'extension': extension[1:]
                    })
                elif re.fullmatch(r'\.(jpg|jpeg|png)', extension):
                    pictures.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
                elif re.fullmatch(r'\.(flac|midi|amr|ogg|aiff|mp3|wav)', extension):
                    audios.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'extension': extension[1:]
                    })
                elif re.fullmatch(r'\.(ppt|pptx)', extension):
                    presentations.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
                elif re.fullmatch(r'\.(doc|docx)', extension):
                    documents.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
                elif re.fullmatch(r'\.(xls|xlsx)', extension):
                    tables.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
                elif re.fullmatch(r'\.(pdf)', extension):
                    pdfs.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
                else:
                    others.append({
                        'src': os.path.join('/media', request.session.session_key, 'webinar', module, file_name),
                        'name': name
                    })
            all_videos.append(videos)
            all_pictures.append(pictures)
            all_audios.append(audios)
            all_presentations.append(presentations)
            all_documents.append(documents)
            all_tables.append(tables)
            all_pdfs.append(pdfs)
            all_others.append(others)

    context = {
        'modules': list(zip(
            names,
            all_videos,
            all_pictures,
            all_audios,
            all_presentations,
            all_documents,
            all_tables,
            all_pdfs,
            all_others
        ))
    }

    return render(request, 'webinar-analysis.html', context)


def remove_selected_files(request):
    tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
    context = {'files': natsorted(os.listdir(tmp_path), key=lambda y: y.lower())}
    trash_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'trash')
    if not os.path.exists(trash_path):
        os.mkdir(trash_path)
    if request.method == 'POST':
        files_names = request.POST.getlist('checked')
        for file_name in files_names:
            file_path = os.path.join(tmp_path, file_name)
            if os.path.exists(file_path):
                src = file_path
                dst = os.path.join(trash_path, file_name)
                shutil.move(src, dst)
                file = models.File(
                    uid=request.session.session_key,
                    src=dst
                )
                file.save()
        context['files'] = natsorted(os.listdir(tmp_path), key=lambda y: y.lower())
        if len(context['files']) == 0:
            shutil.rmtree(tmp_path)
            return redirect('/modules/')
    return render(request, 'files.html', context)


def file_action(request):
    if 'join' in request.POST:
        return join(request)
    elif 'remove' in request.POST:
        return remove_selected_files(request)
    return redirect('/files/')


def return_deleted_files(request):
    files_names = request.POST.getlist('files_names[]')
    trash_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'trash')
    tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if os.path.exists(trash_path):
        files = models.File.objects.all()
        for file in files:
            file_name = os.path.basename(file.src)
            if file.uid == request.session.session_key and file_name in files_names:
                src = file.src
                dst = os.path.join(tmp_path, file_name)
                shutil.move(src, dst)
                file.delete()
    return JsonResponse({'res': True})


def complete_analysis(request):
    pass


def check_scale_name(request):
    scale_name = request.POST.get('scale-name')
    scales = models.Scale.objects.all()
    for scale in scales:
        if scale.name == scale_name:
            return JsonResponse({'res': True})
    return JsonResponse({'res': False})


def get_scale(request):
    scale_name = request.POST.get('scale-name')
    scale = models.Scale.objects.get(name=scale_name)
    return JsonResponse(json.loads(str(scale)))


def delete_scale(request):
    scale_name = request.POST.get('scale-name')
    scale = models.Scale.objects.get(name=scale_name)
    scale.delete()
    return JsonResponse({'res': True})


def add_indicator(request):
    user = auth.get_user(request)
    context = {'username': user.username}
    if request.method == 'POST':
        indicator_name = request.POST.get('indicator-name')
        indicator_type = request.POST.get('indicator-type')
        indicator_show = request.POST.get('indicator-show')
        print(indicator_show)
        indicator = models.Indicator(
            name=indicator_name,
            type=indicator_type,
            show=True if indicator_show == 'on' else False
        )
        indicator.save()
    return render(request, 'add-indicator.html', context)


def delete_indicator(request):
    indicator_name = request.POST.get('indicator-name')
    indicator = models.Indicator.objects.get(name=indicator_name)
    indicator.delete()
    return JsonResponse({'res': True})


def hide_indicator(request):
    indicator_name = request.POST.get('indicator-name')
    indicator = models.Indicator.objects.get(name=indicator_name)
    indicator.show = False
    indicator.save()
    return JsonResponse({'res': True})


def show_indicator(request):
    indicator_name = request.POST.get('indicator-name')
    indicator = models.Indicator.objects.get(name=indicator_name)
    indicator.show = True
    indicator.save()
    return JsonResponse({'res': True})


def check_indicator_name(request):
    indicator_name = request.POST.get('indicator-name')
    indicators = models.Indicator.objects.all()
    for indicator in indicators:
        if indicator.name == indicator_name:
            return JsonResponse({'res': True})
    return JsonResponse({'res': False})


def indicators(request):
    user = auth.get_user(request)
    context = {
        'username': user.username if not user.is_anonymous else 'Anonymous',
        'is_superuser': user.is_superuser,
        'is_anonymous': user.is_anonymous,
    }
    if request.method == 'POST':
        modules = request.POST.getlist('modules')

        media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
        tmp_path = os.path.join(media_path, 'tmp')
        theory_path = os.path.join(media_path, 'theory')
        self_test_path = os.path.join(media_path, 'self-test')
        control_test_path = os.path.join(media_path, 'control-test')
        exam_test_path = os.path.join(media_path, 'exam-test')
        video_file_path = os.path.join(media_path, 'video-file')
        video_lecture_path = os.path.join(media_path, 'video-lecture')
        audio_file_path = os.path.join(media_path, 'audio-file')
        audio_lecture_path = os.path.join(media_path, 'audio-lecture')
        webinar_path = os.path.join(media_path, 'webinar')
        presentation_path = os.path.join(media_path, 'presentation')

        if not os.path.exists(tmp_path):
            file_names = os.listdir(media_path)

            os.mkdir(tmp_path)
            os.mkdir(theory_path)
            os.mkdir(self_test_path)
            os.mkdir(control_test_path)
            os.mkdir(exam_test_path)
            os.mkdir(video_file_path)
            os.mkdir(video_lecture_path)
            os.mkdir(audio_file_path)
            os.mkdir(audio_lecture_path)
            os.mkdir(webinar_path)
            os.mkdir(presentation_path)

            for file_name in file_names:
                src = os.path.join(media_path, file_name)
                dst = os.path.join(tmp_path, file_name)
                shutil.move(src, dst)

        for module in modules:
            file_type = request.POST.get('type-' + module)
            src = os.path.join(tmp_path, module)
            if file_type == 'theory':
                dst = os.path.join(theory_path, module)
            elif file_type == 'self-test':
                dst = os.path.join(self_test_path, module)
            elif file_type == 'control-test':
                dst = os.path.join(control_test_path, module)
            elif file_type == 'exam-test':
                dst = os.path.join(exam_test_path, module)
            elif file_type == 'video-file':
                dst = os.path.join(video_file_path, module)
            elif file_type == 'video-lecture':
                dst = os.path.join(video_lecture_path, module)
            elif file_type == 'audio-file':
                dst = os.path.join(audio_file_path, module)
            elif file_type == 'audio-lecture':
                dst = os.path.join(audio_lecture_path, module)
            elif file_type == 'webinar':
                dst = os.path.join(webinar_path, module)
            elif file_type == 'presentation':
                dst = os.path.join(presentation_path, module)
            else:
                dst = None

            if dst is not None and os.path.exists(src):
                models.File(
                    uid=request.session.session_key,
                    src=dst
                ).save()
                shutil.move(src, dst)

        context['indicators'] = models.Indicator.objects.filter(show=True)
        return render(request, 'indicators.html', context)
    else:
        context['modules'] = get_modules(request)
        return render(request, 'modules.html', context)
