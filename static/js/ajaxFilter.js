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
	$.ajax({
		url:"/enrich/init/",
		type:"GET",
		success:function(d){
			console.log(d);
		}
	});



	// Submit YNA filter set value to backend
	$("#submit-btn").click(function(){
		$("#feature_accordion .collapse").collapse('hide'); //close all collapse
		$("#genetextarea").addClass('geneText-close');
		let jdata = {};
		for (var i = 1; i < 5; i++) {
			
			chk_box = $("#collapse" + String(i) +" .feature-checkbox:checked");
			// console.log(chk_box);
			jdata[i] = chk_box.map(function(){
				let select = $(this).closest('div.row').find('select');
				let type = select.eq(0).val();
				let compare = select.eq(1).val();
				let value = $(this).closest('div.row').find('input.value').val();
				return $(this).val() + "_" + type + "_" + compare + "_" + value;
			}).get();
		};
	
		if($("#switch").prop("checked")){
			$.ajax({
		    	url:"/result/",
		    	data:{
		    		jdata: JSON.stringify(jdata),
		    		composition: $("#Composition").val(),
		    	},
		    	type:"POST",
		    	success:function(d){
		    		$("#resultDiv").html(d);
		    		$("#result_table").DataTable();
		    		// console.log(d);

		    		$.ajax({
		    			url:"/enrich/",
		    			type:"GET",
		    			success:function(d){
							$("#EnrichmentDiv").html(d);
				    		$("#enrich_table").DataTable({
				    			// 'order': [[3, "asc"]]
				    			'order': [[3, "asc"], [0, 'desc']]
				    		});
		    			}
		    		});
		    	},
		    });
		}
		else{
			$.ajax({
    			url:"/enrich/",
    			data:{
    				gene:$("#genetextarea").val()
    			},
    			type:"POST",
    			success:function(d){
    				$("#resultDiv").html('')
					$("#EnrichmentDiv").html(d);
		    		$("#enrich_table").DataTable({
		    			// 'order': [[3, "asc"]]
		    			'order': [[3, "asc"], [0, 'desc']]
		    		});
    			}
    		});

		}


	});



	// ajax to update SQL Views when custom setting
	$("#enrich-table tbody input[type=text]").focusout(function(){

		let text = $(this);
		let clss = text.closest('td').attr('class');

		if (text.val() < 2 && clss.includes("enriched")){
			text.addClass('err');
			text.val('2.0');
			setTimeout(function(){text.removeClass('err');}, 2000)
			return 0;
		}
		else if (text.val() > 0.5 && clss.includes("depleted")){
			text.addClass('err');
			text.val('0.5');
			setTimeout(function(){text.removeClass('err');}, 2000)
			return 0;
		}


		let feature = text.closest('tr').find('td').first().text();
		// console.log(feature + '/' + clss + '/' + text.val());
		setTimeout(function(){
			console.log(text.parent().find('input[type=checkbox]').prop('checked'));
			if(text.parent().find('input[type=checkbox]').prop('checked')){
				$.ajax({
					url:"/enrich/update/",
					type:"GET",
					data:{f:feature + '/' + clss + '/' + text.val()}
				});
			}
		},1000)
	});

});

window.onbeforeunload = function() {
	// console.log("leave!");
	$.ajax({
		async:false,
		url:"/enrich/close/",
		type:"GET",
	});
};