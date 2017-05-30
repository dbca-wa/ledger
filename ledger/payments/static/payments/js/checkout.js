$(function(){
    var new_card_form = $('#new_card_form');
    var stored_card_form = $('#stored_card_form');
    var mastercard_regex = /^(((222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)\d+)|((5[1-6])\d+))$/;
    var visa_regex = /^[4]{1}\d+$/;
    // Reset Forms
    function reset_forms() {
        if (stored_card_form.length > 0){
            stored_card_form[0].reset();
        }
        new_card_form[0].reset();
        $('#use_stored').prop('checked',false);
    }
    
    $('#use_stored').click('on',function(){
        if (this.checked) {
            if (!new_card_form.hasClass('hide')) {
               new_card_form.addClass('hide');
            }
            if (stored_card_form.hasClass('hide')) {
               stored_card_form.removeClass('hide');
            }
        }
        else{
            if (new_card_form.hasClass('hide')) {
               new_card_form.removeClass('hide');
            }
            if (!stored_card_form.hasClass('hide')) {
               stored_card_form.addClass('hide');
            }
        }
    });
    reset_forms();

    $('#id_number').on('keydown keyup',function(e){
        if(mastercard_regex.test(e.target.value)){
            $('.mastercard').removeClass('disabled');
            $('.visa').addClass('disabled');
        }
        else if (visa_regex.test(e.target.value)){
            $('.mastercard').addClass('disabled');
            $('.visa').removeClass('disabled');
        }
        else{
            $('.mastercard').addClass('disabled');
            $('.visa').addClass('disabled');
        }
    }); 
});
