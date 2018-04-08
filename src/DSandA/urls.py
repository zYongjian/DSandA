"""DSandA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from homework import views as hview

urlpatterns = [
    url(r'^index', hview.index),
    url(r'^register/', hview.register),
    url(r'^confirm/', hview.confirm),
    url(r'^profile/', hview.profile),
    url(r'^login/', hview.login),
    url(r'^logout/', hview.logout),
    url(r'^upload/', hview.upload),
    url(r'^download/', hview.download),
    url(r'^a_register/', hview.a_register),
    url(r'^a_login/', hview.a_login),
    url(r'^a_profile/', hview.a_profile),
    url(r'^a_homeworks/', hview.a_homeworks),
    url(r'^a_score/', hview.a_score),
    url(r'^a_logout/', hview.a_logout),
    url(r'^a_students/', hview.a_students),
    url(r'^a_student/', hview.a_student),
    url(r'^a_zip/', hview.a_zip),
    url(r'^a_download/', hview.a_download),
    url(r'^a_get_excel/', hview.get_excel),
    path('admin/', admin.site.urls),
    url(r'^', hview.index),
]
