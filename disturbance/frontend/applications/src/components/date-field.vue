<template lang="html">
    <div class="form-group">
        <label>{{ label }}</label>
        <div class='input-group date'>
            <input :name="name" class="form-control" placeholder="DD/MM/YYYY" :value="value"/>
            <span class="input-group-addon">
                <span class="glyphicon glyphicon-calendar"></span>
            </span>
        </div>
        <p class="help-block">{{ help_text }}</p>
    </div>
</template>

<script>
import moment from 'moment'
import datetimepicker from 'datetimepicker'
export default {
    props:['name','label','help_text','value','conditions',"handleChange"],
    computed:{
        isChecked:function () {
            //TODO return value from database
            return false;
        },
        options:function () {
            return JSON.stringify(this.conditions);
        }
    },
    mounted:function () {
        $('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }
}
</script>

<style lang="css">
</style>
