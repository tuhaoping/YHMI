function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
	// crossDomain: false,
	timeout:20000,
	beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	}

});

var tableID = '';
// console.log(tableID)
var rootURL = '';
var setting_data = [];
var custom_save = false;
var bar_data;

$(document).ready(function(){
	// $.ajax({
	// 	url:"/result/init/",
	// 	type:"GET",
	// 	success:function(d){
	// 		console.log(d);
	// 	}
	// });

	$("#btn-send").click(function(){
		let jdata_gene
		let jdata_setting
		// let composition

		// if($("#switch").prop('checked')){
		// 	jdata_setting = $("tr.tr-custom-setting input[type=checkbox]:checked").map(function(){
		// 				id = $(this).closest('tr').prop('id');
		// 				textbox = $(this).siblings('input');
		// 				fClass = $(this).siblings('span').text();
		// 				console.log(id + "_" + fClass + "_" + textbox.val());
		// 				return id + "_" + fClass + "_" + textbox.val();
		// 			});
		// 	jdata_setting = JSON.stringify(jdata_setting.get());
		// 	// composition = $("#Composition-select").val();
		// }

		jdata_gene = JSON.stringify($('#inputTextArea').val().split("\n"));

		$.ajax({
			url: rootURL + '/result/specific',
			type: "POST",
			data:{
				'tableID': tableID,
				'InputGene': jdata_gene,
				'corrected': $("#div-corrected input[name=corrected]:checked").val(),
				'cutoff': $("#div-corrected input[type=text]:enabled").val()
			},
			success:function(res){
				// let histoneID = 1
				$("#userspecific").html(res);
				$("#userspecific a.histone_gene_modal").click(function(){
					var histone_gene_download_url = '/result/specific/histonegene?';
					[histoneID, histoneType] = $(this).attr('href').slice(1).split("_");
					$("#HistoneGeneInfo .modal-title").text("Genes with " + $(this).data('feature'));
					console.log(histone_gene_download_url)
					$("#HistoneGeneInfo a.download_a").attr('href',histone_gene_download_url+'tableID=' + tableID + "&histoneID="+histoneID + '&histoneType='+histoneType);
					$("#HistoneGeneInfo_table").DataTable().destroy();
					$("#HistoneGeneInfo_table").DataTable({
						serverSide: true,
						ajax: {
							url: rootURL + '/result/specific/histonegene',
							type: 'POST',
							dataType: 'json',
							data: {
								'tableID': tableID,
								'histoneID': histoneID,
								'histoneType': histoneType
							}
						},
					});
				})
			}
		});

		$.ajax({
			url: rootURL + '/result',
			type: 'POST',
			data: {
				'tableID':tableID,
				'InputGene': jdata_gene,
				// 'composition': composition,
				'corrected': $("#div-corrected input[name=corrected]:checked").val(),
				'cutoff': $("#div-corrected input[type=text]:enabled").val(),
			},
			dataType:'json',
			success:function(res){
				// $(".container-fluid.container-input").hide();
				$(".container-fluid.container-results").show();
				$("#leftAccordion .nav-link").removeClass("active");
				$("#leftAccordion .nav-link").eq(2).addClass("active");

				$("#result").html(res['template']);
				$("#Acetylation_tab").addClass("active show");

				$('html, body').stop().animate({
					scrollTop: ($('#userspecific').offset().top)-80
				}, 1000, 'easeInOutExpo');

				$("#Acetylation_Promoter_enrich_table, \
				   #Acetylation_Coding_Region_enrich_table, \
				   #Methylation_Promoter_enrich_table, \
				   #Methylation_Coding_Region_enrich_table, \
				   #H2A_Variant_Promoter_enrich_table, \
				   #H2A_Variant_Coding_Region_enrich_table, \
				   #H2BK123_Ubiquitination_Promoter_enrich_table, \
				   #H2BK123_Ubiquitination_Coding_Region_enrich_table, \
				   #TF_Promoter_enrich_table").DataTable({
						'order': [[5, "asc"], [0, 'asc']],
					});
				
				var intersect_data = {};
				$("#Acetylation_Promoter_enrich_table, \
				   #Acetylation_Coding_Region_enrich_table, \
				   #Methylation_Promoter_enrich_table, \
				   #Methylation_Coding_Region_enrich_table, \
				   #H2A_Variant_Promoter_enrich_table, \
				   #H2A_Variant_Coding_Region_enrich_table, \
				   #H2BK123_Ubiquitination_Promoter_enrich_table, \
				   #H2BK123_Ubiquitination_Coding_Region_enrich_table, \
				   #TF_Promoter_enrich_table").on('click', 'a.intersect', function(){
						var intersect_download_url = '/intersect/download?';
						$("#genemodal .modal-body .container-fluid").html("");
						id = $(this).attr('href').slice(1);
						$('#intersect_download_a').attr('href',intersect_download_url+'tableID=' + tableID + "&histone="+id);
						if(id in intersect_data){
							$("#genemodal .modal-body .container-fluid").html(intersect_data[$(this).attr('href')]);
								$("#intersect_datatable").DataTable({
									'order': [[1, "asc"], [0, 'asc']],
									"searching": false,
									"paging": false,
									"info": false,
								});
						}
						else {
							$.ajax({
								url: rootURL + '/intersect',
								type: 'POST',
								data: {
									'tableID':tableID,
									'histone':id,
								},
								success:function(res){
									$("#genemodal .modal-body .container-fluid").html(res);
									$("#intersect_datatable").DataTable({
										'order': [[1, "asc"], [0, 'asc']],
										"searching": false,
										"paging": false,
										"info": false,
									});
									intersect_data[id] = res
								}
							});
						};
					});
					
				// $("#TF_enrich_table").DataTable({
		  //   			'order': [[5, "asc"], [0, 'asc']],
		  //   		});

				$("#input_gene_table").DataTable();

				bar_data = res['data']
				barplot("Acetylation", 'fold');
				// $("#Acetylation_enrich_table_wrapper, #Methylation_enrich_table_wrapper, #others_enrich_table_wrapper, #TF_enrich_table_wrapper").css('padding', '10');
			}
		});
	});

});



$(document).ready(function(){
	$.ajax({
		url:rootURL + '/setting/init',
		type: 'GET',
		dataType: 'json',

		success:function(d){
			tableID = d['tableID'];
		}
	});

	$("tr.tr-custom-setting input[type=text]").change(function(){

		prevalue = $(this).data('prevalue');

		fClass = $(this).siblings('span').text();
		value = Number($(this).val());
		if (value && (value != prevalue)){
			$(this).data('prevalue', value);
			$(this).val(value);
			let id = $(this).closest('tr').prop('id');
			let setting_data = id + "_" + fClass + "_" + value;
			$.ajax({
				url:rootURL + '/setting/update',
				type:'POST',
				data: {
					'tableID':tableID,
					'setting_data': setting_data,
				}

			});
		}
		else{
			console.log('type err')
			$(this).val(prevalue);
		}
		// console.log($(this).defaultValue);
	});

	$("#btn-save-custom").click(function(){
		// let setting_data;
		setting_data = $("tr.tr-custom-setting input[type=checkbox]:checked").map(function(){
					id = $(this).closest('tr').prop('id');
					textbox = $(this).siblings('input');
					fClass = $(this).siblings('span').text();
					console.log(id + "_" + fClass + "_" + textbox.val());
					return id + "_" + fClass + "_" + textbox.val();
				}).get();
		console.log(setting_data);
		$.ajax({
			url:rootURL + '/setting/update',
			type: 'POST',
			data: {
				'tableID':tableID,
				'setting_data': JSON.stringify(setting_data),
			}

		});
		custom_save = true
	});

	$("#btn-reset").click(function(){
		$.ajax({
			url:rootURL + '/setting/default',
			type:"POST",
			data:{'tableID':tableID,}
		});
	});
});

window.onbeforeunload = function() {
	// console.log("leave!");
	$.ajax({
		async:false,
		url:rootURL + "/setting/drop",
		type:"POST",
		data:{'tableID':tableID,}
	});
};