<template lang="html" :id="id">
<div>
    <div class="row">
                <fieldset class="scheduler-border">
                    <legend class="scheduler-border">{{accreditation.accreditation_type_value}}</legend>
                    <div class="form-group">
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-right"  for="Name">Expiry Date</label>
                            </div>
                            <div class="col-sm-9">
                                <div class="input-group date" ref="accreditation_expiry" style="width: 70%;">
                                    <input type="text" class="form-control" v-model="accreditation.accreditation_expiry" name="accreditation_expiry" placeholder="DD/MM/YYYY" :disabled="readonly">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-right"  for="Name">Accreditation certificates</label>
                            </div>
                            <div class="col-sm-9">
                                <FileField :proposal_id="proposal_id" isRepeatable="false" :name="'accreditation'+accreditation.accreditation_type" :id="'accreditation'+accreditation_type+proposal_id" :readonly="readonly"></FileField>
                            </div>
                        </div>
                        <div  v-if="typeOther"class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-right"  for="Name">Details</label>
                            </div>
                            <div class="col-sm-9">
                                <div class="" ref="accreditation_comments" style="width: 70%;">
                                    <input type="textarea" class="form-control" v-model="accreditation.comments" name="accreditation_comments" :disabled="readonly">        
                                </div>
                            </div>
                        </div>
                    </div>
                </fieldset>
            </div>  
</div>
</template>

<script>
import FileField from '@/components/forms/filefield.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

export default {
    name:"accreditation",
    props:{
        proposal_id: null,
        accreditation: {
                type: Object,
                required:true
            },
        id:String,
        assessor_readonly: Boolean,
        assessorMode:{
            default:function(){
                return false;
            }
        },
        value:{
            default:function () {
                return null;
            }
        },
        readonly:Boolean,
    },
    components: {
        FileField,
    },
    data:function(){
        return {
            repeat:1,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
        }
    },

    computed: {
        typeOther: function(){
            return this.accreditation && this.accreditation.accreditation_type=='other' ? true: false;
        }
    },

    methods:{
        eventListeners:function (){
            let vm=this;
                $(vm.$refs.accreditation_expiry).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.accreditation_expiry).on('dp.change', function(e){
                    if ($(vm.$refs.accreditation_expiry).data('DateTimePicker').date()) {
                        vm.accreditation.accreditation_expiry =  e.date.format('DD/MM/YYYY');
                    }
                    else if ($(vm.$refs.accreditation_expiry).data('date') === "") {
                        vm.accreditation.accreditation_expiry = null;
                    }
                 });
        },
    },
    mounted:function () {
        let vm = this;
        this.$nextTick(()=>{
                vm.eventListeners();
            });
    }
}

</script>

<style lang="css">
    fieldset.scheduler-border {
        border: 1px groove #ddd !important;
        padding: 0 1.4em 1.4em 1.4em !important;
        margin: 0 0 1.5em 0 !important;
        -webkit-box-shadow:  0px 0px 0px 0px #000;
                box-shadow:  0px 0px 0px 0px #000;
    }
    legend.scheduler-border {
        width:inherit; /* Or auto */
        padding:0 10px; /* To give a bit of padding on the left and right */
        border-bottom:none;
    }
</style>
