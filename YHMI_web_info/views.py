from django.shortcuts import render
from .models import ConstInfoContact

# Create your views here.
def help_page(request):
	return render(request, 'help.html')

def contact_page(request):
    contact = ConstInfoContact.objects.all()
    return render(request, 'contact.html', locals())
