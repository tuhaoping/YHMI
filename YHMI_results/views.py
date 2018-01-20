from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from YHMI_results.models import YhmiEnrichment, FilterResult
from django.views.decorators.csrf import csrf_exempt

import json
import scipy.stats
from pprint import pprint

@csrf_exempt
def enrichJSON(request):
	'''
	request.POST

	argument:
	InputGene: list with json
	corrected: 1.Bonferroni, 2.FDR
	cutoff: correction standard
	'''
	if ('InputGene' not in request.POST) or ('corrected' not in request.POST) or ('cutoff' not in request.POST):
		return HttpResponseBadRequest

	geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	if geneset:
		data = YhmiEnrichment.objects.all()
		S = len(geneset)
		enrich_value = []

		for i in data:
			gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]

			for g,t in zip(gene, [0, 1, 2, 3]):
				T = len(g & geneset)
				G = len(g)

				if request.POST['corrected'] == '1':
					enrich_value.append({
						'feature':i.feature,
						'enrich_type':t, 
						'intersectOfgene':[T, S, G, 6572],
						'pvalue':Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))
					})
					enrich_value = [e for e in enrich_value if e['pvalue']]
				else:
					enrich_value.append([i.feature, t, (T, S, G)])

			if request.POST['corrected'] == '2':
				enrich_value = FDR_corrected(enrich_value, cutoff=float(request.POST['cutoff']), length=len(enrich_value))

	print(enrich_value)

	return JsonResponse(enrich_value,safe=False)

def showEnrich(request):
	if request.POST['composition']:
		yhmi_filter = list(filter(None, json.loads(request.POST['InputGene'])))
		geneset = set(FilterResult.filterGene(yhmi_filter, request.POST['composition']))
	else:
		geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	

	if geneset:
		data = YhmiEnrichment.objects.all()

		S = len(geneset)
		enrich_value = []

		for i in data:
			# gene = [set(i.pro_en.split(',')), set(), set(i.cod_en.split(',')), set()]
			gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]
			

			if request.POST['corrected'] == '1':
				for g,t in zip(gene, [0, 1, 2, 3]):
					T = len(g & geneset)
					G = len(g)
					enrich_value.append([i.feature, t, (T, S, G,), Hypergeometric_pvalue(T, S, G, cutoff=float(request.POST['cutoff']))])

			else:
				for g,t in zip(gene, [0, 1, 2, 3]):
					T = len(g & geneset)
					G = len(g)
					enrich_value.append([i.feature, t, (T, S, G)])
		
		if request.POST['corrected'] == '2':
			enrich_value = FDR_corrected(enrich_value, cutoff=float(request.POST['cutoff']), length=len(enrich_value))

	else:
		enrich_value = []
		
	render_dict = {
		'enrich_value': enrich_value,
		'corrected': request.POST['corrected'],
		'cutoff': request.POST['cutoff'],
	}
	return render(request, 'enrich_template.html', render_dict)


def FDR_corrected(temp_enrich, cutoff, length):
	F = 6572
	# pprint(temp_enrich)
	for i,data in enumerate(temp_enrich):
		T, S, G = data[2]

		S_T = S-T
		G_T = G-T
		F_G_S_T = F-G-S+T
		
		if F_G_S_T <= 0:
			temp_enrich[i].append((Decimal('Infinity'),))
		else:
			temp_enrich[i].append((scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1],))

	temp_enrich.sort(key=lambda x:x[3][0])
	# pprint(temp_enrich)
	for i,t in reversed(list(enumerate(temp_enrich, 1))):
		# print(i,t)
		if t[3][0] < i*cutoff/length:
			return temp_enrich[:i]


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
	
	pvalue_over = scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1]*836
	pvalue_under = scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'less')[1]*836

	if pvalue_over < (10**(-cutoff)):
		return pvalue_over,0
	elif pvalue_under < (10**-2):
		return pvalue_under,1
	else:
		return ""
