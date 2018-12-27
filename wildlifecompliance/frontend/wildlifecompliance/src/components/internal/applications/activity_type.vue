<template lang="html">
    <div>
      <h3>Activity Name: {{ activity_type.activity_name }} - {{ activity_type.code  }}</h3>
      <p>Applicant: {{ application.applicant }}</p>
      <!--<p>Applicant Details: {{ application.applicant_details }}</p>-->

      <div>
        <input type="text" :name="activity_type.code+'_code'" :value="activity_type.code" style="display:none;"><br>
        Purpose: <input type="text" :name="activity_type.code+'_purpose'" :value="activity_type.purpose"><br>
        Additional Information: <input type="text" :name="activity_type.code+'_additional_info'" :value="activity_type.additional_info"><br>
        Standard/Advanced: <input type="text" :name="activity_type.code+'_standard_advanced'" :value="activity_type.advanced"><br>
        Conditions: <textarea class="form-control" rows="3" :name="activity_type.code+'_conditions'">{{ activity_type.conditions }}</textarea><br/>
        Issue Date: <input type="date" :name="activity_type.code+'_issue_date'" :value="activity_type.issue_date"><br>
        Start Date: <input type="date" :name="activity_type.code+'_start_date'" :value="activity_type.start_date"><br>
        Expiry Date: <input type="date" :name="activity_type.code+'_expiry_date'" :value="activity_type.expiry_date"><br>

        To Be Issued:
        <select :name="activity_type.code+'_to_be_issued'">
            <option value="" selected disabled hidden>Select ...</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
        </select><br>

        Processed:
        <select :name="activity_type.code+'_processed'">
            <option value="" selected disabled hidden>Select ...</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
        </select>

        <!--
        To Be Issued: <input type="checkbox" :name="activity_type.code+'_to_be_issued'" :value="activity_type.to_be_issued" :checked="isChecked"><br>
        Processed: <input type="checkbox" :name="activity_type.code+'_processed'" :value="activity_type.processed" data-parsley-required :checked="isChecked"><br>
        -->
      </div>

    </div>
</template>

    <!--
    application = models.ForeignKey(Application, related_name='app_activity_types')
    activity_name = models.CharField(max_length=68)
    name = models.CharField(max_length=68)
    short_name = models.CharField(max_length=68)
    data = JSONField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    advanced = models.NullBooleanField('Standard/Advanced', default=None)
    conditions = models.TextField(blank=True, null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    to_be_issued = models.NullBooleanField(default=None)
    processed = models.NullBooleanField(default=None)
    -->


<script>
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
        props:["activity_type", "application", "id"],
        /*
        props:{
            activity_type:{
                type: ,
                required:true
            },
            id:{
                type:Number,
            },

        },
        */
        data:function () {
            return{
                values:null
            }
        },
        methods:{
        },
        computed: {
            isChecked: function() {
                //return (this.value == 'on');
                return (this.activity_type.processed == 'on');
            },
        },

        mounted:function () {
            let vm = this;
            if (vm.isChecked) {
                var input = this.$refs.Checkbox;
                var e = document.createEvent('HTMLEvents');
                e.initEvent('change', true, true);

                /* replacing input.disabled with onclick because disabled checkbox does NOT get posted with form on submit */
                if(vm.readonly) {
                    vm.isClickable = "return false;";
                } else {
                    vm.isClickable = "return true;";
                }
                input.dispatchEvent(e);
            }
        }

    }
</script>

<style lang="css" scoped>
</style>

