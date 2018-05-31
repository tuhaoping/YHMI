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


function specific_block(jdata_gene){
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
			$("#gene_specific_table").DataTable({
				autoWidth:false,
				fixedHeader: true,
				scrollY: "300px",
				scrollCollapse: true,
				paging: false,
				info: false,
				searching: false,
				orderFixed: [ 0, 'asc' ],
				columnDefs:[
					{"width":"10%", "targets":0, "orderable": false},
					{"width":"12%", "targets":1},
					{"width":"9%", "targets":2},
					{"width":"30%", "targets":3},
					{"width":"9%", "targets":4},
					{"width":"30%", "targets":5}
				]
			});
			$("#gene_specific_table_wrapper div.dataTables_scrollBody").css('border-bottom-color', '#a5a7a9')
			$("#userspecific a.histone_gene_modal").click(function(){
				var gene_number = $(this).text();
				var region = $(this).data('region');
				var criteria = $(this).data('criteria');
				var histone_gene_download_url = rootURL + '/result/specific/histonegene?';
				[histoneID, histoneType] = $(this).attr('href').slice(1).split("_");
				$("#HistoneGeneInfo .modal-title").html(gene_number + " genes whose " + region + " have " + $(this).data('feature') + " [Criteria: " + criteria.replace('2', '<sub>2</sub>') +"]");
				$("#HistoneGeneInfo a.download_a").attr('href',histone_gene_download_url +
					'tableID='+tableID + "&histoneID="+histoneID + '&histoneType='+histoneType + "&region="+region + "&criteria="+criteria + "&histone");
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
	$('html, body').stop().animate({
		scrollTop: ($('#userspecific').offset().top)-80
	}, 1000, 'easeInOutExpo');
}

$(document).ready(function(){
	// $.ajax({
	// 	url:"/result/init/",
	// 	type:"GET",
	// 	success:function(d){
	// 		console.log(d);
	// 	}
	// });

	$("#btn-send, #btn-illegal-send").click(function(){
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


		var illegal_check = 1
		if ($(this).attr('id')=='btn-illegal-send')
			illegal_check = 0
		
		$.ajax({
			url: rootURL + '/result',
			type: 'POST',
			data: {
				'tableID':tableID,
				'InputGene': jdata_gene,
				// 'composition': composition,
				'corrected': $("#div-corrected input[name=corrected]:checked").val(),
				'cutoff': $("#div-corrected input[type=text]:enabled").val(),
				'illegal_check':illegal_check,
			},
			dataType:'json',
			success:function(res){
				// $(".container-fluid.container-input").hide();
				if(res['illegal']){
					$("#inputErr").modal('show');
					$("#illegal_gene").html("");
					res['illegal_gene'].forEach((g)=>{
						$("#illegal_gene").append("<tr><td class='py-1'>" + g + "</td></tr>");
					})
					$("#userspecific, #result").html('');
					return 0;
				}
				specific_block(jdata_gene);
				$(".container-fluid.container-results").show();
				// $("#leftAccordion .nav-link").removeClass("active");
				// $("#leftAccordion .nav-link").eq(2).addClass("active");

				$("#result").html(res['template']);
				$("#Acetylation_tab").addClass("active show");

				

				$("#Acetylation_Promoter_enrich_table, \
				   #Acetylation_Coding_Region_enrich_table, \
				   #Methylation_Promoter_enrich_table, \
				   #Methylation_Coding_Region_enrich_table, \
				   #H2A_Variant_Promoter_enrich_table, \
				   #H2A_Variant_Coding_Region_enrich_table, \
				   #H2BK123_Ubiquitination_Promoter_enrich_table, \
				   #H2BK123_Ubiquitination_Coding_Region_enrich_table").DataTable({
						'order': [[2, "asc"], [0, 'asc']],
						"autoWidth": false,
						'columnDefs':[
							{"width":"15%", "targets":0},
							{"width":"10%", "targets":1},
							{"width":"17%", "targets":2},
							{"width":"18%", "targets":3},
							{"width":"18%", "targets":4},
							{"width":"22%", "targets":5}

						]
					});

				$("#TF_Promoter_enrich_table").DataTable({
					'order': [[1, 'asc'], [2, "asc"], [0, 'asc']],
					"autoWidth": false,
					'columnDefs':[
						{"width":"15%", "targets":0},
						{"width":"10%", "targets":1},
						{"width":"17%", "targets":2},
						{"width":"18%", "targets":3},
						{"width":"20%", "targets":4},
						{"width":"20%", "targets":5}
					]
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
						var intersect_download_url = rootURL + '/intersect/download?';
						$("#genemodal .modal-body .container-fluid").html("");
						id = $(this).attr('href').slice(1);
						$('#intersect_download_a').attr('href',intersect_download_url+'tableID=' + tableID + "&histone="+id);
						if(id in intersect_data){
							$("#genemodal .modal-body .container-fluid").html(intersect_data[id]);
								$("#intersect_datatable").DataTable({
									'order': [[1, "asc"], [0, 'asc']],
									"searching": false,
									"paging": false,
									"info": false,
									"autoWidth": false,
									'columnDefs':[
										{"width":"25%", "targets":0},
										{"width":"75%", "targets":1},
									]
								});
							$("#modelTitleId").text($("#intersect_datatable > thead > tr > th.intersect_input").text());
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
										"autoWidth": false,
										'columnDefs':[
											{"width":"25%", "targets":0},
											{"width":"75%", "targets":1},
										]
									});
									intersect_data[id] = res;
								},
								complete:function(){
									$("#modelTitleId").text($("#intersect_datatable > thead > tr > th.intersect_input").text());
								}
							});
						};
					});
				// $("#Acetylation_Promoter_enrich_table, \
				//    #Acetylation_Coding_Region_enrich_table, \
				//    #Methylation_Promoter_enrich_table, \
				//    #Methylation_Coding_Region_enrich_table, \
				//    #H2A_Variant_Promoter_enrich_table, \
				//    #H2A_Variant_Coding_Region_enrich_table, \
				//    #H2BK123_Ubiquitination_Promoter_enrich_table, \
				//    #H2BK123_Ubiquitination_Coding_Region_enrich_table, \
				//    #TF_Promoter_enrich_table").on('click', 'a.histone_Gene', function(){

				// })
				$("#input_gene_table").DataTable();
				bar_data = res['data']
				barplot("Acetylation", 'fold');
				// $("#Acetylation_enrich_table_wrapper, #Methylation_enrich_table_wrapper, #others_enrich_table_wrapper, #TF_enrich_table_wrapper").css('padding', '10');
			},
			complete:function(){
				MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
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