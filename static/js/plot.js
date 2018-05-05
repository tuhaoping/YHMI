function barplot(ftype) {
	// var fig_id1 = ftype + "_Promoter_pvalue_fig"
	// var fig_id2 = ftype + "_Coding_Region_pvalue_fig"
	// var enrich_type = ['Enriched in Promoter', 'depleted in Promoter', 'Enriched in Coding Region', 'depleted in Coding Region', ''];
	var title, barcolor;

	// console.log(plot_data)
	if(ftype == 'H2A_Variant_and_H2B_Ubiquitination'){
		// var item = {'name':[], 'fold':[], 'pvalue':[]};
		var plot_data = bar_data['H2A_Variant'];
		var fig_id = "H2A_Variant_fig"
		plot(plot_data, 'pvalue');
		plot(plot_data, 'fold');
		
		// var item = {'name':[], 'fold':[], 'pvalue':[]};
		var plot_data = bar_data['H2BK123_Ubiquitination'];
		var fig_id = "H2BK123_Ubiquitination_fig"
		plot(plot_data, 'pvalue');
		plot(plot_data, 'fold');
	}
	else
		var plot_data = bar_data[ftype];
		plot(plot_data, 'pvalue');
		plot(plot_data, 'fold');

	function plot(plot_data, graphtype){
		var item = {'Promoter':{'name':[], 'fold':[], 'pvalue':[]}, 'Coding_Region':{'name':[], 'fold':[], 'pvalue':[]}};
		var fig_id1 = ftype + "_Promoter_" + graphtype +"_fig";
		var fig_id2 = ftype + "_Coding_Region_" + graphtype +"_fig"
		if(graphtype == 'fold'){
			plot_data.sort(function(a,b){return b[1]-a[1]})
			plot_data.forEach((e)=>{
				if(e[3]<2 || e[3]==4) histoneType = 'Promoter';
				else histoneType = 'Coding_Region';

				item[histoneType]['name'].push(e[0]);
				// item[histoneType]['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item[histoneType]['fold'].push(Math.log2(Number(e[1])));
			});
			title = 'Fold enrichment (log2)';
			barcolor_promoter = '#2679ff';
			barcolor_cds = '#2679ff';
		}
		else{
			plot_data.sort(function(a,b){return a[2]-b[2]})
			plot_data.forEach((e)=>{
				if(e[3]<2 || e[3]==4) histoneType = 'Promoter';
				else histoneType = 'Coding_Region';
				item[histoneType]['name'].push(e[0]);
				// item[histoneType]['name'].push(e[0] + " " + enrich_type[Number(e[3])]);
				item[histoneType]['pvalue'].push(-Math.log10(e[2]));
			});
			title = 'P-value (-log10)';
			barcolor_promoter = '#ffff00';
			barcolor_cds = '#ffff00';

		}

		var trace1 = {
			x:item['Promoter']['name'],
			y:item['Promoter'][graphtype],
			// width:[0.1],
			type: 'bar',
			// name:'Promoter',
			marker:{
				color: barcolor_promoter,
				opacity: 0.7,
			}
		}

		var trace2 = {
			x:item['Coding_Region']['name'],
			y:item['Coding_Region'][graphtype],
			// width:[0.1],
			type: 'bar',
			// name:'Coding Region',
			marker:{
				color: barcolor_cds,
				opacity: 0.7,
			}
		}

		var data1 = [trace1]
		var data2 = [trace2];


		var bargap1=0.1
		if(item['Promoter']['name'].length<10)
			bargap1 = 1-item['Promoter']['name'].length*0.1

		var layout1 = {
			bargap:bargap1,
			yaxis:{
				title: title,
			},
		}

		var bargap2=0.1
		if(item['Coding_Region']['name'].length<10)
			bargap2 = 1-item['Coding_Region']['name'].length*0.1

		var layout2 = {
			bargap:bargap2,
			yaxis:{
				title: title,
			},
		}

		var modeBarButtonsToRemove = [
			'sendDataToCloud',
			'hoverCompareCartesian',
			'zoom2d',
			// 'pan2d',
			'select2d',
			'lasso2d',
			'toggleSpikelines',
			'hoverClosestCartesian',
			'hoverCompareCartesian',
		]
		Plotly.newPlot(fig_id1, data1, layout1, {'displayModeBar':true, 'modeBarButtonsToRemove': modeBarButtonsToRemove});
		if(ftype != "TF")
			Plotly.newPlot(fig_id2, data2, layout2, {'displayModeBar':true, 'modeBarButtonsToRemove': modeBarButtonsToRemove});
	}
}



$(window).resize(function(){
	var ftype = $("#result .result-tabs-content > div.active.show").data('graph');
	// var histoneType = $("#result .result-tabs-content > div.active.show > .histonetype-pill a.active").data("graph");
	// console.log(histoneType);
	if(bar_data)
		if(ftype == 'H2A_Variant_and_H2B_Ubiquitination'){
        	  barplot('H2A_Variant');
          	barplot('H2BK123_Ubiquitination');
        	}
    	else{
    		barplot(ftype);
    	}
    else
    	return 0;

});
