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
        <!--<Checkbox :name="activity_type.code+'_processed'" :value="activity_type.processed" label="Processed" :id="'id_'+activity_type.code+'_processed'" />-->

        <!-- Add isEditable fields to form and allow values to be overridden (original data is NOT overwritten) -->
        <div v-for="editable_element in editable_elements">
            <div v-if="'table' in editable_element">
                <Table :name="activity_type.code+'_table_'+editable_element.table.name" :value="editable_element.table.value" :label="editable_element.table.label" :headers="editable_element.table.headers"/>
            </div>
            <div v-else-if="'text' in editable_element">
                <TextField type="text" :name="activity_type.code+'_text_'+editable_element.text.name" :value="editable_element.text.value" :label="editable_element.text.label" />
            </div>
            <div v-else-if="'text_area' in editable_element">
                <TextArea :name="activity_type.code+'_text_area_'+editable_element.text_area.name" :value="editable_element.text_area.value" :label="editable_element.text_area.label" />
            </div>
            <!--{{ editable_element }}-->
        </div>

        <!-- https://medium.freecodecamp.org/an-introduction-to-dynamic-list-rendering-in-vue-js-a70eea3e321 -->
<!--
        <Table v-for="editable_element in render_editable_elements()" :name="editable_element['']"/>
-->

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
    import Table from '@/components/forms/table.vue'
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
        props:["activity_type", "application", "id"],
        components: {TextField, TextArea, DateField, Checkbox, Radio, Table},
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
            let vm = this;
            vm.editable_elements = [];

            if ('editable' in vm.activity_type.data[0]) {
                var data = vm.activity_type.data[0]['editable'];
                for (var k in data) {
                    if (data[k]['type'] == 'table') {
                        vm.editable_elements.push({'table': {
                                name: k,
                                value: data[k]['answer'],
                                label: data[k]['label'],
                                headers: data[k]['headers'],
                            }
                        })
                    } else if (data[k]['type'] == 'text') {
                        vm.editable_elements.push({'text': {
                                name: k,
                                value: data[k]['answer'],
                                label: data[k]['label'],
                            }
                        })
                    } else if (data[k]['type'] == 'text_area') {
                        vm.editable_elements.push({'text_area': {
                                name: k,
                                value: data[k]['answer'],
                                label: data[k]['label'],
                            }
                        })
                    }
                }
            }
            console.log(vm.editable_elements);

            return{
                values:null
            }
        },
        methods:{
            render_editable_elements: function() {
                let vm = this;
                var _elements = [];
                if ('editable' in vm.activity_type.data[0]) {
                    var data = vm.activity_type.data[0]['editable'];
                    for (var k in data) {
                        if (data[k]['type'] == 'table') {
                            var section_name = k;
                            var value = data[k]['answer'];
                            var label = data[k]['label'];
                            //_elements.push(
                            //    //<TextArea readonly={readonly} name={k} value={data[k]['answer']} label={data[k]['label']} />
                            //    "<Table name='"+ section_name +"' value='"+ value +"' label='"+ label +"' />"
                            //)
                            vm.element = {
                                    type: 'table',
                                    name: section_name,
                                    value: value,
                                    label: label
                            }


                        }
                    }
                }
                return _elements;
            },
            /*
            process: function(e) {
                let vm = this;
                vm.form = document.forms.new_application;
                let formData = new FormData(vm.form);
                formData.append('action', 'process');
                vm.$http.post(vm.application_form_url,formData).then(res=>{
                  swal(
                    'Processed',
                    'Your application has been processed',
                    'success'
                  )
                },err=>{
                });
            },
            */
        },
        computed: {
            application_iseditable_url: function() {
              return (this.application) ? `/api/application/${this.application.id}/is_editable_data.json` : '';
            },
        },

        mounted:function () {
            let vm = this;
        }

    }
</script>

<style lang="css" scoped>
</style>

