var ledger_payments = {
     var: {
	'current_invoice_group_id': '',
	'current_invoice_no': '',
	'current_booking_reference': '',
        'csrf_token': '',
        'payment_info_url' : '/ledger/payments/api/ledger/payments-info',
        'failed_transaction_url' : '/ledger/payments/api/ledger/failed-transactions',
        'payment_info': [],
	'pagestart': 0,
	'pageend': 10,
        'formoptions': {'frstatus': '', 'frsystem':'','frkeyword': '' },
	'selected_id': null
     },
     load_payment_info: function() {
	 data = {}
         $.ajax({
             url: ledger_payments.var.payment_info_url+"?invoice_group_id="+ledger_payments.var.current_invoice_group_id+"&invoice_no="+ledger_payments.var.current_invoice_no+"&booking_reference="+ledger_payments.var.current_booking_reference,
             method: "GET",
             headers: {'X-CSRFToken' : ledger_payments.var.csrf_token },
             //data: JSON.stringify({'payload': data,}),
             contentType: "application/json",
             success: function(data) {
		        var orderdata = "";
		        var bpointdata = "";
                        if (data.data.order.length > 0) {
                             for (let i = 0; i < data.data.order.length; i++) {
                                    var line_price_incl_tax_color = '#bb2d3b';
				    if (data.data.order[i].line_price_incl_tax > 0) {
					 line_price_incl_tax_color = '#157347';				         	   
			            }

				    orderdata+= "<tr><td>"+data.data.order[i].order_number+"</td><td>"+data.data.order[i].title+"</td><td>"+data.data.order[i].oracle_code+"</td><td style='background-color: "+line_price_incl_tax_color+"; color: #FFFFFF;'>$"+data.data.order[i].line_price_incl_tax+"</td><td>$"+data.data.order[i].rolling_total+"</td><td>"+data.data.order[i].order_date+"</td></tr>";
                                    console.log(data.data.order[i]); 
			     }

			     for (let i = 0; i < data.data.bpoint.length; i++) {
				     
                                     bpointdata+= "<tr><td>"+data.data.bpoint[i].txnnumber+"</td><td>"+data.data.bpoint[i].crn1+"</td><td>"+data.data.bpoint[i].action+"</td><td>$"+data.data.bpoint[i].amount+"</td><td>"+data.data.bpoint[i].processed+"</td></tr>";
				     console.log(data.data.bpoint[i]);
			     }
		      }

		      $('#order_list').html(orderdata);
		      $('#bpoint_tbody').html(bpointdata);
		      $('#total_payment_gateway').html('$&nbsp;'+data.data.total_gateway_amount);
		      $('#total_unallocated').html('$&nbsp;'+data.data.total_unallocated);

                      refund_booking.var.bpoint_trans_totals = data.data.bpoint;
		      refund_booking.var.unique_oracle_code_on_booking = data.data.oracle_code_totals; 
		      refund_booking.var.booking_reference = data.data.booking_reference;
		      refund_booking.var.booking_reference_linked = data.data.booking_reference_linked;
		      refund_booking.re_init();

		      $('#LoadingPopup').modal('hide');
		      // refund_booking.init();
		      console.log(data);
             },
             error: function(errMsg) {
		     $('#LoadingPopup').modal('hide');
             }
         });
     },
     update_page_failed_transactions: function(pagestart,pageend) { 
              ledger_payments.var.pagestart = pagestart;
	      ledger_payments.var.pageend = pageend;
              ledger_payments.load_failed_transactions();
     },
     update_failed_transaction_status: function(selected_id) { 
           ledger_payments.var.selected_id = selected_id;
           $('#ConfirmAction').modal('show');
     },
     update_failed_transaction_status_confirmed: function() {
	     ledger_payments.save_failed_transaction(ledger_payments.var.selected_id);
     },
     init_failed_transactions: function() {

          $("#fr-status").change(function() {
                  ledger_payments.var.formoptions.frstatus =this.value;
                  console.log(ledger_payments.var.formoptions.frstatus);
          });

          ledger_payments.var.formoptions.frstatus = $("#fr-status").val();

          $("#fr-system").change(function() {
                  ledger_payments.var.formoptions.frsystem =this.value;
                  console.log(ledger_payments.var.formoptions.frsystem);
          });

          ledger_payments.var.formoptions.frsystem = $("#fr-system").val();

          $("#fr-keyword").change(function() {
                  ledger_payments.var.formoptions.frkeyword =this.value;
                  console.log(ledger_payments.var.formoptions.frkeyword);
          });

          ledger_payments.var.formoptions.frkeyword = $("#fr-keyword").val();

          $("#fr-filter").click(function() {
                    ledger_payments.load_failed_transactions();
          });

          $("#confirm_status_change_btn").click(function() {
	      ledger_payments.update_failed_transaction_status_confirmed();
          });

          ledger_payments.load_failed_transactions();
     },	
     save_failed_transaction: function(rfid) {
	    $("#LoadingPopup").modal('show');
	    $('#ConfirmAction').modal('hide');
            $.ajax({
		    url: "/ledger/payments/api/ledger/failed-transaction-complete/"+rfid+"/",
		    method: "GET",
		    contentType: "application/json",
		    success: function(data) {
			    ledger_payments.load_failed_transactions();
                            setTimeout(function() {$('#LoadingPopup').modal('hide')}, 500);
	            },
                    error: function(errMsg) {
                            $('#LoadingPopup').modal('hide');
                    }
            });
     },
     load_failed_transactions: function() {

         data = {}
         $.ajax({
             url: ledger_payments.var.failed_transaction_url+"?pagestart="+ledger_payments.var.pagestart+"&pageend="+ledger_payments.var.pageend+"&status="+ledger_payments.var.formoptions.frstatus+"&system="+ledger_payments.var.formoptions.frsystem+"&keyword="+ledger_payments.var.formoptions.frkeyword,
             method: "GET",
             //headers: {'X-CSRFToken' : ledger_payments.var.csrf_token},
             //data: JSON.stringify({'payload': data,}),
             contentType: "application/json",
             success: function(data) {
                     var html = "";
                     if (data.data.rows.length > 0) {
	                    for (let i = 0; i < data.data.rows.length; i++) {
			            html+= "<tr>";
			            html+= "<td>"+data.data.rows[i]['invoice_group_id']+"</td>";
			            html+= "<td>"+data.data.rows[i]['booking_reference']+"</td>";
			            html+= "<td>"+data.data.rows[i]['invoice_reference']+"</td>";
			            html+= "<td>"+data.data.rows[i]['refund_amount']+"</td>";
			            html+= "<td>"+data.data.rows[i]['status_name']+"</td>";
			            html+= "<td>"+data.data.rows[i]['system_identifier']+"</td>";
			            html+= "<td>";
				    var link = '"/ledger/payments/oracle/payments?invoice_group_id='+data.data.rows[i]['invoice_group_id']+'"';
				    var link_completed = 'ledger_payments.update_failed_transaction_status("'+data.data.rows[i]['id']+'");'
			            html+= "<button type='button' class='btn btn-primary btn-sm' onclick='window.location="+link+"'>Oracle Refund</button>&nbsp;";
				    if (data.data.rows[i]['status'] == 0) { 
			                html+= "<button type='button' class='btn btn-primary btn-sm' onclick='"+link_completed+"'>Mark Completed</button>";
			            }
			            html+= "</td>";
			            html+= "</tr>";
                            }
		     }
                     
		     $('#failed-refunds-table tbody').html(html);

                     var pageiterate = data.data.totalrows / 10;
		     var totalpages = parseInt(pageiterate);

		     if (pageiterate > parseInt(pageiterate)) {
			 totalpages = parseInt(pageiterate) + 1;
		     }
		     
                     var pages = "";
                     pages+='<ul class="pagination  justify-content-center">';
                     pages+='<li class="page-item disabled">';
                     // pages+='<a class="page-link" href="#" tabindex="-1">Previous</a>';
                     pages+='</li>';
		     var pagelimit = 10;
		     var pstart = 0;
		     var pend = 0 + pagelimit;
		     for (let i = 1; i <= totalpages; i++) {
                         pages+='<li class="page-item ';
                         if (ledger_payments.var.pagestart == pstart && ledger_payments.var.pageend == pend) { 
			    pages+=' active';
		         }
			 pages+= '"><a class="page-link" href="javascript:void(0);" onclick="ledger_payments.update_page_failed_transactions('+pstart+','+pend+');">'+i+'</a></li>';
			 pstart = pstart + pagelimit;
			 pend = pend + pagelimit;
		     }
                     //    pages+='<li class="page-item active">';
                     //    pages+='<a class="page-link" href="#">2</a>';
                     //    pages+='</li>';
                     //pages+='<li class="page-item"><a class="page-link" href="#">3</a></li>';
                     pages+='<li class="page-item">';
                     // pages+='<a class="page-link" href="#">Next</a>';
                     pages+='</li>';
                     pages+='</ul>';

                     $('#pages').html(pages);
             },
             error: function(errMsg) {
                     $('#LoadingPopup').modal('hide');
             }
         });
     },
     init: function() {
       ledger_payments.load_payment_info();

     }
}

