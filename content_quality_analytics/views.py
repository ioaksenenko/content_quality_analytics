import os
import shutil
import sys

from django.http import HttpResponse, HttpResponseRedirect
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


def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def upload_file(request):
    if request.method == 'POST':
        context = {}
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            clear_media()
            modules = []
            if 'zip-file' in request.FILES:
                file = request.FILES['zip-file']
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)
                write_file(file, file_path)
                Archive(file_path).extractall(settings.MEDIA_ROOT)
                os.remove(file_path)
                modules = get_modules()
            elif 'html-files' in request.FILES:
                files = request.FILES.getlist('html-files')
                dir_path = os.path.join(settings.MEDIA_ROOT, 'HTML')
                os.mkdir(dir_path)
                for file in files:
                    file_path = os.path.join(dir_path, file.name)
                    write_file(file, file_path)
                    modules.append(file.name)
            else:
                context['msg'] = "Файл не был загружен."
            template = loader.get_template('modules.html')
            context['modules'] = natsorted(modules, key=lambda y: y.lower())
            return HttpResponse(template.render(context, request))
    else:
        form = forms.UploadFileForm()
    return render(request, 'index.html', {'form': form})


def clear_media():
    for file_name in os.listdir(settings.MEDIA_ROOT):
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def write_file(file, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def get_modules():
    res = []
    for file_name in os.listdir(settings.MEDIA_ROOT):
        dir_path = os.path.join(settings.MEDIA_ROOT, file_name)
        if os.path.isdir(dir_path):
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                if os.path.isdir(file_path):
                    res.append(file_name)
    return res


def parallel_analyze_file(file):
    p = ThreadPool(processes=3)

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


def analyze_file(file):
    txt_ch = analyzer.text_characteristics(file)
    img_ch = analyzer.img_characteristics(file)
    san_ch = analyzer.search_and_nav_characteristics(file)

    res = {
        'txt_ch': txt_ch,
        'img_ch': img_ch,
        'san_ch': san_ch
    }

    return res


def parallel_analyze(files):
    start_time = time()
    p = ThreadPool(processes=os.cpu_count())
    res = p.map(analyze_file, files)
    p.close()
    p.join()
    finish_time = time()
    print(f'Parallel analyze: {finish_time - start_time}')
    return res


def parallel_analyze_with_futures(files):
    print(len(files))
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


def linear_analyze(files):
    files.pop(0)

    start_time = time()

    results = [analyze_file(file) for file in files]

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


def analyze(request):
    if request.method == 'POST':
        form = forms.Analyze(request.POST)
        if form.is_valid():
            modules = request.POST.getlist('modules')
            results = []
            for file_name in os.listdir(settings.MEDIA_ROOT):
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                if os.path.isdir(file_path):
                    files = analyzer.read_files(file_path, modules)
                    # results = linear_analyze(files)
                    # results = parallel_analyze(files)
                    results = parallel_analyze_with_futures(files)

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
