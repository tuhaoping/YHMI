from django.shortcuts import render
from YHMI_results.models import YhmiEnrichment, FilterResult

import json
import scipy.stats

# Create your views here.
def InputGeneSet(request):
	print(request.POST['InputGene'])
	data = request.POST['InputGene'].split("\n")
	return render(request, 'test.html', {'data':data})



def showEnrich(request):
	if request.POST['composition']:
		yhmi_filter = list(filter(None, json.loads(request.POST['InputGene'])))
		print(yhmi_filter)
		FilterResult.getGeneSet(yhmi_filter)
		geneset = set(yhmi_filter)

	else:
		geneset = set(filter(None, json.loads(request.POST['InputGene'])))
	
	data = YhmiEnrichment.objects.all()
	# if 'gene' in request.POST:
	# 	geneset = set(filter(None,request.POST['gene'].split('\n')))
	# else:
	# 	geneset = set(request.session['geneset'].split(','))

	S = len(geneset)
	enrich_value = []

	for i in data:
		temp_enrich = []
		temp_intersects = []

		gene = [set(i.pro_en.split(',')), set(), set(i.cod_en.split(',')), set()]
	# 	# gene = [set(i.pro_en.split(',')), set(i.pro_de.split(',')), set(i.cod_en.split(',')), set(i.cod_de.split(','))]
		
		for g in gene:
			T = len(g & geneset)
			G = len(g)
			temp_enrich.append(Hypergeometric_pvalue(T, S, G))
			temp_intersects.append([T, S, "{:0<.2f}%".format(T/S*100), G, 6576, "{:0<.2f}%".format(G/6576*100)])

		enrich_value.append([i.feature, zip(temp_enrich, temp_intersects)])

	render_dict = {
		'enrich_value': enrich_value,
	}
	return render(request, 'enrich_template.html', render_dict)




def Hypergeometric_pvalue(T, S, G, F=6572):
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
    
    pvalue = scipy.stats.fisher_exact( [ [T,G_T] , [S_T,F_G_S_T]] ,'greater')[1]

    if pvalue < (10**-2):
    	return "{:1.3E}".format(pvalue)
    else:
    	return ""
