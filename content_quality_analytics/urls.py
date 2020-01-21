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

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.Analytics.index, name='index'),
    path('moodle/', views.Analytics.moodle, name='moodle'),
    path('modules/', views.Analytics.modules, name='modules'),
    path('indicators/', views.Analytics.indicators, name='indicators'),
    path('theory-analysis-results/', views.Analytics.theory_analysis_results, name='theory-analysis-results'),
    path('expert-analysis/', views.Analytics.expert_analysis, name='expert-analysis'),
    path('results/', views.Analytics.results, name='results'),
    path('course-rating/', views.Analytics.course_rating, name='course-rating'),

    path('move-files-to-tmp/', views.Ajax.move_files_to_tmp, name='move-files-to-tmp'),

    path('auth/', include('userauth.urls')),
    path('admin-settings/', views.Admin.admin_settings, name='admin-settings'),
    path('add-scale/', views.Admin.add_scale, name='add-scale'),
    path('check-scale-id/', views.Admin.check_scale_id, name='check-scale-id'),
    path('get-scale/', views.Admin.get_scale, name='get-scale'),
    path('delete-scale/', views.Admin.delete_scale, name='delete-scale'),
    path('add-indicator/', views.Admin.add_indicator, name='add-indicator'),
    path('delete-indicator/', views.Admin.delete_indicator, name='delete-indicator'),
    path('hide-indicator/', views.Admin.hide_indicator, name='hide-indicator'),
    path('show-indicator/', views.Admin.show_indicator, name='show-indicator'),
    path('check-indicator-id/', views.Admin.check_indicator_id, name='check-indicator-id'),

    path('history/', views.History.history, name='history'),
    path('show-course-result/', views.History.show_course_result, name='show-course-result'),
    path('clear-history/', views.History.clear_history, name='clear-history'),

    path('log/', views.Log.show_log, name='log'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
