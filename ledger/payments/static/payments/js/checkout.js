$(function(){
    $new_card_form = $('#new_card_form');
    $stored_card_form = $('#stored_card_form');
    // Reset Forms
    function reset_forms() {
        $stored_card_form[0].reset();
        $new_card_form[0].reset();
        $('#use_stored').prop('checked',false);
    }
    
    $('#use_stored').click('on',function(){
        if (this.checked) {
            if (!$new_card_form.hasClass('hide')) {
               $new_card_form.addClass('hide');
            }
            if ($stored_card_form.hasClass('hide')) {
               $stored_card_form.removeClass('hide');
            }
        }
        else{
            if ($new_card_form.hasClass('hide')) {
               $new_card_form.removeClass('hide');
            }
            if (!$stored_card_form.hasClass('hide')) {
               $stored_card_form.addClass('hide');
            }
        }
    });
    reset_forms();
});