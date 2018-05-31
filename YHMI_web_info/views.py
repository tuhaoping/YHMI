from django.shortcuts import render
from .models import ConstInfoContact
from django.http import HttpResponse
from django.conf import settings
import os
import urllib

# Create your views here.
def help_page(request):
	return render(request, 'help.html')

def contact_page(request):
    contact = ConstInfoContact.objects.all()
    return render(request, 'contact.html', locals())

def supplementary_download(request):

	# def download_file():
		# with open(settings.BASE_DIR, 'rb') as f:
			# yield f.read()
	path = os.path.join("E:/Github/YHMI/static/media/Supplementary-Table-1.xlsx")
	# path = os.path.join(settings.BASE_DIR, settings.MEDIA_URL+'Supplementary-Table-1.xlsx')
	with open(path, 'rb') as f:
		data = f.read()

	response = HttpResponse(data , content_type='application/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment;filename=Supplementary-Table-1.xlsx'
	return response

