from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

# @ensure_csrf_cookie
@csrf_exempt
def HomePage(request):
	filter_item = {
		'Histone Acetylation Patterns ':{
			'Histone Acetylation (WildType)':['H3K4ac vs H3', 'H3K9ac vs H3 [YPD]', 'H3K14ac vs H3 [YPD]', 'H4ac vs H3 [YPD]'],
			'Histone Acetylation (Mutant)':['H3K4ac [set1D] vs [WT]', 'H3K4ac vs H3 [set1D]']
		},
		'Histone Methylation Patterns':{
			'Histone Methylation (WildType)':['H3K4me3 vs H3 [WCE]', 'H3K36me3 vs H3', 'H3K79me2 vs H3', 'H3K79me3 vs H3', 'H3K4me1 vs H3', 'H3K4me2 vs H3', 'H3R2me2a vs H3'],
			'Histone Methylation (Mutant)':['H3K4me3 vs H3 [ubp8D]', 'H3K36me3 vs H3 [ubp8D]', 'H3K79me3 vs H3 [ubp8D]', 'H3K4me3 vs H3 [ubp10D]', 'H3K79me3 vs H3 [ubp10D]']
		},
		'H2A Variant and H2B Ubiquitination Patterns':{
			'H2A Variant':['H2A.Z vs H2B', 'H2A vs H2B'],
			'H2B Ubiquitination (WildType)':['H2BK123ub vs H2'],
			'H2B Ubiquitination (Mutant)':['H2BK123ub vs H2 [ubp8D]', 'H2BK123ub vs H2 [ubp10D]']
		},
		# 'Regulatory Protein Binding Sites':{
		# 	'Regulatory Protein Binding Sites':['Ada2','Ahc1','Aor1','Arp6','Ash1','Bre1','Bre2','Chd1','Dot1','Eaf3','Elp3','Epl1','Esa1','Gcn5','Hda1','Hfi1','Hos1','Hos2','Hos3','Htz1','Ino80','Ioc2','Ioc3','Ioc4','Isw1','Isw2','Itc1','Jhd1','Jhd2','Nap1','Nhp6a','Pob3','Rad6','Rpd3','Rph1','Rsc1','Rsc2','Rsc4','Rsc8','Rsc9','Rtt109','Rvb1','Rvb2','Rxt1','Rxt2','Sas4','Set1','Set2','Sif2','Sin3','Sir2','Sir3','Snf2','Snf5','Spt16','Spt2','Spt20','Spt3','Spt6','Spt7','Spt8','Swc1','Swi3','Swr1','Taf10','Taf14','Taf5','Taf9','Ubp8','Ume6','Vps72','Yaf9','Yng1']
		# }
	}
	


	render_dict = {
		'item':filter_item,
	}
	return render(request, 'home.html', render_dict)