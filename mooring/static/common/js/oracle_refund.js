var refund_booking =  {
           var: { 
              row_id: 0,
              total_from_money: parseFloat('0.00'),
              total_to_money: parseFloat('0.00'),
              total_bpoint_money: parseFloat('0.00'),
              bpoint_amount_available: parseFloat(''),
              booking_allocation_pool: parseFloat(''),
              unique_oracle_code_on_booking: {},
              booking_id: 0,
              newest_booking_id: 0,
              bpoint_trans_totals: {},
              oracle_code_refund_allocation_pool: ''
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
                          html += "<td><span class='money_sign'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"' ></td>";
                          html += "<td><input type='button' value='X' class='btn btn-danger' onclick='refund_booking.remove_row("+'"money_row'+refund_booking.var.row_id+'"'+")'  ></td>";
                          html += "</tr>";
               $("#from-money-booking tbody").append(html);
   	},
           to_money_add_row: function() {
              refund_booking.var.row_id = refund_booking.var.row_id + 1;
              var html = "<tr id='money_row"+refund_booking.var.row_id+"' >";
                  html += "<td><span id='oracle-error"+refund_booking.var.row_id+"'><input style='width: 200px;' class='form-control input-sm' type='text' id='oracle-code"+refund_booking.var.row_id+"' onblur='refund_booking.input_oracle_code_change("+refund_booking.var.row_id+")' ></span></td>";
                  html += "<td><input style='width: 100%' type='text' class='form-control input-sm' id='line-text"+refund_booking.var.row_id+"'></td>";
                  html += "<td><span class='money_sign'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"'></td>";
                  html += "<td><input type='button' value='X' class='btn btn-danger' onclick='refund_booking.remove_row("+'"money_row'+refund_booking.var.row_id+'"'+")' ></td>";
                  html += "</tr>";
              $("#to-money-booking tbody").append(html);
   	},
           remove_row: function(row_id) {
                $('#'+row_id).remove();
                refund_booking.total_from_money();
                refund_booking.total_to_money();
                refund_booking.total_bpoint_money();
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
  	                 url: '/api/check_oracle_code?oracle_code='+oracle_code,
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
           init: function() {
                   console.log('Mooring Oracle Refund Loaded');
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
                // START REFUND BOOKING BUTTON ( Esecute when button clicked )
           
                $('#refund-booking').on("click", function() {
                           $('.modal-backdrop').show();
                           $("#refund-booking").hide();
                           $("#refund-booking-wait").show();

                           var from_money_pool_array = [];
                           var to_money_pool_array = [];
                           var bpoint_trans_split_array = [];
                           var notification_message = "";
                           var un_pool = $('#unallocated_pool_refund').val();
                           var refund_method = $('input[name="refund_method"]:checked').val();

                           if (refund_method == undefined) { 
   			       notification_message += "<li>Please choose how the refund will be completed?</li>";
   			   }

                           if (refund_booking.var.total_from_money > 0) {
      			   } else {
   			     notification_message += "<li>From Money Pool total needs to be greater than $0.00.</li>";
   			   }
   		
                           if (un_pool > refund_booking.var.booking_allocation_pool) {
   				notification_message += "<li>Your unallocated pool from money pool total is greater than the unallocation pool available total</li>";
   			   }

                           if (refund_method == "1") {
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


                           if (refund_method == "1") { 
                                 $("#money-bpoint-booking").find('input').each(function() {
                                          input_id = this.id;
                                          input = this;

                                          if (this.type == 'text' || this.type=='hidden') {
                                               idvalname = input_id.substring(0, 10);
                                               rowid = input_id.replace(idvalname,"");
                                               if (idvalname == 'txn_number') {
                                                      var txn_number = $('#txn_number'+rowid).val();
                                                      var line_amount = $('#line-amount'+rowid).val();
                                                      if (parseFloat(line_amount) > parseFloat(refund_booking.var.bpoint_trans_totals[txn_number].amount)) {
                                                             notification_message += "<li>Transaction '"+txn_number+"' amount '"+line_amount+"' is greater than available amount '"+refund_booking.var.bpoint_trans_totals[txn_number].amount+"'</li>";

   			      		     }
                                               }
                                          }
                                 });
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
                                   $('#notification-body').html(notification_message);
                                   $('.modal-backdrop').show();
                                   $('#notification-box').show();
                                   $("#refund-booking").show();
                                   $("#refund-booking-wait").hide();
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
                                   $.ajax({
                                   url: '/api/refund_oracle',
                                   data: {
                                           csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), 
                                           money_from : JSON.stringify(from_money_pool_array),
                                           money_to: JSON.stringify(to_money_pool_array),
                                           bpoint_trans_split: JSON.stringify(bpoint_trans_split_array),
                                           refund_method: refund_method,
                                           booking_id: refund_booking.var.booking_id,
                                           newest_booking_id: refund_booking.var.newest_booking_id
                                   },
                                   // async: false,
                                   error: function(data) {
                                            $('#notification-body').html("There was a system error, attempting to process your request please try again later.");
   	                                 $('.modal-backdrop').show();
            	                         $('#notification-box').show();
                                   },
                                   dataType: 'json',
                                   success: function(data) {
                                            if (data.failed_refund == false) {
                                                $('#notification-body-success').html("Refund completed successfully");
                                                $('.modal-backdrop').show();
                                                $('#notification-box-success').show();
   					 } else {
                                                $('#notification-body-success').html("<span style='color: red'>A refund on one or more of the transaction failed and has been moved to the unllocation pool. Please see order history to see which transaction failed. </span>");
                                                $('.modal-backdrop').show();
                                                $('#notification-box-success').show();

   					 } 
                                   },
                                           type: 'post'
                                   })
   			}
   			console.log('Refund Button Clicked');
   		});
                // END REFUND BOOKING BUTTON ( Esecute when button clicked )


                   // Hide To Money and Bpoint until refund method selection is selected.
                   $('#to-money-booking-div').hide();
                   $('#money-bpoint-div').hide();
                   // --

                   $("input[name='refund_method']").on( "change", function() {
                       if (this.value == 1) { 
                           $('#to-money-booking-div').hide();
                           $('#money-bpoint-div').show();
   		    } else {
                           $('#to-money-booking-div').show();
                           $('#money-bpoint-div').hide();
                       }
                   });

                   refund_booking.to_money_add_row();
                   refund_booking.total_from_money();
                   refund_booking.total_to_money();
                   refund_booking.total_bpoint_money();

                   $('.modal-backdrop').hide();
                   refund_booking.var.bpoint_trans_totals
                   const btt_keys = Object.keys(refund_booking.var.bpoint_trans_totals);
                   for (const btt_key of btt_keys) {
                       refund_booking.var.row_id = refund_booking.var.row_id + 1;
                       var html = "<tr id='money_bpoint_row"+refund_booking.var.row_id+"' >";
                           html += "<td><input style='width: 150px;' class='form-control input-sm' type='hidden' id='txn_number"+refund_booking.var.row_id+"' value='"+btt_key+"'>"+btt_key+"  ($"+refund_booking.var.bpoint_trans_totals[btt_key]['amount']+" Available)</td>";
                           html += "<td><span class='money_sign'>$</span><input style='width: 100px;' class='form-control input-sm money' type='number' step='0.01' value='0.00' onblur='refund_booking.money_update(this);' id='line-amount"+refund_booking.var.row_id+"'></td>";
                           html += "</tr>";
                           $("#money-bpoint-booking tbody").append(html);
                   }


   	}
   }
   window.onload = function() { refund_booking.init(); }
