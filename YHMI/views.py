from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

# @ensure_csrf_cookie
@csrf_exempt
def HomePage(request):

	
	######## get Papers and Features #########
	db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'yhmi_database')
	cursor = db.cursor()
	SqlCmd = "SELECT `ID`,`Paper`,`Feature` FROM `yhmi_comparison_feature`"
	cursor.execute(SqlCmd)

	filter_item = {}
	for ID, Paper, Feature in cursor.fetchall():
		if Paper in filter_item:
			filter_item[Paper].append((ID,Feature))
		else:
			filter_item[Paper] = [(ID,Feature)]
	######## ./get Papers and Features ########

	# print(filter_item)
	render_dict = {
		'filter_data':filter_item,
	}
	return render(request, 'home.html', render_dict)