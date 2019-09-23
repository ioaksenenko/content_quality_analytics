import os
import re
import shutil
import sys
import bs4
import datetime

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


def index(request):
    clear_media()
    request.session.create()
    session = models.Session(id=request.session.session_key, active=True)
    session.save()
    os.mkdir(os.path.join(settings.MEDIA_ROOT, request.session.session_key))
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def upload_file(request):
    if request.method == 'POST':
        context = {}
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # clear_media()
            tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
            html_path = os.path.join(tmp_path, 'html')
            img_path = os.path.join(tmp_path, 'img')
            if not os.path.exists(tmp_path):
                os.mkdir(tmp_path)
                os.mkdir(html_path)
                os.mkdir(img_path)
            html_files = []
            files = request.FILES.getlist('files')
            if len(files) != 0:
                for file in files:
                    file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, file.name)
                    write_file(file, file_path)
                    name, extension = os.path.splitext(file_path)
                    if re.fullmatch(r'\.(7z|ace|alz|a|arc|arj|bz2|cab|Z|cpio|deb|dms|gz|lrz|lha|lzh|lz|lzma|lzo|rpm|rar|rz|tar|xz|zip|jar|zoo)', extension, re.I):
                        Archive(file_path).extractall(os.path.join(settings.MEDIA_ROOT, request.session.session_key))
                        os.unlink(file_path)
                    elif re.fullmatch(r'\.html', extension, re.I):
                        shutil.move(file_path, os.path.join(html_path, file.name))
                        html_files.append(file.name)
                    elif re.fullmatch(r'\.(jpg|jpeg|png)', extension, re.I):
                        shutil.move(file_path, os.path.join(img_path, file.name))
                    else:
                        os.unlink(file_path)
            else:
                context['msg'] = "Файл не был загружен."
            if len(html_files) != 0:
                template = loader.get_template('files.html')
                context['files'] = natsorted(html_files, key=lambda y: y.lower())
            else:
                shutil.rmtree(tmp_path)
                return redirect('/modules/')
            return HttpResponse(template.render(context, request))
    else:
        form = forms.UploadFileForm()
    return render(request, 'index.html', {'form': form})


def join(request):
    template = loader.get_template('modules.html')
    context = {}
    if request.method == 'POST':
        form = forms.Join(request.POST)
        if form.is_valid():
            checked = request.POST.getlist('checked')
            files = request.POST.getlist('files')
            mod_name = request.POST['module-name']
            mod_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, mod_name)
            if not os.path.exists(mod_path):
                os.mkdir(mod_path)
                os.mkdir(os.path.join(mod_path, 'HTML'))
                os.mkdir(os.path.join(mod_path, 'HTML', 'img'))
                module = models.Module(
                    uid=request.session.session_key,
                    name=mod_name
                )
                module.save()
                for file in checked:
                    src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', 'html', file)
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
                        img_src = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp', 'img', img_name)
                        img_dst = os.path.join(mod_path, 'HTML', 'img', img_name)
                        if os.path.exists(img_src):
                            shutil.move(img_src, img_dst)
                    f = open(dst, 'w', encoding='utf-8')
                    f.write(str(soup))
                    f.close()
                    files.remove(file)
            else:
                context['msg'] = 'Такое имя модуля уже существует. Введите другое имя модуля.'
                context['checked'] = checked
                context['mod_name'] = mod_name
            if len(files) != 0:
                template = loader.get_template('files.html')
                context['files'] = natsorted(files, key=lambda y: y.lower())
            else:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp'))
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
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isdir(file_path):
            res.append(file_name)
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


def parallel_analyze_file_with_futures(file):

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        txt_ch = executor.submit(analyzer.text_characteristics, file)
        img_ch = executor.submit(analyzer.img_characteristics, file)
        san_ch = executor.submit(analyzer.search_and_nav_characteristics, file)

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


def parallel_analyze_with_futures(files):
    files.pop(0)

    start_time = time()

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(parallel_analyze_file_with_futures, file) for file in files]

    results = [future.result() for future in futures]

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        txt_ch = executor.submit(analyzer.text_characteristics_all_files, results)
        img_ch = executor.submit(analyzer.img_characteristics_all_files, results)
        san_ch = executor.submit(analyzer.search_and_nav_characteristics_all_files, results)

    results.insert(0, {
        'txt_ch': txt_ch.result(),
        'img_ch': img_ch.result(),
        'san_ch': san_ch.result()
    })

    finish_time = time()

    print(f'Parallel analyze with futures: {finish_time - start_time}')

    return results


def analyze(request):
    if request.method == 'POST':
        form = forms.Analyze(request.POST)
        if form.is_valid():
            modules = request.POST.getlist('modules')
            files = analyzer.read_files(os.path.join(settings.MEDIA_ROOT, request.session.session_key), modules)

            results = linear_analyze(files)
            # results = parallel_analyze(files)
            # results = parallel_analyze_with_futures(files)

            template = loader.get_template('analyze.html')
            context = {
                'modules': list(zip(
                    ['all'] + [os.path.splitext(module)[0] for module in modules],
                    ['Анализ всего текста'] + ['Анализ модуля ' + module for module in modules],
                    results
                ))
            }
            return HttpResponse(template.render(context, request))
    else:
        form = forms.UploadFileForm()
    return render(request, 'modules.html', {'form': form})


def del_last_module(request):
    files_names = request.POST.getlist('files_names[]')
    module_name = request.POST['module_name']
    if module_exist(request, files_names, module_name):
        modules = models.Module.objects.all()
        module = None
        for mod in modules:
            if mod.uid == request.session.session_key and mod.name == module_name:
                module = mod
        if module is not None:
            dir_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, module.name)
            html_path = os.path.join(dir_path, 'HTML')
            img_path = os.path.join(dir_path, 'HTML', 'img')
            tmp_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'tmp')
            tmp_html = os.path.join(tmp_path, 'html')
            tmp_img = os.path.join(tmp_path, 'img')
            if not os.path.exists(tmp_path):
                os.mkdir(tmp_path)
                os.mkdir(tmp_html)
                os.mkdir(tmp_img)
            for file_name in os.listdir(html_path):
                file_path = os.path.join(html_path, file_name)
                if not os.path.isdir(file_path):
                    shutil.move(file_path, os.path.join(tmp_html, file_name))
            for file_name in os.listdir(img_path):
                shutil.move(os.path.join(img_path, file_name), os.path.join(tmp_img, file_name))
            shutil.rmtree(dir_path)
            module.delete()
        return JsonResponse({'res': True})
    return JsonResponse({'res': False})


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


def show_modules(request):
    template = loader.get_template('modules.html')
    modules = get_modules(request)
    context = {'modules': natsorted(modules, key=lambda y: y.lower())}
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