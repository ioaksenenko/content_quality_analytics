"""content_quality_analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('uploaded-files/', views.uploaded_files, name='uploaded-files'),
    path('unpack-files/', views.unpack_files, name='unpack-files'),
    path('delete-uploaded-file/', views.delete_uploaded_file, name='delete-uploaded-file'),
    path('restore-deleted-uploaded-files/', views.restore_deleted_uploaded_files, name='restore-deleted-uploaded-files'),
    path('indicators/', views.indicators, name='indicators'),
    path('moodle/', views.moodle, name='moodle'),
    path('move-files-to-tmp/', views.move_files_to_tmp, name='move-files-to-tmp'),

    path('load/', views.load, name='load'),
    path('unload/', views.unload, name='unload'),

    path('files/', views.files, name='files'),
    path('file-action/', views.file_action, name='file-action'),
    path('join/', views.join, name='join'),
    path('remove-selected-files/', views.remove_selected_files, name='remove-selected-files'),
    path('del-last-module/', views.del_last_module, name='del-last-module'),
    path('return-deleted-files/', views.return_deleted_files, name='return-deleted-files'),

    path('modules/', views.modules, name='modules'),
    path('theory-analysis-results/', views.theory_analysis_results, name='theory-analysis-results'),

    path('self-test-analysis/', views.self_test_analysis, name='self-test-analysis'),
    path('self-test-analysis-results/', views.self_test_analysis_results, name='self-test-analysis-results'),

    path('control-test-analysis/', views.control_test_analysis, name='control-test-analysis'),
    path('control-test-analysis-results/', views.control_test_analysis_results, name='control-test-analysis-results'),

    path('video-file-analysis/', views.video_file_analysis, name='video-file-analysis'),
    path('video-lecture-analysis/', views.video_lecture_analysis, name='video-lecture-analysis'),
    path('audio-file-analysis/', views.audio_file_analysis, name='audio-file-analysis'),
    path('audio-lecture-analysis/', views.audio_lecture_analysis, name='audio-lecture-analysis'),
    path('webinar-analysis/', views.webinar_analysis, name='webinar-analysis'),
    path('complete-analysis/', views.complete_analysis, name='complete-analysis'),

    path('auth/', include('userauth.urls')),
    path('admin-settings/', views.admin_settings, name='admin-settings'),
    path('add-scale/', views.add_scale, name='add-scale'),
    path('check-scale-name/', views.check_scale_name, name='check-scale-name'),
    path('get-scale/', views.get_scale, name='get-scale'),
    path('delete-scale/', views.delete_scale, name='delete-scale'),

    path('add-indicator/', views.add_indicator, name='add-indicator'),
    path('delete-indicator/', views.delete_indicator, name='delete-indicator'),
    path('hide-indicator/', views.hide_indicator, name='hide-indicator'),
    path('show-indicator/', views.show_indicator, name='show-indicator'),
    path('check-indicator-name/', views.check_indicator_name, name='check-indicator-name'),

    path('join-elements/', views.join_elements, name='join-elements'),
    path('split-elements/', views.split_elements, name='split-elements'),
    path('expert-analysis/', views.expert_analysis, name='expert-analysis'),
    path('results/', views.results, name='results'),
    path('course-rating/', views.course_rating, name='course-rating'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
