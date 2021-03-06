"""yna_filter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from .views import search_page, home_page
from YHMI_results.views import showEnrich, customSetting, showIntersect, userSpecific, result_download
from YHMI_api.views import enrich_api
from YHMI_web_info.views import help_page, contact_page, supplementary_download

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home_page),
    url(r'^home/$', home_page),
    url(r'^tool/$', search_page),

    url(r'^result$', showEnrich),
    url(r'^result/download$', result_download),
    url(r'^result/specific$', userSpecific),
    url(r'^result/specific/histonegene$', userSpecific, {'HistoneGene':True}),

    url(r'^intersect$', showIntersect),
    url(r'^intersect/download$', showIntersect),

    url(r'^setting/(init|update|drop|default)$', customSetting),

    url(r'^api/enrich$', enrich_api),

    url(r'^help$', help_page),
    url(r'^contact$', contact_page),
    url(r'supplementary', supplementary_download)
]