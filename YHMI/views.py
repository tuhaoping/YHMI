from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

# @ensure_csrf_cookie
@csrf_exempt
def HomePage(request):

	
	######## get Papers and Features #########
	db = MySQLdb.connect('localhost', 'haoping', 'a012345', 'yhmi_database')
	cursor = db.cursor()
	SqlCmd = "SELECT `ID`,`Feature`,`Feature_Criteria`,`MainClass`,`SubClass` FROM `const_comparison_feature` WHERE `Valid`"
	cursor.execute(SqlCmd)

	filter_item = {}
	for ID, Feature, Criteria, mC, sC in cursor.fetchall():
		if mC in filter_item:
			if mC == 'TF':
				pass
				# filter_item[mC].append((ID,Feature,Criteria))
			elif sC in filter_item[mC]:
				filter_item[mC][sC].append((ID,Feature,Criteria))
			else:
				filter_item[mC][sC] = [(ID,Feature,Criteria)]
		else:
			if mC == 'TF':
				pass
				# filter_item[mC] = [(ID,Feature,Criteria)]
			else:
				filter_item[mC] = {sC:[(ID,Feature,Criteria)]}
	######## ./get Papers and Features ########

	# print(filter_item)
	render_dict = {
		'filter_data':filter_item,
	}
	return render(request, 'home.html', render_dict)