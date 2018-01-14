var csrftoken = Cookies.get('csrftoken');
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

$(document).ready(function(){
	var rootURL = '';
	// $.ajax({
	// 	url:"/result/init/",
	// 	type:"GET",
	// 	success:function(d){
	// 		console.log(d);
	// 	}
	// });

	$("#btn-send").click(function(){
		let jdata
		let composition

		if($("#switch").prop('checked')){
			jdata = $("tr.tr-feature input[type=checkbox]:checked").map(function(){
						id = $(this).closest('tr').prop('id');
						textbox = $(this).siblings('input');
						return id + "_" + textbox.prop('class') + "_" + textbox.val();
					});
			jdata = JSON.stringify(jdata.get());
			composition = $("#Composition-select").val();
		}
		else{
			jdata = JSON.stringify($('#inputTextArea').val().split("\n"));
			composition = null;
		}

		console.log(composition);
		$.ajax({
			url: rootURL + '/result',
			type: 'POST',
			data: {
				'InputGene': jdata,
				'composition': composition,
			},
			success:function(d){
				$(".container-fluid.container-input").hide();
				$(".container-fluid.container-results").show();
				$("#leftAccordion .nav-link").removeClass("active");
				$("#leftAccordion .nav-link").eq(2).addClass("active");

				$("#result").html(d);
				$("#enrich_table").DataTable({
		    			// 'order': [[3, "asc"]]
		    			'order': [[3, "asc"], [0, 'desc']]
		    		});
				$("#enrich_table_wrapper").css('padding', '10');

				console.log('success');
			}
		});

	});


	// Submit YNA filter set value to backend
	// $("#btn-send").click(function(){
	// 	let jdata = {};

	// 	jdata['filter'] = $("tr.tr-feature input[type=checkbox]:checked").map(function(){
	// 				id = $(this).closest('tr').prop('id');
	// 				textbox = $(this).siblings('input');
	// 				return id + "_" + textbox.prop('class') + "_" + textbox.val();
	// 			});
	// 	console.log(jdata);
	
	// 	// if($("#switch").prop("checked")){
	// 	// 	$.ajax({
	// 	//     	url:"/result/",
	// 	//     	data:{
	// 	//     		jdata: JSON.stringify(jdata),
	// 	//     		composition: $("#Composition").val(),
	// 	//     	},
	// 	//     	type:"POST",
	// 	//     	success:function(d){
	// 	//     		$("#resultDiv").html(d);
	// 	//     		$("#result_table").DataTable();
	// 	//     		// console.log(d);

	// 	//     		$.ajax({
	// 	//     			url:"/enrich/",
	// 	//     			type:"GET",
	// 	//     			success:function(d){
	// 	// 					$("#EnrichmentDiv").html(d);
	// 	// 		    		$("#enrich_table").DataTable({
	// 	// 		    			// 'order': [[3, "asc"]]
	// 	// 		    			'order': [[3, "asc"], [0, 'desc']]
	// 	// 		    		});
	// 	//     			}
	// 	//     		});
	// 	//     	},
	// 	//     });
	// 	// }
	// 	// else{
	// 	// 	$.ajax({
 //  //   			url:"/enrich/",
 //  //   			data:{
 //  //   				gene:$("#genetextarea").val()
 //  //   			},
 //  //   			type:"POST",
 //  //   			success:function(d){
 //  //   				$("#resultDiv").html('')
	// 	// 			$("#EnrichmentDiv").html(d);
	// 	//     		$("#enrich_table").DataTable({
	// 	//     			// 'order': [[3, "asc"]]
	// 	//     			'order': [[3, "asc"], [0, 'desc']]
	// 	//     		});
 //  //   			}
 //  //   		});

	// 	// }


	// });



// 	// ajax to update SQL Views when custom setting
// 	$("#enrich-table tbody input[type=text]").focusout(function(){

// 		let text = $(this);
// 		let clss = text.closest('td').attr('class');

// 		if (text.val() < 2 && clss.includes("enriched")){
// 			text.addClass('err');
// 			text.val('2.0');
// 			setTimeout(function(){text.removeClass('err');}, 2000)
// 			return 0;
// 		}
// 		else if (text.val() > 0.5 && clss.includes("depleted")){
// 			text.addClass('err');
// 			text.val('0.5');
// 			setTimeout(function(){text.removeClass('err');}, 2000)
// 			return 0;
// 		}


// 		let feature = text.closest('tr').find('td').first().text();
// 		// console.log(feature + '/' + clss + '/' + text.val());
// 		setTimeout(function(){
// 			console.log(text.parent().find('input[type=checkbox]').prop('checked'));
// 			if(text.parent().find('input[type=checkbox]').prop('checked')){
// 				$.ajax({
// 					url:"/enrich/update/",
// 					type:"GET",
// 					data:{f:feature + '/' + clss + '/' + text.val()}
// 				});
// 			}
// 		},1000)
// 	});

// });

// window.onbeforeunload = function() {
// 	// console.log("leave!");
// 	$.ajax({
// 		async:false,
// 		url:"/enrich/close/",
// 		type:"GET",
// 	});
});