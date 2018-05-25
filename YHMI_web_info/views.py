from django.shortcuts import render

# Create your views here.
def help_page(request):
	return render(request, 'help.html')