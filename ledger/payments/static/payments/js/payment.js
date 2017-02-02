$(function(){
    $(document).foundation();
    var $other_form = $('#other_form');
    var $card_form = $('#card_form');
    var $errors_div = $('#errors');
    var $errors_row = $('#errors_row');
    var $success_div = $('#success_div');
    var $success_row = $('#success_row');
    var $location_fieldset = $('#location_fieldset');
    var $card_fieldset = $('#card_fieldset');
    var $storedcard_fieldset = $('#storedcard_fieldset');
    var invoice = $('#payment_div').data('reference');
    var $regions = $('#regions');
    
    
    //Datatables
    var unlinkedBPAYTable = $('#unlinkedBpayTable').DataTable({
        "ajax":{
            "url":'/ledger/payments/api/bpay/transactions.json?sorting=unmatched',
            "dataSrc":""
        },
        "processing":true,
        "columns":[
            {
                data: "crn"
            },
            {
                data: "amount"
            },
            {
                mRender: function(data,type,full){
                    return '<a href="#" data-txn_id="'+full.id+'" class="button float-right bpay_link_btn">LINK</a>';
                }
            }
        ]
    });
    
    var linkedBPAYTable = $('#linkedBpayTable').DataTable({
        "ajax":{
            "url":'/ledger/payments/api/invoices/'+invoice+'/linked_bpay.json',
            "dataSrc":""
        },
        "processing":true,
        "columns":[
            {
                data: "crn"
            },
            {
                data: "amount"
            },
            {
                mRender: function(data,type,full){
                    return '<a href="#" data-txn_id="'+full.id+'" class="button alert round float-right bpay_unlink_btn">UNLINK</a>';
                }
            }
        ]
    });
    // BPAY Buttons
    unlinkedBPAYTable.on('click','.bpay_link_btn',function(e){
        e.preventDefault();
        var txn = $(this).data('txn_id');
        bpay_payment(txn,true,function(){
            unlinkedBPAYTable.ajax.reload();
            linkedBPAYTable.ajax.reload();
        });
        
    });
    linkedBPAYTable.on('click','.bpay_unlink_btn',function(e){
        e.preventDefault();
        var txn = $(this).data('txn_id');
        bpay_payment(txn,false,function(){
            linkedBPAYTable.ajax.reload();
            unlinkedBPAYTable.ajax.reload();
        });
    });
    // Display for the external cash payment feature
    $('#other_external').click('on',function(){
        if (this.checked) {
            $location_fieldset.removeClass('hide');
        }
        else{
            $location_fieldset.addClass('hide');
        }
    });
    // Display for the stored card feature
    $('#use_stored').click('on',function(){
        if (this.checked) {
            $storedcard_fieldset.removeClass('hide');
            $card_fieldset.addClass('hide');
        }
        else{
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
    });
    // Reset Forms
    function reset_forms() {
        $other_form[0].reset();
        $card_form[0].reset();
    }
    // Disable PayButtons
    function disablePayButtons() {
        $('.pay_btn').addClass('disabled');
    }
    // Check if invoice is paid
    function checkInvoiceStatus(){
        var status = '';
        var redirect_url = $('#payment_div').data('redirect');
        $.get('/ledger/payments/api/invoices/'+invoice+'.json',function(resp){
            status = resp.payment_status;
            if (status === 'paid' && redirect_url) {
                window.location.replace(redirect_url);
            }
            updateBanner(status);
        });
    }
    function updateBanner(value) {
        $('#invoice_status').html(value);
        if (!$success_div.hasClass('hide')) {
            setTimeout(function(){$success_div.addClass('hide');},3000);
        }
    }
    /*
     * Update Region Districts
     */
    function updateDistricts(region) {
        $('#dist_wrapper').addClass('hide');
        if (!region) {
            $('#districts').html("");
        }
        else{
            $.get('/ledger/payments/api/regions/'+region+'.json',function(resp){
                var districts = resp.districts;
                $('#districts').html("");
                if (districts.length > 0) {
                    $('#districts').append('<option value="">---- Select District ----</option>');
                    $(districts).each(function(i){
                        $('#districts').append('<option value="'+districts[i].code+'">'+districts[i].name+'</option>');
                    });
                    if (districts.length === 1) {
                        $('#districts').val(districts[0].code);
                    }
                }
            });
            if ($('#dist_wrapper').hasClass('hide')) {
                $('#dist_wrapper').removeClass('hide');
            }
        }
    }
    /*
    * Make cash payments
    */
    function otherPayment(){
        var type,source,payload,ref;
        var amount, orig_txn = null;
        var external = false;
        
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": invoice,
            "type": $('#other_type').val(),
            "source": $('#other_source').val()
        }
        // Check if the amount field is there and has a value
        if ($('#other_amount').val()) {
            payload["amount"] = $('#other_amount').val();
        }
        // Check if the original transaction field is there and has a value
        if ($('#other_orig_txn').val()) {
            payload["orig_txn"] = invoice;
        }
        
        // Check if the external checkbox is selected
        if ($('#other_external').is(':checked')){
            payload['external'] = true;
            payload['region'] = $('#regions').val();
            payload['district'] = $('#districts').val();
            payload['receipt'] = $('#receipt_number').val();
        }
        
        $.post("/ledger/payments/api/cash.json",payload, function(resp){
            success(resp,invoice,$('#other_source').val());
        })
        .fail(function(resp){
            error(resp);
        })
        .always(function(){
            checkInvoiceStatus()
        });
    }
    /*
    *  Make card payments with either stored cards or new cards
    */
    function cardPayment(){
        
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": String(invoice),
            "action": $('#card_action').val(),
            "type": "telephoneorder"
        }
        // Check if amount filed is present and has value has value
        if ($('#card_amount').val()) {
            payload["amount"] = $('#card_amount').val();
        }
        // Check if the pay by stroed cards checkbox is selected
        if ($('#use_stored').is(':checked')){
            payload['using_token'] = true;
            payload['token'] = $('input[name=card]:checked').val();
        }
        else{
            var card= {
                "number": $('#card_number').val(),
                "cvn": $('#card_cvn').val(),
                "expiry": $('#month_expiry').val()+$('#year_expiry').val(),
            }
            payload["card"] = card;
        }
        // POST
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: "/ledger/payments/api/bpoint/payment",
            data: JSON.stringify(payload),
            dataType: "json",
            success: function(resp){
                success(resp,invoice,'card');
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatus();  
            }
        });
    }
    function bpay_payment(txn,link,reload_table){
        // Hide div if not hidden
        if (!$errors_div.hasClass('hide')) {
            $errors_div.addClass('hide');
        }
        // Get payload
        payload = {
            "invoice": String(invoice),
            "link": link,
            "bpay": txn
        }
        
        // POST
        $.ajax ({
            beforeSend: function(xhrObj){
              xhrObj.setRequestHeader("Content-Type","application/json");
              xhrObj.setRequestHeader("Accept","application/json");
            },
            type: "POST",
            url: "/ledger/payments/api/invoices/"+invoice+"/link.json",
            data: JSON.stringify(payload),
            dataType: "json",
            success: function(resp){
                if (!link) {
                    success(invoice,'This BPAY transaction has been unlinked from this invoice.');
                }
                else{
                    success(resp,invoice,'bpay');
                }
                reload_table();
            },
            error: function(resp){
                error(resp);
            },
            complete: function(resp){
                checkInvoiceStatus();  
            }
        });
    }
    /*
     * Display success message
     */
    function success(resp,reference,source){
        var success_str = '';
                         
        success_str = 'Invoice #'+reference+' successfully paid using '+source;
        
        success_html = '<div class="columns small-12"><div class="success callout" data-closable="slide-out-right"> \
            <p class="text-center">'+success_str+'</p> \
        </div></div>';
        
        $success_row.html(success_html);
        $success_div.removeClass('hide');
        if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
        reset_forms();
    }
    function success(reference,msg){
        var success_str = '';
                         
        success_str = msg;
        
        success_html = '<div class="columns small-12"><div class="success callout" data-closable="slide-out-right"> \
            <p class="text-center">'+success_str+'</p> \
        </div></div>';
        
        $success_row.html(success_html);
        $success_div.removeClass('hide');
        if (!$location_fieldset.hasClass('hide')) {
            $location_fieldset.addClass('hide');
        }
        if (!$storedcard_fieldset.hasClass('hide')) {
            $storedcard_fieldset.addClass('hide');
            $card_fieldset.removeClass('hide');
        }
        reset_forms();
    }
    /*
     * Display Error Message
     */
    function error(resp){
        var error_str = '';
        // Show Errors
        if (resp.status === 400) {
            try {
                obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[\[\]"]/g,'');
            } catch(e) {
                error_str = resp.responseText.replace(/[\[\]"]/g,'');
            }
        }
        error_html = '<div class="columns small-12"><div class="alert callout" data-closable="slide-out-right"> \
            <p class="text-center">'+error_str+'</p> \
        </div></div>';
        $errors_row.html(error_html);
        $errors_div.removeClass('hide');
    }
    $other_form.submit(function(e){
        e.preventDefault();
        otherPayment();
    });
    
    $regions.change(function(){
        updateDistricts($(this).val());
    });
    // Reset all forms when page is loaded
    reset_forms();
    /*$card_form.submit(function(e){
        e.preventDefault();
        cardPayment();
    });*/
});