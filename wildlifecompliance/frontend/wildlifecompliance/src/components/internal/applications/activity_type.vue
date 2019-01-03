<template lang="html">
    <div>
      <h3>Activity Name: {{ activity_type.activity_name }} - {{ activity_type.code  }}</h3>
      <p>Applicant: {{ application.applicant }}</p>
      <!--<p>Applicant Details: {{ application.applicant_details }}</p>-->

      <div>
        <input type="text" :name="activity_type.code+'_code'" :value="activity_type.code" style="display:none;"><br>

        <TextField type="text" :name="activity_type.code+'_purpose'" :value="activity_type.purpose" label="Purpose" />
        <TextField type="text" :name="activity_type.code+'_additional_info'" :value="activity_type.additional_info" label="Additional information" />
        <Checkbox :name="activity_type.code+'_standard_advanced'" :value="activity_type.advanced" label="Standard/Advanced" :id="'id_'+activity_type.code+'_standard_advanced'" />

        <TextArea :name="activity_type.code+'_conditions'" :value="activity_type.conditions" label="Conditions" :id="'id_'+activity_type.code+'_conditions'" />

        <DateField :name="activity_type.code+'_issue_date'" :value="activity_type.issue_date" label="Issue Date" :id="'id_'+activity_type.code+'_issue_date'" />
        <DateField :name="activity_type.code+'_start_date'" :value="activity_type.start_date" label="Start Date" :id="'id_'+activity_type.code+'_start_date'" />
        <DateField :name="activity_type.code+'_expiry_date'" :value="activity_type.expiry_date" label="Expiry Date" :id="'id_'+activity_type.code+'_expiry_date'" />

        <Checkbox :name="activity_type.code+'_to_be_issued'" :value="activity_type.to_be_issued" label="To be issued" :id="'id_'+activity_type.code+'_to_be_issued'" />
        <Checkbox :name="activity_type.code+'_processed'" :value="activity_type.processed" label="Processed" :id="'id_'+activity_type.code+'_processed'" />

<!--
        <Radio name="activity_type.code+'_approve'" value="activity_type.approve" label="Approve/Decline" id="'id_'+activity_type.code+'_approve'" :options="activity_type.approve_options" />
        <Radio name="activity_type.code+'_approve'" value="activity_type.approve" label="Approve/Decline" id="'id_'+activity_type.code+'_approve'" :options="activity_type.approve_options" />
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
    import TextField from '@/components/forms/text.vue'
    import TextArea from '@/components/forms/text-area.vue'
    import DateField from '@/components/forms/date-field.vue'
    import Checkbox from '@/components/forms/checkbox.vue'
    import Radio from '@/components/forms/radio.vue'
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
        props:["activity_type", "application", "id"],
        components: {TextField, TextArea, DateField, Checkbox, Radio},
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
        },

        mounted:function () {
            let vm = this;
        }

    }
</script>

<style lang="css" scoped>
</style>

