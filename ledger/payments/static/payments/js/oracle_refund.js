var refund_booking =  {
           var: { 
              row_id: 0,
              total_from_money: parseFloat('0.00'),
              total_to_money: parseFloat('0.00'),
              total_bpoint_money: parseFloat('0.00'),
              total_cash_money: parseFloat('0.00'),
              bpoint_amount_available: parseFloat(''),
              booking_allocation_pool: parseFloat(''),
              unique_oracle_code_on_booking: {},
              booking_id: 0,
              newest_booking_id: 0,
              bpoint_trans_totals: {},
	      cash_trans_totals: {},
	      cash_on_invoices: [],
	      invoices_data: [],
              oracle_code_refund_allocation_pool: '',
	      api_url: '',
              cash_refund_url: '',
	      cash_payment_url: '',
	      booking_reference: '',
	      booking_reference_linked: '',
              csrf_token: ''
           }, 
   	from_money_add_row:  function() {
              refund_booking.var.row_id = refund_booking.var.row_id + 1;

              var money_from_dropdown = "<option>None</option>";
              const ocb_keys = Object.keys(refund_booking.var.unique_oracle_code_on_booking);
              for (const ocb_key of ocb_keys) {
                     money_from_dropdown +="<option value='"+ocb_key+"'>"+ocb_key+" ($"+refund_booking.var.unique_oracle_code_on_booking[ocb_key]+")</option>";
              }

              var html = "<tr id='money_row"+refund_booking.var.row_id+"' >";
                          html += "<td><span id='oracle-error"+refund_booking.var.row_id+"'>";
                                html += "<select class='form-control input-sm' id='oracle-code"+refund_booking.var.row_id+"' onchange='refund_booking.input_oracle_code_change("+refund_booking.var.row_id+")' >"+money_from_dropdown+"</select>";
                          html += "</span></td>";
                          html += "<td><input style='width: 100%' class='form-control input-sm' type='text' id='line-text"+refund_booking.var.row_id+"' ></td>";
                          html += "<td ><div style='display:flex'><span class='money_sign' style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"' ></div></td>";
                          html += "<td><button type='button'  class='btn btn-danger' onclick='refund_booking.remove_row("+'"money_row'+refund_booking.var.row_id+'"'+")'  ><i class='bi bi-x-lg'></i></button></td>";
                          html += "</tr>";
               $("#from-money-booking tbody").append(html);
   	  },
           to_money_add_row: function() {
              refund_booking.var.row_id = refund_booking.var.row_id + 1;
              var html = "<tr id='money_row"+refund_booking.var.row_id+"' >";
                  html += "<td><span id='oracle-error"+refund_booking.var.row_id+"'><input style='width: 200px;' class='form-control input-sm' type='text' id='oracle-code"+refund_booking.var.row_id+"' onblur='refund_booking.input_oracle_code_change("+refund_booking.var.row_id+")' ></span></td>";
                  html += "<td><input style='width: 100%' type='text' class='form-control input-sm' id='line-text"+refund_booking.var.row_id+"'></td>";
                  html += "<td><div style='display:flex'><span class='money_sign'  style='padding-top:6px;'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"'></div></td>";
                  html += "<td><button type='button' class='btn btn-danger' onclick='refund_booking.remove_row("+'"money_row'+refund_booking.var.row_id+'"'+")' ><i class='bi bi-x-lg'></i></button></td>";
                  html += "</tr>";
              $("#to-money-booking tbody").append(html);
   	},
        remove_row: function(row_id) {
                $('#'+row_id).remove();
                refund_booking.total_from_money();
                refund_booking.total_to_money();
                refund_booking.total_bpoint_money();
        },
        money_bpoint_trans_refund: function() {
                   $("#money-bpoint-booking tbody").html("");
                   for (let i = 0; i < refund_booking.var.bpoint_trans_totals.length; i++) {
                       if (refund_booking.var.bpoint_trans_totals[i].action == 'payment') {
                       refund_booking.var.row_id = refund_booking.var.row_id + 1;
                       total_available = refund_booking.var.bpoint_trans_totals[i].amount-refund_booking.var.bpoint_trans_totals[i].amount_refunded;
                       var html = "<tr id='money_bpoint_row"+refund_booking.var.row_id+"' >";
                           html += "<td><input style='width: 150px;' class='form-control input-sm' type='hidden' id='txn_number"+refund_booking.var.row_id+"' value='"+refund_booking.var.bpoint_trans_totals[i].txnnumber+"'>"+refund_booking.var.bpoint_trans_totals[i].txnnumber+"  ($"+total_available+" Available)</td>";
                           html += "<td><div style='display:flex'><span class='money_sign' style='padding-top: 6px'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"'></div></td>";
                           html += "</tr>";

                           $("#money-bpoint-booking tbody").append(html);
                       }
                   } 
	},
        money_cash_trans_payment: function() { 
                 var html = "<option selected value=''>Open this select menu</option>";
		 for (let i = 0; i < refund_booking.var.invoices_data.length; i++) { 
		      console.log(refund_booking.var.invoices_data[i].invoice_reference);
                      html += "<option value="+refund_booking.var.invoices_data[i].invoice_reference+">Invoice: "+refund_booking.var.invoices_data[i].invoice_reference+" Payment Status:"+refund_booking.var.invoices_data[i].payment_status+" Balance Owing $"+refund_booking.var.invoices_data[i].balance+"</option>";
	         }
                 $('#new-cash-line-invoice1').html(html); 

        },
        money_cash_trans_refund: function() {
                   $("#money-cash-booking tbody").html("");
		   refund_booking.var.row_id = 0;
                   for (let i = 0; i < refund_booking.var.cash_on_invoices.length; i++) {
                       refund_booking.var.row_id = refund_booking.var.row_id + 1;
                       total_available = refund_booking.var.cash_on_invoices[i].amount;
                       var html = "<tr id='money_bpoint_row"+refund_booking.var.row_id+"' >";
                           html += "<td><input style='width: 150px;' class='form-control input-sm' type='hidden' id='cash_invoice_number"+refund_booking.var.row_id+"' value='"+refund_booking.var.cash_on_invoices[i].invoice_reference+"'>"+refund_booking.var.cash_on_invoices[i].invoice_reference+"  ($"+total_available+" Available)</td>";
                           html += "<td><div style='display:flex'><span class='money_sign' style='padding-top: 6px'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='cash-line-amount"+refund_booking.var.row_id+"'></div></td>";
                           html += "</tr>";

                           $("#money-cash-booking tbody").append(html);
                   }

   	},
           total_bpoint_money: function() {
                refund_booking.var.total_bpoint_money = parseFloat('0.00');
                $('#total_bpoint_money').html('$'+refund_booking.format_money(refund_booking.var.total_bpoint_money));
                $("#money-bpoint-booking").find('input').each(function() {
                         if (this.type == 'number') {
                              if (this.value > 0 ) {
                              } else {
                                  this.value = '0.00';
                              }
                              refund_booking.var.total_bpoint_money = refund_booking.var.total_bpoint_money + parseFloat(this.value);
                              $('#total_bpoint_money').html('$'+refund_booking.format_money(refund_booking.var.total_bpoint_money));
                         }
                });
           },

           total_cash_money: function() {
                refund_booking.var.total_cash_money = parseFloat('0.00');
                $('#total_cash_money').html('$'+refund_booking.format_money(refund_booking.var.total_cash_money));
                $("#money-cash-booking").find('input').each(function() {
                         if (this.type == 'number') {
                              if (this.value > 0 ) {
                              } else {
                                  this.value = '0.00';
                              }
                              refund_booking.var.total_cash_money = refund_booking.var.total_cash_money + parseFloat(this.value);
                              $('#total_cash_money').html('$'+refund_booking.format_money(refund_booking.var.total_cash_money));
                         }
                });
           },


           total_from_money: function() {
                refund_booking.var.total_from_money = parseFloat('0.00');
                $('#total_from_money').html('$'+refund_booking.format_money(refund_booking.var.total_from_money));
                $("#from-money-booking").find('input').each(function() {
                         if (this.type == 'number') {
                              if (this.value > 0 ) {
                              } else {
                                  this.value = '0.00';
                              }
                              refund_booking.var.total_from_money = refund_booking.var.total_from_money + parseFloat(this.value);
                              $('#total_from_money').html('$'+refund_booking.format_money(refund_booking.var.total_from_money));
   		      }
                });
           },
           total_to_money: function() {
                refund_booking.var.total_to_money = parseFloat('0.00');
                $('#total_to_money').html('$'+refund_booking.format_money(refund_booking.var.total_to_money));
                $("#to-money-booking").find('input').each(function() {
                         if (this.type == 'number') {
                              if (this.value > 0 ) { 
   	                   } else {
                                  this.value = '0.00'; 
                              } 
                              refund_booking.var.total_to_money = refund_booking.var.total_to_money + parseFloat(this.value);
                              $('#total_to_money').html('$'+refund_booking.format_money(refund_booking.var.total_to_money));
                         }
                });
           },
           format_money: function(total, comma) {
              if (comma == null) { 
                       comma = true;
   	   }
              if (total == null) {
                 total = '0.00';
   	   }
              var neg = false;
              if(total < 0) {
                  neg = true;
                  total = Math.abs(total);
              }
              if (comma == true) { 
                  return (neg ? "-" : '') + parseFloat(total, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString();
              } else {
                  return (neg ? "-" : '') + parseFloat(total, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1").toString();
   	   } 
           },
           money_update: function(item) {
                              item.value = refund_booking.format_money(item.value, false);
                              refund_booking.total_from_money();
                              refund_booking.total_to_money();
                              refund_booking.total_bpoint_money();
                              refund_booking.total_cash_money();
                              var unallocated_pool_refund = $('#unallocated_pool_refund').val();
                              if (parseFloat(unallocated_pool_refund) > parseFloat(refund_booking.var.booking_allocation_pool)) {
                                  $('.tooltiptext').show();
   			   } else {
                                  $('.tooltiptext').hide();
   			   }
   	},
           input_oracle_code_change: function(row_id) {
                  var item = $('#oracle-code'+row_id);
                  
                  var code_found = refund_booking.check_oracle_code(item.val()); 
                  if (code_found == true) { 
                       $('#oracle-error'+row_id).css('border','none');
                       $('#oracle-error'+row_id).css('position','');
   	       } else { 
                       $('#oracle-error'+row_id).css('border','2px solid red');
                       $('#oracle-error'+row_id).css('border-radius','4px');
                       $('#oracle-error'+row_id).css('position','absolute');
                  }

   	},
           check_oracle_code: function(oracle_code) {
                    var found = false; 
                    $.ajax({
  	                 url: '/ledger/payments/api/ledger/oracle-codes-lookup?oracle_code='+oracle_code,
         	         data: {
                   	 format: 'json'
                    },
                    async: false,
                    error: function() {
                            $('#info').html('<p>An error has occurred</p>');
                    },
                    dataType: 'json',
   	            success: function(data) {
                   	 found = data.found;
                 	 },
                            type: 'GET'
                    });
                    return found;
           },
	   re_init: function() {
                   $('#from-money-booking tr').each(function(){ 
                           var fromtrid = this.id.substring(0, 9);
                           if (fromtrid.length > 0) {
                             $("#"+this.id).remove();
                           }
                   });

		   $('#to-money-booking tbody').html("");
                   refund_booking.to_money_add_row();
		   refund_booking.total_from_money();
		   refund_booking.total_to_money();
		   refund_booking.total_bpoint_money();
                   refund_booking.money_bpoint_trans_refund();
		   refund_booking.money_cash_trans_refund();
		   refund_booking.money_cash_trans_payment();
		   

                   $("#refund-booking").show();
                   $("#refund-booking-wait").hide();

	   },
           init: function() {
                   console.log('Oracle Refund Loaded');
                   $('#from-money-booking-button').on("click", function() {
                     refund_booking.from_money_add_row();
   		   });
                   $('#to-money-booking-button').on("click", function() {
                     refund_booking.to_money_add_row();
                   });
                   $('.close').on("click", function() {
                           $('.modal-backdrop').hide();
                           $('#notification-box').hide();
   		        // $('.modal').hide();
   		});
                $('#okBtn').on("click", function() {
                        $('.modal-backdrop').hide();
                        // $('.modal').hide();
                        $('#notification-box').hide();
                });
                $('#success-refund').on("click", function() {
   		     $('.modal-backdrop').hide();
                        $('#notification-box-success').hide();
                        window.location.href  = window.location.href;
   		});

                // CREATE CASH RECORD
		$('#record-payment').on("click", function() {
                    var notification_message = "";
                    var newcashlineamount1 = $('#new-cash-line-amount1').val();   
                    var newcashlinesource1 = $('#new-cash-line-source1').val();
	            var newcashlinereceipt1 = $('#new-cash-line-receipt1').val();
	            var newcashlineinvoice1 = $('#new-cash-line-invoice1').val();

                    if (newcashlineinvoice1.length > 0) {
                    } else {
                        notification_message += "<li>Please select an invoice.</li>";
                    }

		    if (newcashlineamount1 > 0) {
		    } else {
                        notification_message += "<li>Please enter an amount greater than 0.00.</li>";
	            }

                    if (newcashlinesource1.length > 0) {
	            } else {
                        notification_message += "<li>Please select a payment source.</li>";
		    }

	            if ( newcashlinereceipt1.length > 2) { 
                       
		    } else {
                           notification_message += "<li>Please enter a receipt number.</li>";
		    }


                    if (notification_message.length > 0) {
                            $('#error-message').html(notification_message);
                            $("#MessageBox").modal("show");
                            //$('#LoadingPopup').modal('hide');
                            $('#notification-body').html(notification_message);
                            $('.modal-backdrop').show();
                            $('#notification-box').show();
                    } else {
                           $('#LoadingPopup').modal('show');

                             $.ajax({
                              beforeSend: function(xhrObj){
                                xhrObj.setRequestHeader("Content-Type","application/json");
                                xhrObj.setRequestHeader("Accept","application/json");
                             },
                             url: refund_booking.var.cash_refund_url,
                             headers: {'X-CSRFToken' : refund_booking.var.csrf_token },
                             data: JSON.stringify({
                                      "invoice" : newcashlineinvoice1,
                                     "amount": newcashlineamount1,
                                     "receipt": newcashlinereceipt1,
                                     "source": newcashlinesource1,
                                     "type": 'payment'}),

                             // async: false,
                             error: function(data) {
				   var error_text = "There was a system error, attempting to process your request please try again later.";
				   if ('responseText' in data) {
                                         error_text = data.responseText;
				   } else {

				   }
                                   
				   $("#MessageBox").modal("show");
                                   $('#error-message').html(error_text);
                                   setTimeout("ledger_payments.load_payment_info();",500);
                             },
                             dataType: 'json',
                             success: function(data, textStatus, xhr) {
                                   $('#new-cash-line-amount1').val("");
                                   $('#new-cash-line-source1').val("");
                                   $('#new-cash-line-receipt1').val("");
                                   $('#new-cash-line-invoice1').val("");
                                   if (xhr.status == 201) {
                                          $('#notification-body-success').html("Refund completed successfully");
                                          $('.modal-backdrop').show();
                                          $('#notification-box-success').show();
                                      setTimeout("ledger_payments.load_payment_info()",500);
                                   } else {
                                          $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                          $('.modal-backdrop').show();
                                          $('#notification-box-success').show();
                                      setTimeout("ledger_payments.load_payment_info();",500);

                                   }
                             },
                                     type: 'post'
                             })


                    }

		});


                // START REFUND BOOKING BUTTON ( Esecute when button clicked )
                $('#refund-booking').on("click", function() {
                           $('.modal-backdrop').show();
                           $("#refund-booking").hide();
                           $("#refund-booking-wait").show();
                           console.log('STARTING REFUND');
                           var from_money_pool_array = [];
                           var to_money_pool_array = [];
                           var bpoint_trans_split_array = [];
                           var notification_message = "";
                           var un_pool = $('#unallocated_pool_refund').val();
                           var trans_method = $('input[name="trans_method"]:checked').val();

			   if (trans_method == "4") {

		           } else {

                                if (trans_method == undefined) { 
   			            notification_message += "<li>Please choose how the refund will be completed?</li>";
   			        }

                                if (refund_booking.var.total_from_money > 0) {
      			        } else {
   			          notification_message += "<li>From Money Pool total needs to be greater than $0.00.</li>";
   			        }
   		
                                if (un_pool > refund_booking.var.booking_allocation_pool) {
   			             notification_message += "<li>Your unallocated pool from money pool total is greater than the unallocation pool available total</li>";
   			        }

                                if (trans_method == "1") {
                                     if (refund_booking.var.total_from_money != refund_booking.var.total_bpoint_money) {
   			                notification_message += "<li>Your total from money pool dose not match your bpoint allocation total.</li>"
   			             }

                                     if (refund_booking.var.total_from_money > refund_booking.var.bpoint_amount_available) {
                                         notification_message += "<li>Your total from pool is more than the available payment gateway funds</li>";
                                     }
                                } else { 
                                     if (refund_booking.var.total_to_money > refund_booking.var.total_from_money) {
                                              notification_message += "<li>Your to money pool is greater than the from money pool.</li>";
                                     }
                                     if (refund_booking.var.total_to_money != refund_booking.var.total_from_money) {
                                         notification_message += "<li>Your total from and to pools do not match.</li>";
                                     }
                                }


                                $("#from-money-booking").find('input, select').each(function() {
                                         input_id = this.id;
                                         input = this; 
                                         if (this.type == 'text' || this.type=='select-one') {
                        
                                              idvalname = input_id.substring(0, 11);
                                              rowid = input_id.replace(idvalname,"");
                                              if (idvalname == 'oracle-code') { 
                                                     var val = $('#'+input_id).val();
                                                     var money_from_amount = $('#line-amount'+rowid).val();
                                                     var line_text = $('#line-text'+rowid).val();
                                                     if (val.length > 0) { 
   			             		   if (refund_booking.check_oracle_code(val) == false) {
   			             			notification_message += "<li>'"+val+"' oracle code does not exist. </li>";
   			             		   }
                                                           if (parseFloat(money_from_amount) > parseFloat(refund_booking.var.unique_oracle_code_on_booking[val])) {
   			             			notification_message += "<li>'"+val+"' oracle code amount is greater than available amount pool of $"+refund_booking.var.unique_oracle_code_on_booking[val]+". </li>";
   			             		   }
                                                           if (line_text.length < 3) {
   			             			notification_message += "<li>Please enter a suitable line description length. </li>";
   			             	           }
                                                     }
   			                   }
                                         }
                                });
                           }

                           if (trans_method == "1") { 
                                 $("#money-bpoint-booking").find('input').each(function() {
                                          input_id = this.id;
                                          input = this;

                                          if (this.type == 'text' || this.type=='hidden') {
                                               idvalname = input_id.substring(0, 10);
                                               rowid = input_id.replace(idvalname,"");
                                               if (idvalname == 'txn_number') {
                                                      var txn_number = $('#txn_number'+rowid).val();
                                                      var line_amount = $('#line-amount'+rowid).val();
						      var btt = {};
						      for (let i = 0; i < refund_booking.var.bpoint_trans_totals.length; i++) {
							      if (refund_booking.var.bpoint_trans_totals[i].txnnumber == txn_number) {
                                                                       btt = refund_booking.var.bpoint_trans_totals[i]
                                                                                
							      }

						      }

                                                      if (parseFloat(line_amount) > parseFloat(btt.amount)) {
                                                             notification_message += "<li>Transaction '"+txn_number+"' amount '"+line_amount+"' is greater than available amount '"+btt.amount+"'</li>";

   			      		     }
                                               }
                                          }
                                 });
		           } else if (trans_method == "4") {
                               $("#refund-booking").show();
                               $("#refund-booking-wait").hide();
   			   } else {
                                  $("#to-money-booking").find('input, select').each(function() {
                                           input_id = this.id;
                                           input = this;
                                           if (this.type == 'text' || this.type=='select-one') {
  
                                                idvalname = input_id.substring(0, 11);
                                                rowid = input_id.replace(idvalname,"");
                                                if (idvalname == 'oracle-code') {
                                                       var val = $('#'+input_id).val();
                                                       var money_from_amount = $('#line-amount'+rowid).val();
                                                       var line_text = $('#line-text'+rowid).val();
                                                       if (val.length > 0) {
                                                             if (refund_booking.check_oracle_code(val) == false) {
                                                                  notification_message += "<li>'"+val+"' oracle code does not exist. </li>";
                                                             }
                                                             if (line_text.length < 3) {
                                                                  notification_message += "<li>Please enter a suitable line description length. </li>";
                                                             }
                                                       }
                                                }
                                           }
                                  });

   			   }
                           if (notification_message.length > 0) {
				   $('#error-message').html(notification_message);
                                   $("#MessageBox").modal("show");
				   //$('#LoadingPopup').modal('hide');
                                   $('#notification-body').html(notification_message);
                                   $('.modal-backdrop').show();
                                   $('#notification-box').show();
                                   $("#refund-booking").show();
                                   $("#refund-booking-wait").hide();
   			   } else {

				    if (trans_method == "4") {




                                       $('#LoadingPopup').modal('show');


                                        $("#money-cash-booking").find('input').each(function() {
                                                 input_id = this.id;
                                                 input = this;

                                                 if (this.type == 'text' || this.type=='hidden') {
                                                      idvalname = input_id.substring(0, 19);
                                                      rowid = input_id.replace(idvalname,"");
						       console.log(idvalname);
                                                      if (idvalname == 'cash_invoice_number') {
                                                             var cash_iv = $('#cash_invoice_number'+rowid).val();
                                                             var line_amount = $('#cash-line-amount'+rowid).val();
                                                             $.ajax({
                                                              beforeSend: function(xhrObj){
                                                                xhrObj.setRequestHeader("Content-Type","application/json");
                                                                xhrObj.setRequestHeader("Accept","application/json");
                                                             },
                                                             url: refund_booking.var.cash_refund_url,
                                                             headers: {'X-CSRFToken' : refund_booking.var.csrf_token },
                                                             data: JSON.stringify({ 
								      "invoice" : cash_iv,
                                                                     "amount": line_amount,
                                                                     "details": 'refunding',
                                                                     "source": 'cash',
                                                                     "type": 'refund'}),

                                                             // async: false,
                                                             error: function(data) {
                                                                   $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
                                                                   $('.modal-backdrop').show();
                                                                   $('#notification-box').show();
                                                                   ledger_payments.load_payment_info();
                                                             },
                                                             dataType: 'json',
                                                             success: function(data, textStatus, xhr) {
                                                                   if (xhr.status == 201) {
                                                                          $('#notification-body-success').html("Refund completed successfully");
                                                                          $('.modal-backdrop').show();
                                                                          $('#notification-box-success').show();
                                                                      setTimeout("ledger_payments.load_payment_info()",500);
                                                                   } else {
                                                                          $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                                                          $('.modal-backdrop').show();
                                                                          $('#notification-box-success').show();
                                                                      ledger_payments.load_payment_info();

                                                                   }
                                                             },
                                                                     type: 'post'
                                                             })


                                                      }
                                                 }
                                       });


				    } else {
                                        var unallocated_text = $('#unallocated-text').val();
                                        from_money_pool_array.push({'oracle-code': refund_booking.var.oracle_code_refund_allocation_pool, 'line-text': unallocated_text, 'line-amount': un_pool});

                                        $("#from-money-booking").find('input, select').each(function() {
                                                 input_id = this.id;
                                                 input = this;
                                                  
                                                 if (this.type == 'text' || this.type=='select-one') {
                                                      idvalname = input_id.substring(0, 11);
                                                      rowid = input_id.replace(idvalname,"");
                                                      if (idvalname == 'oracle-code') {
                                                             var oracle_code = $('#oracle-code'+rowid).val();
                                                             var line_text = $('#line-text'+rowid).val();
                                                             var line_amount = $('#line-amount'+rowid).val();
                                                             from_money_pool_array.push({'oracle-code': oracle_code, 'line-text': line_text, 'line-amount': line_amount});
                                                      }
                                                 }
                                        });
    

                                        $("#to-money-booking").find('input').each(function() {
                                                 input_id = this.id;
                                                 input = this;

                                                 if (this.type == 'text') {
                                                      idvalname = input_id.substring(0, 11);
                                                      rowid = input_id.replace(idvalname,"");
                                                      if (idvalname == 'oracle-code') {
                                                             var oracle_code = $('#oracle-code'+rowid).val();
                                                             var line_text = $('#line-text'+rowid).val();
                                                             var line_amount = $('#line-amount'+rowid).val();
                                                             to_money_pool_array.push({'oracle-code': oracle_code, 'line-text': line_text, 'line-amount': line_amount});
                                                      }
                                                 }
                                        });

                                        $("#money-bpoint-booking").find('input').each(function() {
                                                 input_id = this.id;
                                                 input = this;

                                                 if (this.type == 'text' || this.type=='hidden') {
                                                      idvalname = input_id.substring(0, 10);
                                                      rowid = input_id.replace(idvalname,"");
                                                      if (idvalname == 'txn_number') {
                                                             var txn_number = $('#txn_number'+rowid).val();
                                                             var line_amount = $('#line-amount'+rowid).val();
                                                             bpoint_trans_split_array.push({'txn_number': txn_number, 'line-amount': line_amount});
                                                      }
                                                 }
                                       });
				       $('#LoadingPopup').modal('show');
				       // $('input[name="csrfmiddlewaretoken"]').val(),
                                       $.ajax({
                                       url: refund_booking.var.api_url,
			               headers: {'X-CSRFToken' : refund_booking.var.csrf_token },
                                       data: {
                                               csrfmiddlewaretoken: refund_booking.var.csrf_token,
                                               money_from : JSON.stringify(from_money_pool_array),
                                               money_to: JSON.stringify(to_money_pool_array),
                                               bpoint_trans_split: JSON.stringify(bpoint_trans_split_array),
                                               refund_method: trans_method,
                                               booking_id: refund_booking.var.booking_id,
                                               newest_booking_id: refund_booking.var.newest_booking_id,
				               booking_reference: refund_booking.var.booking_reference,
				               booking_reference_linked: refund_booking.var.booking_reference_linked
                                       },
                                       // async: false,
                                       error: function(data) {
                                             $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
   	                                     $('.modal-backdrop').show();
            	                             $('#notification-box').show();
                                             ledger_payments.load_payment_info();
                                       },
                                       dataType: 'json',
                                       success: function(data) {

                                             if (data.failed_refund == false) {
                                                    $('#notification-body-success').html("Refund completed successfully");
                                                    $('.modal-backdrop').show();
                                                    $('#notification-box-success').show();
				            	ledger_payments.load_payment_info();
   				             } else {
                                                    $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                                    $('.modal-backdrop').show();
                                                    $('#notification-box-success').show();
				            	ledger_payments.load_payment_info();

   				             } 
                                       },
                                               type: 'post'
                                       })

			           }
   			}
   			console.log('Refund Button Clicked');
   		   });
                   // END REFUND BOOKING BUTTON ( Esecute when button clicked )


                   // Hide To Money and Bpoint until refund method selection is selected.
                   $('#to-money-booking-div').hide();
                   $('#money-bpoint-div').hide();
		   $('#money-cash-div').hide();
		   $('#cash-payment').hide();
                   // --

                   $("input[name='trans_method']").on( "change", function() {
		       $('#from-money-booking-div').show();
		       $('#to-money-booking-div').hide();
                       $('#money-bpoint-div').hide();
		       $('#money-cash-div').hide();
		       $('#cash-payment').hide();
		       $('#money-management').show();

                       if (this.value == 1) { 
                           // $('#to-money-booking-div').hide();
                           $('#money-bpoint-div').show();
		       } else if (this.value == 4) {
                           $('#from-money-booking-div').hide();
			   $('#money-cash-div').show();
                       } else if (this.value == 5) {
			   $('#cash-payment').show();
			   $('#money-management').hide();
      		       } else {
                           $('#to-money-booking-div').show();
                           //$('#money-bpoint-div').hide();
                       }
                   });
                   refund_booking.re_init();

                   $('.modal-backdrop').hide();

                   refund_booking.money_bpoint_trans_refund();
		   refund_booking.money_cash_trans_refund();
		   refund_booking.money_cash_trans_payment();
                   // const btt_keys = Object.keys(refund_booking.var.bpoint_trans_totals);
                   //for (const btt_key of btt_keys) {
		   //$("#money-bpoint-booking tbody").html("");
		   //for (let i = 0; i < refund_booking.var.bpoint_trans_totals.length; i++) {
		   //    if (refund_booking.var.bpoint_trans_totals[i].action == 'payment') { 
                   //    refund_booking.var.row_id = refund_booking.var.row_id + 1;
		   //    total_available = refund_booking.var.bpoint_trans_totals[i].amount-refund_booking.var.bpoint_trans_totals[i].amount_refunded;
                   //    var html = "<tr id='money_bpoint_row"+refund_booking.var.row_id+"' >";
                   //        html += "<td><input style='width: 150px;' class='form-control input-sm' type='hidden' id='txn_number"+refund_booking.var.row_id+"' value='"+refund_booking.var.bpoint_trans_totals[i].txnnumber+"'>"+refund_booking.var.bpoint_trans_totals[i].txnnumber+"  ($"+total_available+" Available)</td>";
                   //        html += "<td><div style='display:flex'><span class='money_sign' style='padding-top: 6px'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"'></div></td>";
                   //        html += "</tr>";
		   //    
                   //        $("#money-bpoint-booking tbody").append(html);
		   //    }
                   //}


   	}
   }
   window.onload = function() { refund_booking.init(); }
