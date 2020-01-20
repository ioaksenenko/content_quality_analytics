import os
import re
import shutil
import bs4
import json
import requests
import django
django.setup()

from django.http import JsonResponse
from django.shortcuts import render
from . import settings
from natsort import natsorted
from . import analyzer
from time import time
from concurrent.futures import ProcessPoolExecutor
from . import models
from django.shortcuts import redirect
from django.contrib import auth
from datetime import datetime
from django.utils.timezone import pytz


class Analytics:

    @staticmethod
    def index(request):
        models.Module.objects.all().delete()
        models.File.objects.all().delete()
        models.Scale.objects.all().delete()
        models.Indicator.objects.all().delete()
        models.Results.objects.all().delete()
        models.Course.objects.all().delete()
        user = auth.get_user(request)
        request.session.create()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        os.mkdir(os.path.join(settings.MEDIA_ROOT, request.session.session_key))
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
        }
        return render(request, 'index.html', context)

    @staticmethod
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

            request.session['course_id'] = course_id
            request.session['moodle'] = moodle
            request.session.save()

            response = requests.get(
                f'https://online.tusur.ru/local/filemap/?courseid={course_id}&key=cea17f418fc4227b647f75fe66fe859bd24ea752'
            )
            if response.status_code == 200:
                modules = response.json()
                response.close()
                media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
                futures = []

                for module in modules:
                    module_path = os.path.join(media_path, module['cmid'])
                    models.Module(
                        uid=request.session.session_key,
                        sdo=moodle,
                        cid=course_id,
                        mid=module['cmid'],
                        sec_name=module['section_name'] if module['section_name'] is not None else 'Тема ' + module[
                            'section'],
                        mod_name=module['name']
                    ).save()
                    if not os.path.exists(module_path):
                        os.mkdir(module_path)
                    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                        futures += [executor.submit(Analytics.download_file, file, module, module_path) for file in
                                    module['files']]
                for future in futures:
                    future.result()
            return redirect('/modules/')
        else:
            return render(request, 'index.html', context)

    @staticmethod
    def download_file(file, module, module_path):
        file_path = os.path.join(module_path, file['name'])
        response = requests.get(file['url'])
        if response.status_code == 200:
            if re.fullmatch(r'.+\.(png|jpeg|jpg|flac|midi|amr|ogg|aiff|mp3|wav|avi|mp4|mkv|doc|docx|lsx|xlsx|ppt|pptx)',
                            file['name'], re.I):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
        response.close()

    @staticmethod
    def modules(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
            'modules': Analytics.get_modules(request)
        }
        return render(request, 'modules.html', context)

    @staticmethod
    def get_modules(request):
        res = []
        modules = models.Module.objects.filter(
            uid=request.session.session_key,
            sdo=request.session['moodle'],
            cid=request.session['course_id']
        )
        dir_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
        for module in modules:
            file_name = str(module.mid)
            module_name = ''.join(re.findall(r'[a-zA-Zа-яА-Я0-9_\s]+', module.mod_name)).replace(' ', '_')
            if re.fullmatch(
                    r'^(theory|введение|глоссарий|заключение|карта_курса|литература|сведения_об_авторе|список_сокращений|теоретический_материал|abbreviature|authors|conclusion|glossary|introduction|karta|literature|\d+).*$',
                    module_name, re.I):
                file_type = 'theory'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(html)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(test|самоконтроль).*$', module_name, re.I):
                file_type = 'self-test'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(html)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(control|контрольная_работа).*$', module_name, re.I):
                file_type = 'control-test'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(xml)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(exam|экзаменационная_работа).*$', module_name, re.I):
                file_type = 'exam-test'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(xml)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(webinar|вебинар).*$', module_name, re.I):
                file_type = 'webinar'
                src = os.path.join(dir_path, file_name)
                src = src[src.index(request.session.session_key) + len(request.session.session_key):]
                allowed_for_analysis = True
            elif re.fullmatch(r'^(audiofile|аудиофайл).*$', module_name, re.I):
                file_type = 'audio-file'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(flac|midi|amr|ogg|aiff|mp3|wav)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(audiolecture|аудиолекция).*$', module_name, re.I):
                file_type = 'audio-lecture'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(flac|midi|amr|ogg|aiff|mp3|wav)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(videofile|видеофайл).*$', module_name, re.I):
                file_type = 'video-file'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(avi|mp4|mkv)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            elif re.fullmatch(r'^(videolecture|видеолекция).*$', module_name, re.I):
                file_type = 'video-lecture'
                src = 'undefined'
                dp = os.path.join(dir_path, file_name)
                allowed_for_analysis = True
                for fn in os.listdir(dp):
                    fn, fe = os.path.splitext(fn)
                    if re.fullmatch(r'\.(avi|mp4|mkv)', fe, re.I):
                        src = os.path.join(dp, fn + fe)
                if src != 'undefined':
                    src = src[src.index(request.session.session_key) + len(request.session.session_key):]
            else:
                file_type = 'unknown-file'
                src = 'undefined'
                allowed_for_analysis = False
            module.mod_type = file_type
            module.save()
            res.append({
                'section': module.sec_name,
                'name': module.mod_name,
                'id': str(module.mid),
                'type': file_type,
                'src': src,
                'allowed_for_analysis': allowed_for_analysis
            })
        return res

    @staticmethod
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

            context['modules'] = []
            indicators = models.Indicator.objects.filter(show=True)
            for module in modules:
                mod = {}
                file_type = request.POST.get('type-' + module)
                src = os.path.join(tmp_path, module)
                if file_type == 'theory':
                    dst = os.path.join(theory_path, module)
                    mod['indicators'] = indicators.filter(type='auto-indicator')
                elif file_type == 'self-test':
                    dst = os.path.join(self_test_path, module)
                    mod['indicators'] = indicators.filter(name='self_test')
                elif file_type == 'control-test':
                    dst = os.path.join(control_test_path, module)
                    mod['indicators'] = indicators.filter(name='control_and_exam_tests')
                elif file_type == 'exam-test':
                    dst = os.path.join(exam_test_path, module)
                    mod['indicators'] = indicators.filter(name='control_and_exam_tests')
                elif file_type == 'video-file':
                    dst = os.path.join(video_file_path, module)
                    mod['indicators'] = indicators.filter(name='video_file')
                elif file_type == 'video-lecture':
                    dst = os.path.join(video_lecture_path, module)
                    mod['indicators'] = indicators.filter(name='video_lecture')
                elif file_type == 'audio-file':
                    dst = os.path.join(audio_file_path, module)
                    mod['indicators'] = indicators.filter(name='audio_file')
                elif file_type == 'audio-lecture':
                    dst = os.path.join(audio_lecture_path, module)
                    mod['indicators'] = indicators.filter(name='audio_lecture')
                elif file_type == 'webinar':
                    dst = os.path.join(webinar_path, module)
                    mod['indicators'] = indicators.filter(name='webinar')
                elif file_type == 'presentation':
                    dst = os.path.join(presentation_path, module)
                    mod['indicators'] = indicators.filter(name='presentation')
                else:
                    dst = None
                    mod['indicators'] = []
                db_modules = models.Module.objects.filter(
                    uid=request.session.session_key,
                    sdo=request.session['moodle'],
                    cid=request.session['course_id'],
                    mid=module,
                )
                if len(db_modules) > 0:
                    mod_name = db_modules[0].mod_name
                    sec_name = db_modules[0].sec_name
                else:
                    mod_name = module
                    sec_name = module
                mod['name'] = mod_name
                mod['section'] = sec_name
                mod['id'] = module
                context['modules'].append(mod)

                if dst is not None and os.path.exists(src):
                    models.File(
                        uid=request.session.session_key,
                        src=dst
                    ).save()
                    shutil.move(src, dst)

            return render(request, 'indicators.html', context)
        else:
            context['modules'] = Analytics.get_modules(request)
            return render(request, 'modules.html', context)

    @staticmethod
    def theory_analysis_results(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
        }
        if request.method == 'POST':
            media_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
            theory_path = os.path.join(media_path, 'theory')
            files = analyzer.read_files(theory_path, request)
            if len(files) > 0:
                results, names, contents, sections, indicators = Analytics.parallel_analyze(files)
                context = {
                    'theory_modules': list(zip(names, contents, sections, results, indicators))
                }
            objects = models.Results.objects.filter(uid=request.session.session_key, name='theory-analysis')
            if len(objects) == 0:
                models.Results(
                    uid=request.session.session_key,
                    name='theory-analysis',
                    context=json.dumps(context)
                ).save()
            else:
                for object in objects:
                    object.context = json.dumps(context)
                    object.save()
            return redirect('/expert-analysis/')

    @staticmethod
    def parallel_analyze(files):
        file_for_all = files.pop(0)

        start_time = time()

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = [executor.submit(Analytics.parallel_analyze_file, files[i]) for i in range(len(files))]

        results = []
        names = []
        contents = []
        sections = []
        indicators = []
        for future in futures:
            result, name, content, section, indicator = future.result()
            results.append(result)
            names.append(name)
            contents.append(content)
            sections.append(section)
            indicators.append(indicator)

        results = [
            {
                'txt_ch': result['txt_ch'],
                'img_ch': {
                    'img_number': result['img_ch']['img_number'],
                    'pgs_num': result['img_ch']['pgs_num'],
                    'aver_img_in_pg_num': result['img_ch']['aver_img_in_pg_num'],
                    'images': natsorted(result['img_ch']['images'], key=lambda k: k['img_name'].lower())
                },
                'san_ch': result['san_ch']
            } for result in results
        ]

        indicators_for_all = set(files[0]['indicators'])
        for i in range(1, len(files)):
            indicators_for_all.intersection(set(files[i]['indicators']))
        indicators_for_all = list(indicators_for_all)

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            txt_ch = executor.submit(analyzer.text_characteristics_all_files, results, indicators_for_all)
            img_ch = executor.submit(analyzer.img_characteristics_all_files, results, indicators_for_all)
            san_ch = executor.submit(analyzer.search_and_nav_characteristics_all_files, results, indicators_for_all)

        results.insert(0, {
            'txt_ch': txt_ch.result(),
            'img_ch': img_ch.result(),
            'san_ch': san_ch.result()
        })
        names.insert(0, file_for_all['name'])
        contents.insert(0, file_for_all['content'])
        sections.insert(0, file_for_all['section'])
        indicators.insert(0, indicators_for_all)

        finish_time = time()

        print(f'Parallel analyze with futures: {finish_time - start_time}')

        return results, names, contents, sections, indicators

    @staticmethod
    def parallel_analyze_file(file):

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            txt_ch = executor.submit(analyzer.text_characteristics, file)
            img_ch = executor.submit(analyzer.img_characteristics, file)
            san_ch = executor.submit(analyzer.search_and_nav_characteristics, file)

        res = {
            'txt_ch': txt_ch.result(),
            'img_ch': img_ch.result(),
            'san_ch': san_ch.result()
        }

        return res, file['name'], file['content'], file['section'], file['indicators']

    @staticmethod
    def expert_analysis(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
        }

        self_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'self-test')
        self_test_modules = os.listdir(self_test_path)
        questions = []
        ids = []
        names = []
        sections = []
        for module in self_test_modules:
            dir_path = os.path.join(self_test_path, module)
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                if re.fullmatch(r'.*\.html', file_name, re.I):
                    questions.append(Analytics.get_questions(file_path))
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['self_test_modules'] = list(zip(
            ids,
            names,
            sections,
            questions
        ))

        control_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'control-test')
        exam_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'exam-test')
        control_test_modules = os.listdir(control_test_path)
        exam_test_modules = os.listdir(exam_test_path)
        all_questions = []
        ids = []
        names = []
        sections = []
        for module in control_test_modules:
            dir_path = os.path.join(control_test_path, module)
            questions = []
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                if re.fullmatch(r'.*\.xml', file_name, re.I):
                    questions += Analytics.get_control_questions(file_path)
            all_questions.append(questions)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)
        for module in exam_test_modules:
            dir_path = os.path.join(exam_test_path, module)
            questions = []
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                if re.fullmatch(r'.*\.xml', file_name, re.I):
                    questions += Analytics.get_control_questions(file_path)
            all_questions.append(questions)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)
        context['control_and_exam_test_modules'] = list(zip(
            ids,
            names,
            sections,
            all_questions
        ))

        video_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-file')
        video_file_modules = []
        for dir_name in os.listdir(video_file_path):
            video_file_modules.append(os.path.join('/media', request.session.session_key, 'video-file', dir_name))

        names = []
        extensions = []
        src = []
        ids = []
        sections = []
        for module in video_file_modules:
            name = os.path.basename(module)
            has_video = False
            dir_path = os.path.join(video_file_path, name)
            for file_name in os.listdir(dir_path):
                if re.fullmatch(r'.*\.(mkv|avi|mp4)', file_name, re.I):
                    name, extension = os.path.splitext(file_name)
                    extensions.append(extension[1:])
                    src.append(os.path.join(module, file_name))
                    has_video = True
                    break
            if not has_video:
                extensions.append(None)
                src.append(None)
            module = os.path.basename(module)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['video_file_modules'] = list(zip(
            ids,
            names,
            sections,
            extensions,
            src
        ))

        video_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-lecture')
        theory_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'theory')
        video_lecture_modules = []
        for dir_name in os.listdir(video_lecture_path):
            video_lecture_modules.append(os.path.join('/media', request.session.session_key, 'video-lecture', dir_name))

        names = []
        extensions = []
        src = []
        ids = []
        sections = []
        for module in video_lecture_modules:
            name = os.path.basename(module)
            has_video = False
            dir_path = os.path.join(video_lecture_path, name)
            for file_name in os.listdir(dir_path):
                if re.fullmatch(r'.*\.(mkv|avi|mp4)', file_name, re.I):
                    name, extension = os.path.splitext(file_name)
                    # names.append(name.replace(' ', '-'))
                    extensions.append(extension[1:])
                    src.append(os.path.join(module, file_name))
                    has_video = True
                    break
            if not has_video:
                extensions.append(None)
                src.append(None)
            module = os.path.basename(module)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['video_lecture_modules'] = list(zip(
            ids,
            names,
            sections,
            extensions,
            src
        ))
        context['video_lecture_sections'] = []
        for mid in os.listdir(theory_path):
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=mid,
            )
            if len(db_modules) > 0:
                context['video_lecture_sections'].append(
                    db_modules[0].sec_name + (': ' if db_modules[0].sec_name != '' else '') + db_modules[0].mod_name
                )

        audio_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-file')
        audio_file_modules = []
        for dir_name in os.listdir(audio_file_path):
            audio_file_modules.append(os.path.join('/media', request.session.session_key, 'audio-file', dir_name))

        names = []
        extensions = []
        src = []
        ids = []
        sections = []
        for module in audio_file_modules:
            name = os.path.basename(module)
            has_audio = False
            dir_path = os.path.join(audio_file_path, name)
            for file_name in os.listdir(dir_path):
                if re.fullmatch(r'.*\.(flac|midi|amr|ogg|aiff|mp3|wav)', file_name, re.I):
                    name, extension = os.path.splitext(file_name)
                    extensions.append(extension[1:])
                    src.append(os.path.join(module, file_name))
                    has_audio = True
                    break
            if not has_audio:
                extensions.append(None)
                src.append(None)
            module = os.path.basename(module)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['audio_file_modules'] = list(zip(
            ids,
            names,
            sections,
            extensions,
            src
        ))

        audio_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-lecture')
        theory_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'theory')
        audio_lecture_modules = []
        for dir_name in os.listdir(audio_lecture_path):
            audio_lecture_modules.append(os.path.join('/media', request.session.session_key, 'audio-lecture', dir_name))

        names = []
        extensions = []
        src = []
        ids = []
        sections = []
        for module in audio_lecture_modules:
            name = os.path.basename(module)
            has_audio = False
            dir_path = os.path.join(audio_lecture_path, name)
            for file_name in os.listdir(dir_path):
                if re.fullmatch(r'.*\.(flac|midi|amr|ogg|aiff|mp3|wav)', file_name, re.I):
                    name, extension = os.path.splitext(file_name)
                    extensions.append(extension[1:])
                    src.append(os.path.join(module, file_name))
                    has_audio = True
                    break
            if not has_audio:
                extensions.append(None)
                src.append(None)
            module = os.path.basename(module)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['audio_lecture_modules'] = list(zip(
            ids,
            names,
            sections,
            extensions,
            src
        ))
        context['audio_lecture_sections'] = []
        for mid in os.listdir(theory_path):
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=mid,
            )
            if len(db_modules) > 0:
                context['audio_lecture_sections'].append(
                    db_modules[0].sec_name + (': ' if db_modules[0].sec_name != '' else '') + db_modules[0].mod_name
                )

        webinar_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'webinar')
        webinar_modules = os.listdir(webinar_path)
        names = []
        all_videos = []
        all_pictures = []
        all_audios = []
        all_presentations = []
        all_documents = []
        all_tables = []
        all_pdfs = []
        all_others = []
        ids = []
        sections = []
        for module in webinar_modules:
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
            module = os.path.basename(module)
            ids.append(module)
            db_modules = models.Module.objects.filter(
                uid=request.session.session_key,
                sdo=request.session['moodle'],
                cid=request.session['course_id'],
                mid=module,
            )
            if len(db_modules) > 0:
                names.append(db_modules[0].mod_name)
                sections.append(db_modules[0].sec_name)
            else:
                names.append(module)
                sections.append(module)

        context['webinar_modules'] = list(zip(
            ids,
            names,
            sections,
            all_videos,
            all_pictures,
            all_audios,
            all_presentations,
            all_documents,
            all_tables,
            all_pdfs,
            all_others
        ))

        objects = models.Results.objects.filter(uid=request.session.session_key, name='expert-analysis')
        if len(objects) == 0:
            models.Results(
                uid=request.session.session_key,
                name='expert-analysis',
                context=json.dumps(context)
            ).save()
        else:
            for object in objects:
                object.context = json.dumps(context)
                object.save()
        return render(request, 'expert-analysis.html', context)

    @staticmethod
    def get_questions(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            c = f.read()
        bs = bs4.BeautifulSoup(c, 'html.parser')
        questions = bs.find_all('div', 'qheader')
        res = []
        for question in questions:
            p = question.find('p')
            if p is not None and p.string is not None:
                res.append(p.string)
        return res

    @staticmethod
    def get_control_questions(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            c = f.read()
        bs = bs4.BeautifulSoup(c, 'html.parser')
        questions = bs.find_all('questiontext')
        res = []
        for question in questions:
            text = question.find('text')
            if text is not None:
                m = re.match(r'<text><!\[CDATA\[\s*(?P<text>(.|\s)+(?!\]\]>))\s*\]\]></text>', str(text))
                if m is not None:
                    bs = bs4.BeautifulSoup(m.group('text'), 'html.parser')
                    imgs = bs.find_all('img')
                    for img in imgs:
                        try:
                            img['src'] = '/' + os.path.join(os.path.dirname(file_path)[file_path.index('media'):],
                                                            os.path.basename(img['src']))
                        except Exception as e:
                            print(e)
                    res.append(str(bs))
        return res

    @staticmethod
    def results(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
        }
        results = models.Results.objects.filter(uid=request.session.session_key, name='theory-analysis') | \
                  models.Results.objects.filter(uid=request.session.session_key, name='expert-analysis')
        for result in results:
            context.update(json.loads(result.context))

        if request.method == 'POST':
            self_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'self-test')
            self_test_modules = os.listdir(self_test_path)
            for self_test_module in self_test_modules:
                for element in context['self_test_modules']:
                    if element[0] == self_test_module:
                        element.append({
                            'difficulty_factor': request.POST.getlist(
                                self_test_module + '-self-test-difficulty-factor'),
                            'completion_rate': request.POST.getlist(self_test_module + '-self-test-completion-rate'),
                            'has_answers': request.POST.getlist(self_test_module + '-self-test-has-answers'),
                            'has_links': request.POST.getlist(self_test_module + '-self-test-has-links'),
                            'special_opinion': request.POST.get(self_test_module + '-self-test-special-opinion')
                        })
            control_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'control-test')
            exam_test_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'exam-test')
            control_test_modules = os.listdir(control_test_path)
            exam_test_modules = os.listdir(exam_test_path)
            for control_and_exam_test_module in control_test_modules + exam_test_modules:
                for element in context['control_and_exam_test_modules']:
                    if element[0] == control_and_exam_test_module:
                        element.append({
                            'volume': request.POST.get(control_and_exam_test_module + '-control-and-exam-test-volume'),
                            'has_generation': request.POST.get(
                                control_and_exam_test_module + '-control-and-exam-test-has-generation'),
                            'testing_technology': request.POST.getlist(
                                control_and_exam_test_module + '-control-and-exam-test-testing-technology'),
                            'has_codifier': request.POST.get(
                                control_and_exam_test_module + '-control-and-exam-test-has-codifier'),
                            'course_section': request.POST.getlist(
                                control_and_exam_test_module + '-control-and-exam-test-course-section'),
                            'researches': request.POST.getlist(
                                control_and_exam_test_module + '-control-and-exam-test-researches'),
                            'special_opinion': request.POST.get(
                                control_and_exam_test_module + '-control-and-exam-test-special-opinion')
                        })
            video_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-file')
            video_file_modules = os.listdir(video_file_path)
            for video_file_module in video_file_modules:
                for element in context['video_file_modules']:
                    if element[0] == video_file_module:
                        element.append({
                            'target': request.POST.getlist(video_file_module + '-video-file-target'),
                            'duration': request.POST.getlist(video_file_module + '-video-file-duration'),
                            'has_scenario': request.POST.get(video_file_module + '-video-file-has-scenario'),
                            'complexity': request.POST.getlist(video_file_module + '-video-file-complexity'),
                            'has_ticker': request.POST.get(video_file_module + '-video-file-has-ticker'),
                            'recording_quality': request.POST.getlist(
                                video_file_module + '-video-file-recording-quality')
                        })
            video_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'video-lecture')
            video_lecture_modules = os.listdir(video_lecture_path)
            for video_lecture_module in video_lecture_modules:
                for element in context['video_lecture_modules']:
                    if element[0] == video_lecture_module:
                        element.append({
                            'target': request.POST.getlist(video_lecture_module + '-video-lecture-target'),
                            'duration': request.POST.getlist(video_lecture_module + '-video-lecture-duration'),
                            'has_scenario': request.POST.get(video_lecture_module + '-video-lecture-has-scenario'),
                            'complexity': request.POST.getlist(video_lecture_module + '-video-lecture-complexity'),
                            'has_ticker': request.POST.get(video_lecture_module + '-video-lecture-has-ticker'),
                            'recording_quality': request.POST.getlist(
                                video_lecture_module + '-video-file-recording-quality'),
                            'coverage': request.POST.getlist(video_lecture_module + '-video-lecture-coverage'),
                            'distribution': request.POST.getlist(video_lecture_module + '-video-lecture-distribution'),
                            'volume': request.POST.get(video_lecture_module + '-video-lecture-volume'),
                            'has_navigation': request.POST.get(video_lecture_module + '-video-lecture-has-navigation')
                        })
            audio_file_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-file')
            audio_file_modules = os.listdir(audio_file_path)
            for audio_file_module in audio_file_modules:
                for element in context['audio_file_modules']:
                    if element[0] == audio_file_module:
                        element.append({
                            'target': request.POST.getlist(audio_file_module + '-audio-file-target'),
                            'target_own': request.POST.get(audio_file_module + '-audio-file-target-own'),
                            'duration': request.POST.get(audio_file_module + '-audio-file-duration'),
                            'quality': request.POST.getlist(audio_file_module + '-audio-file-quality'),
                            'format': request.POST.get(audio_file_module + '-audio-file-format')
                        })
            audio_lecture_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'audio-lecture')
            audio_lecture_modules = os.listdir(audio_lecture_path)
            for audio_lecture_module in audio_lecture_modules:
                for element in context['audio_lecture_modules']:
                    if element[0] == audio_lecture_module:
                        element.append({
                            'target': request.POST.getlist(audio_lecture_module + '-audio-lecture-target'),
                            'target_own': request.POST.get(audio_lecture_module + '-audio-lecture-target-own'),
                            'duration': request.POST.get(audio_lecture_module + '-audio-lecture-duration'),
                            'quality': request.POST.getlist(audio_lecture_module + '-audio-lecture-quality'),
                            'format': request.POST.get(audio_lecture_module + '-audio-lecture-format'),
                            'coverage': request.POST.get(audio_lecture_module + '-audio-lecture-coverage'),
                            'distribution': request.POST.getlist(audio_lecture_module + '-audio-lecture-distribution'),
                            'volume': request.POST.get(audio_lecture_module + '-audio-lecture-volume'),
                            'has_navigation': request.POST.get(audio_lecture_module + '-audio-lecture-has-navigation')
                        })
            webinar_path = os.path.join(settings.MEDIA_ROOT, request.session.session_key, 'webinar')
            webinar_modules = os.listdir(webinar_path)
            for webinar_module in webinar_modules:
                for element in context['webinar_modules']:
                    if element[0] == webinar_module:
                        element.append({
                            'type': request.POST.getlist(webinar_module + '-webinar-type'),
                            'duration': request.POST.get(webinar_module + '-webinar-duration'),
                            'has_scenario': request.POST.get(webinar_module + '-webinar-has-scenario'),
                            'scenario_has_introduction': request.POST.get(
                                webinar_module + '-webinar-scenario-has-introduction'),
                            'scenario_has_presentation': request.POST.get(
                                webinar_module + '-webinar-scenario-has-presentation'),
                            'scenario_has_add_materials': request.POST.get(
                                webinar_module + '-webinar-scenario-has-add-materials'),
                            'scenario_has_questions_answers': request.POST.get(
                                webinar_module + '-webinar-scenario-has-questions-answers'),
                            'scenario_has_quiz': request.POST.get(webinar_module + '-webinar-scenario-has-quiz'),
                            'scenario_has_summarizing': request.POST.get(
                                webinar_module + '-webinar-scenario-has-summarizing'),
                            'has_presentation': request.POST.get(webinar_module + '-webinar-has-presentation'),
                            'has_presentation_red_color': request.POST.get(
                                webinar_module + '-webinar-has-presentation-red-color'),
                            'has_presentation_text': request.POST.get(
                                webinar_module + '-webinar-has-presentation-text'),
                            'has_presentation_illustrations': request.POST.get(
                                webinar_module + '-webinar-has-presentation-illustrations'),
                            'has_presentation_numeration': request.POST.get(
                                webinar_module + '-webinar-has-presentation-numeration'),
                            'has_additional_materials': request.POST.get(
                                webinar_module + '-webinar-has-additional-materials'),
                            'has_additional_materials_video': request.POST.get(
                                webinar_module + '-webinar-has-additional-materials-video'),
                            'has_additional_materials_help_files': request.POST.get(
                                webinar_module + '-webinar-has-additional-materials-help-files'),
                            'has_questions': request.POST.get(webinar_module + '-webinar-has-questions'),
                            'has_questions_input_control': request.POST.get(
                                webinar_module + '-webinar-has-questions-input-control'),
                            'has_questions_interim_issues': request.POST.get(
                                webinar_module + '-webinar-has-questions-interim-issues'),
                            'has_questions_test_questions': request.POST.get(
                                webinar_module + '-webinar-has-questions-test-questions'),
                        })
            context['tutorial'] = {
                'tutorial_amount_correspond_intensity': request.POST.get('tutorial-amount-correspond-intensity'),
                'tutorial_content_correspond_goals': request.POST.get('tutorial-content-correspond-goals'),
                'tutorial_content_correspond_tasks': request.POST.get('tutorial-content-correspond-tasks'),
                'tutorial_ensures_continuity_knowledge': request.POST.get('tutorial-ensures-continuity-knowledge'),
                'tutorial_content_correspond_competencies': request.POST.get(
                    'tutorial-content-correspond-competencies'),
                'tutorial_content_correspond_knowledge': request.POST.get('tutorial-content-correspond-knowledge'),
                'tutorial_chapter_titles_correspond_section_names': request.POST.get(
                    'tutorial-chapter-titles-correspond-section-names'),
                'tutorial_volume_correspond_hours': request.POST.get('tutorial-volume-correspond-hours'),
                'tutorial_in_references': request.POST.get('tutorial-in-references'),
            }
            context['educational_methodical_manual'] = {
                'educational_methodical_manual_content_correspond_goals': request.POST.get(
                    'educational-methodical-manual-content-correspond-goals'),
                'educational_methodical_manual_content_correspond_tasks': request.POST.get(
                    'educational-methodical-manual-content-correspond-tasks'),
                'educational_methodical_manual_content_correspond_competencies': request.POST.get(
                    'educational-methodical-manual-content-correspond-competencies'),
                'educational_methodical_manual_content_correspond_knowledge': request.POST.get(
                    'educational-methodical-manual-content-correspond-knowledge'),
                'educational_methodical_manual_in_references': request.POST.get(
                    'educational-methodical-manual-in-references'),
                'educational_methodical_manual_task_correspond_hours': request.POST.get(
                    'educational-methodical-manual-task-correspond-hours'),
                'educational_methodical_manual_topics_correspond_rpd': request.POST.get(
                    'educational-methodical-manual-topics-correspond-rpd'),
            }
            context['guidelines'] = {
                'guidelines_content_correspond_goals': request.POST.get('guidelines-content-correspond-goals'),
                'guidelines_content_correspond_tasks': request.POST.get('guidelines-content-correspond-tasks'),
                'guidelines_content_correspond_competencies': request.POST.get(
                    'guidelines-content-correspond-competencies'),
                'guidelines_content_correspond_knowledge': request.POST.get('guidelines-content-correspond-knowledge'),
                'guidelines_task_correspond_hours': request.POST.get('guidelines-task-correspond-hours'),
                'guidelines_in_references': request.POST.get('guidelines-in-references'),
                'guidelines_topics_correspond_rpd': request.POST.get('guidelines-topics-correspond-rpd'),
                'guidelines_po_correspond_mto': request.POST.get('guidelines-po-correspond-mto'),
            }
            context['test_bank'] = {
                'test_bank_checked_competencies_formulate': request.POST.get(
                    'test-bank-checked-competencies-formulate'),
                'test_bank_correspond_rpd': request.POST.get('test-bank-correspond-rpd'),
                'test_bank_correspond_sections': request.POST.get('test-bank-correspond-sections'),
            }
            objects = models.Results.objects.filter(
                uid=request.session.session_key,
                name='course-analysis'
            )
            if len(objects) == 0:
                models.Results(
                    uid=request.session.session_key,
                    name='course-analysis',
                    context=json.dumps(context)
                ).save()
            else:
                for object in objects:
                    object.context = json.dumps(context)
                    object.save()
        return render(request, 'results.html', context)

    @staticmethod
    def course_rating(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
        }
        uid = request.POST.get('uid')
        results = models.Results.objects.filter(uid=uid if uid is not None else request.session.session_key,
                                                name='course-analysis')
        for result in results:
            context.update(json.loads(result.context))

        course_rating = 0
        if request.method == 'POST':
            values = request.POST.getlist('values')
            coefficients = request.POST.getlist('coefficients')
            for i in range(len(values)):
                course_rating += float(values[i]) * float(coefficients[i])
            course_rating /= len(values)
            context['coefficients'] = coefficients

        context['course_rating'] = round(course_rating, 2)

        models.Course(
            uid=request.session.session_key,
            identifier=request.session['course_id'],
            moodle=request.session['moodle'],
            rating=context['course_rating'],
            context=json.dumps(context),
            datetime=datetime.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        ).save()

        return render(request, 'results.html', context)


class Ajax:

    @staticmethod
    def move_files_to_tmp(request):
        files = models.File.objects.all()
        files_names = request.POST.getlist('checked[]')
        media_root = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
        tmp_root = os.path.join(media_root, 'tmp')
        move_from_tmp = False
        for file in files:
            src = file.src
            file_name = os.path.basename(src)
            if file.uid == request.session.session_key and file_name in files_names:
                dst = os.path.join(tmp_root, file_name)
                shutil.move(src, dst)
                file.delete()
                move_from_tmp = True
        if move_from_tmp:
            for file_name in os.listdir(media_root):
                file_path = os.path.join(media_root, file_name)
                if os.path.isdir(file_path) and file_name != 'tmp':
                    shutil.rmtree(file_path)
            for file_name in os.listdir(tmp_root):
                src = os.path.join(tmp_root, file_name)
                dst = os.path.join(media_root, file_name)
                shutil.move(src, dst)
            shutil.rmtree(tmp_root)
        return JsonResponse({'res': True})


class Admin:

    @staticmethod
    def admin_settings(request):
        context = {
            'username': auth.get_user(request).username,
            'scales': models.Scale.objects.all(),
            'indicators': models.Indicator.objects.all()
        }
        return render(request, 'admin-settings.html', context)

    @staticmethod
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

    @staticmethod
    def check_scale_name(request):
        scale_name = request.POST.get('scale-name')
        scales = models.Scale.objects.all()
        for scale in scales:
            if scale.name == scale_name:
                return JsonResponse({'res': True})
        return JsonResponse({'res': False})

    @staticmethod
    def get_scale(request):
        scale_name = request.POST.get('scale-name')
        scale = models.Scale.objects.get(name=scale_name)
        return JsonResponse(json.loads(str(scale)))

    @staticmethod
    def delete_scale(request):
        scale_name = request.POST.get('scale-name')
        scale = models.Scale.objects.get(name=scale_name)
        scale.delete()
        return JsonResponse({'res': True})

    @staticmethod
    def add_indicator(request):
        user = auth.get_user(request)
        context = {'username': user.username}
        if request.method == 'POST':
            indicator_name = request.POST.get('indicator-name')
            indicator_type = request.POST.get('indicator-type')
            indicator_show = request.POST.get('indicator-show')
            indicator_description = request.POST.get('indicator-description')
            indicator = models.Indicator(
                name=indicator_name,
                type=indicator_type,
                show=True if indicator_show == 'on' else False,
                description=indicator_description
            )
            indicator.save()
        return render(request, 'add-indicator.html', context)

    @staticmethod
    def delete_indicator(request):
        indicator_name = request.POST.get('indicator-name')
        indicator = models.Indicator.objects.get(name=indicator_name)
        indicator.delete()
        return JsonResponse({'res': True})

    @staticmethod
    def hide_indicator(request):
        indicator_name = request.POST.get('indicator-name')
        indicator = models.Indicator.objects.get(name=indicator_name)
        indicator.show = False
        indicator.save()
        return JsonResponse({'res': True})

    @staticmethod
    def show_indicator(request):
        indicator_name = request.POST.get('indicator-name')
        indicator = models.Indicator.objects.get(name=indicator_name)
        indicator.show = True
        indicator.save()
        return JsonResponse({'res': True})

    @staticmethod
    def check_indicator_name(request):
        indicator_name = request.POST.get('indicator-name')
        indicators = models.Indicator.objects.all()
        for indicator in indicators:
            if indicator.name == indicator_name:
                return JsonResponse({'res': True})
        return JsonResponse({'res': False})


class History:

    @staticmethod
    def history(request):
        user = auth.get_user(request)
        context = {
            'username': user.username if not user.is_anonymous else 'Anonymous',
            'is_superuser': user.is_superuser,
            'is_anonymous': user.is_anonymous,
            'courses': models.Course.objects.all()
        }
        return render(request, 'history.html', context)

    @staticmethod
    def show_course_result(request):
        course_id = request.GET.get('course_id')
        moodle = request.GET.get('moodle')
        dt = datetime.strptime(request.GET.get('datetime'), '%d.%m.%Y %H:%M:%S')
        uid = request.GET.get('uid')
        courses = models.Course.objects.filter(
            identifier=course_id,
            moodle=moodle,
            uid=uid
        )
        context = {
            'uid': uid
        }
        for course in courses:
            c_dt = course.datetime.astimezone(pytz.timezone(settings.TIME_ZONE))
            if c_dt.day == dt.day and c_dt.month == dt.month and c_dt.year == dt.year and \
                    c_dt.hour == dt.hour and c_dt.minute == dt.minute and c_dt.second == dt.second:
                context.update(json.loads(course.context))
        return render(request, 'results.html', context)

    @staticmethod
    def clear_history(request):
        models.Course.objects.all().delete()
        return redirect('/history/')


class Log:

    @staticmethod
    def show_log(request):
        context = {}
        file_path = '/var/www/cqa.fdo.tusur.ru/cqa.log'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file_object:
                file_content = file_object.read()
                context['content'] = file_content.split('\n')
        return render(request, 'log.html', context)