from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from YHMI_results.models import YhmiEnrichment, FilterResult, YhmiEnrichmentTf, YhmiEnrichmentTempTable
from django.views.decorators.csrf import csrf_exempt

import json
import scipy.stats
from pprint import pprint

@csrf_exempt
def enrichJSON(request):
	'''
	http://140.116.215.238/api/enrich
	request.POST

	argument:
	[necessary]
	InputGene: list with json
	corrected: 1.Bonferroni, 2.FDR
	cutoff: correction standard

	[option]
	setting_data: json ['fs{id}_(pro|cds)_(en/de)_value', ...]
	'''
	if ('InputGene' not in request.POST) or ('corrected' not in request.POST) or ('cutoff' not in request.POST):
		return HttpResponseBadRequest

	geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	if geneset:
		enrich_db = YhmiEnrichmentTempTable()
		if 'setting_data' in request.POST:
			enrich_db.updateTable(request.POST['setting_data'])

		data = enrich_db.getData()
		# data = YhmiEnrichment.objects.all()
		data_tf = YhmiEnrichmentTf.objects.all()
		S = len(geneset)
		enrich_value = []
		enrich_value_tf = []

		for i in data:
			gene = [set(i['pro_en'].split(',')), set(i['pro_de'].split(',')), set(i['cds_en'].split(',')), set(i['cds_de'].split(','))]
			
			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)
				if request.POST['corrected'] == '1':
					enrich_value.append({
						'feature':i['feature'],
						'enrich_type':t, 
						'intersectOfgene':[T, S, G, 6572],
						'pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))
					})
				else:
					enrich_value.append([i['feature'], t, (T, S, G)])
		

		for i in data_tf:
			g = set(i.pro.split(','))
			# gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]
			T = len(g & geneset)
			G = len(g)
			if request.POST['corrected'] == '1':
				enrich_value_tf.append({
					'feature':i.feature,
					'enrich_type':4, 
					'intersectOfgene':[T, S, G, 6572],
					'pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))
				})
			else:
				enrich_value_tf.append([i.feature, 4, (T, S, G)])
		
		enrich_value.extend(enrich_value_tf)
		if request.POST['corrected'] == '1':
			enrich_value = [e for e in enrich_value if e['pvalue']]
		elif request.POST['corrected'] == '2':
			enrich_value = [{
				'feature':e[0],
				'enrich_type':e[1], 
				'intersectOfgene':e[2],
				'pvalue':e[3]
			} for e in FDR_corrected(enrich_value, cutoff=float(request.POST['cutoff']), length=len(enrich_value))]

	enrich_db.dropTable()
	return JsonResponse(enrich_value,safe=False)

def showEnrich(request):
	if request.POST['composition']:
		yhmi_filter = list(filter(None, json.loads(request.POST['InputGene'])))
		geneset = set(FilterResult.filterGene(yhmi_filter, request.POST['composition']))
	else:
		geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	

	if geneset:
		enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
		# data = YhmiEnrichment.objects.all()
		data_tf = YhmiEnrichmentTf.objects.all()
		# print("="*50)
		data = enrich_db.getData()
		# print("="*50)

		S = len(geneset)
		enrich_value = []
		enrich_value_tf = []

		for i in data:
			gene = [set(i['pro_en'].split(',')), set(i['pro_de'].split(',')), set(i['cds_en'].split(',')), set(i['cds_de'].split(','))]
			# gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cds_en.split(',')), set(i.cds_de.split(','))]
			
			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)
				if request.POST['corrected'] == '1':
					enrich_value.append([i['feature'], t, (T, S, G,), Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))])
				else:
					enrich_value.append([i['feature'], t, (T, S, G)])
		

		for i in data_tf:
			g = set(i.pro.split(','))
			# gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]
			T = len(g & geneset)
			G = len(g)
			if request.POST['corrected'] == '1':
				enrich_value_tf.append([i.feature, 4, (T, S, G,), Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))])
			else:
				enrich_value_tf.append([i.feature, 4, (T, S, G)])
		
		
		enrich_value.extend(enrich_value_tf)
		if request.POST['corrected'] == '2':
			enrich_value = FDR_corrected(enrich_value, cutoff=float(request.POST['cutoff']))

	else:
		enrich_value = []
		
	render_dict = {
		'inputGene':sorted(list(geneset)),
		'enrich_value': enrich_value,
		'corrected': request.POST['corrected'],
		'cutoff': request.POST['cutoff'],
	}
	return render(request, 'enrich_template.html', render_dict)


def customSetting(request, method):
	if 'tableID' in request.POST:
		enrich_db = YhmiEnrichmentTempTable(request.POST['tableID'])
	else:
		enrich_db = YhmiEnrichmentTempTable()

	if method == 'init':
		return JsonResponse({'tableID':enrich_db.tableID})

	elif method == 'update':
		enrich_db.updateTable(request.POST['setting_data'])

	elif method == 'drop':
		enrich_db.dropTable()
	elif method == 'drop':
		enrich_db.defaultTable()

	return HttpResponse(status=200)


def FDR_corrected(temp_enrich, cutoff, length=338):
	F = 6572
	for i,data in enumerate(temp_enrich):
		T, S, G = data[2]

		S_T = S-T
		G_T = G-T
		F_G_S_T = F-G-S+T
		
		if F_G_S_T <= 0:
			temp_enrich[i].append((Decimal('Infinity'),))
		else:
			temp_enrich[i].append([scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1],])

	temp_enrich.sort(key=lambda x:x[3][0])
	pass_flag = True

	for i,t in reversed(list(enumerate(temp_enrich, 1))):
		temp_enrich[i-1][3][0] = t[3][0] = t[3][0]*length/i
		if pass_flag and (t[3][0] < 10**(-cutoff)):
			pass_range = i
			pass_flag = False		
	
	return temp_enrich[:pass_range]


def Hypergeometric_pvalue(T, S, G, F=6572, cutoff=2):
	'''calculate every pvalue of each feature'''
	# T = 'intersects'         #交集數         1
	# S = 'input_gene'         #輸入 genes數   18
	# G = 'feature_gene'       #genes 樣本數   1117
	# F = 'total_feature_gene'         #總 genes數     6572

	S_T = S-T
	G_T = G-T
	F_G_S_T = F-G-S+T
	
	if F_G_S_T <= 0:
		return ""
	
	pvalue_over = scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1]*338
	pvalue_under = scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'less')[1]*338

	if pvalue_over < (10**(-cutoff)):
		return pvalue_over,0
	elif pvalue_under < (10**(-cutoff)):
		return pvalue_under,1
	else:
		return ""


