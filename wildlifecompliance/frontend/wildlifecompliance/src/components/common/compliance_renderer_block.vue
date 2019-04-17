<template lang="html">
    <span>
        <div v-if="component.type === 'tab'">
            <compliance-renderer-block v-for="(subcomponent, index) in component.children"
                :component="subcomponent"
                :instance="instance"
                v-bind:key="`subcomponent_${index}`"
                />
        </div>

        <FormSection v-if="component.type === 'section'"
            :label="component.label" :Index="component_name" :id="component_name">
                <compliance-renderer-block v-for="(subcomponent, index) in component.children"
                    :component="subcomponent"
                    :instance="instance"
                    v-bind:key="`section_${index}`"
                    />
        </FormSection>

        <Group v-if="component.type === 'group'"
            :label="component.label"
            :name="component_name"
            :id="element_id()"
            :help_text="help_text"
            :help_text_url="help_text_url"
            :isRemovable="true">
                <compliance-renderer-block v-for="(subcomponent, index) in component.children"
                    :component="subcomponent"
                    :instance="instance"
                    v-bind:key="`group_${index}`"
                    />
        </Group>

        <TextField v-if="component.type === 'text'"
            type="text"
            :name="component_name"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :readonly="is_readonly"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TextField v-if="component.type === 'string'"
            type="string"
            :name="component.name"
            :value="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :readonly="is_readonly"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TextField v-if="component.type === 'number'"
            type="number"
            :name="component_name"
            :field_data="value"
            :id="element_id()"
            :min="component.min"
            :max="component.max"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :readonly="is_readonly"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TextField v-if="component.type === 'email'"
            type="email"
            :name="component_name"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :readonly="is_readonly"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <div v-if="component.type === 'select'">
            <SelectBlock
                :readonly="is_readonly"
                :name="component_name"
                :label="component.label"
                :field_data="value"
                :id="element_id()"
                :comment_value="comment_value"
                :options="component.options"
                :help_text="help_text"
                :handleChange="handleComponentChange(component, true)"
                :conditions="component.conditions"
                :isRequired="component.isRequired"
                :help_text_url="help_text_url"/>
                
                <SelectConditions
                    :conditions="component.conditions" 
                    :name="component_name"
                    :data="json_data"
                    :id="element_id(1)"
                    :readonly="is_readonly" 
                    :isRequired="component.isRequired"/>
        </div>

        <SelectBlock v-if="component.type === 'multi-select'"
            :name="component_name"
            :label="component.label"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :options="component.options"
            :help_text="help_text"
            :handleChange="handleComponentChange(component, false)"
            :readonly="is_readonly"
            :isMultiple="true"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TextAreaBlock v-if="component.type === 'text_area'"
            :readonly="is_readonly"
            :name="component_name"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TableBlock v-if="component.type === 'table'"
            :headers="component.headers"
            :readonly="is_readonly"
            :name="component_name"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <ExpanderTable v-if="component.type === 'expander_table'"
            :json_data="value"
            :readonly="is_readonly"
            :name="component_name"
            :component="component"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <LabelBlock v-if="component.type === 'label'"
            :value="component.label"
            :id="element_id()"/>

        <div class="form-group" v-if="component.type === 'radiobuttons'">
            <label :id="element_id()" class="inline">{{component.label}}</label>
                <HelpText :help_text="help_text"/>
                <HelpTextUrl :help_text_url="help_text_url"/>
                <CommentRadioCheckBox
                    :name="component_name"
                    :comment_value="comment_value"
                    :label="component.label"/>

                <Radio v-for="(option, index) in component.options"
                    :name="component_name"
                    :label="option.label"
                    :value="option.value"
                    :isRequired="option.isRequired || component.isRequired"
                    :id="element_id(1)"
                    :savedValue="value"
                    :handleChange="handleComponentChange(component)"
                    :conditions="component.conditions"
                    :readonly="is_readonly"
                    v-bind:key="`radio_${component_name}_${index}`"/>
 
                <Conditions
                    :conditions="component.conditions"
                    :name="component_name"
                    :instance="instance"
                    :data="json_data"
                    :id="element_id(2)"
                    :readonly="is_readonly"/>
        </div>

        <div class="form-group" v-if="component.type === 'checkbox'">
            <Checkbox
                :group="component.group"
                :name="component_name"
                :label="component.label"
                :id="element_id(1)"
                :help_text="help_text"
                :help_text_url="help_text_url"
                :field_data="value"
                :handleChange="handleComponentChange(component)"
                :conditions="component.conditions"
                :readonly="is_readonly"
                :isRequired="component.isRequired"/>
            <Conditions
                :conditions="component.conditions"
                :name="component_name"
                :instance="instance"
                :data="json_data"
                :id="element_id(2)"
                :isRequired="component.isRequired"/>
        </div>

        <div class="form-group" v-if="component.type === 'declaration'">
            <label>{{component.label}}</label>
            <Checkbox
                :name="component_name"
                :label="component.label"
                :field_data="value"
                :help_text="component.help_text"
                :handleChange="handleComponentChange(component)"
                :conditions="component.conditions"/>
            <Conditions
                :conditions="component.conditions"
                :name="component_name"
                :instance="instance"
                :data="value"/>
        </div>

        <File v-if="component.type === 'file'"
            :name="component_name"
            :label="component.label"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :isRepeatable="strToBool(component.isRepeatable)"
            :readonly="is_readonly"
            :help_text="help_text"
            :docsUrl="documents_url"
            :application_id="application_id"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <DateField v-if="component.type === 'date'"
            :name="component_name"
            :label="component.label"
            :field_data="value"
            :id="element_id()"
            :comment_value="comment_value"
            :readonly="is_readonly"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

    </span>
</template>


<script>
import Vue from 'vue';
import { mapActions, mapGetters } from 'vuex';
import { helpers, api_endpoints } from "@/utils/hooks.js"
import { strToBool } from "@/utils/helpers.js";

import FormSection from '@/components/forms/section.vue'
import Group from '@/components/forms/group.vue'
import Radio from '@/components/forms/radio.vue'
import Conditions from '@/components/forms/conditions.vue'
import SelectConditions from '@/components/forms/select-conditions.vue'
import Checkbox from '@/components/forms/checkbox.vue'
import Declaration from '@/components/forms/declarations.vue'
import File from '@/components/forms/file.vue'
import SelectBlock from '@/components/forms/select.vue'
import DateField from '@/components/forms/date-field.vue'
import TextField from '@/components/forms/text.vue'
import TextAreaBlock from '@/components/forms/text-area.vue'
import LabelBlock from '@/components/forms/label.vue'
import AssessorText from '@/components/forms/readonly_text.vue'
import HelpText from '@/components/forms/help_text.vue'
import HelpTextUrl from '@/components/forms/help_text_url.vue'
import CommentRadioCheckBox from '@/components/forms/comment_icon_checkbox_radio.vue'
import TableBlock from '@/components/forms/table.vue'
import ExpanderTable from '@/components/forms/expander_table.vue'

const ComplianceRendererBlock = {
  name: 'compliance-renderer-block',
  components: {
      FormSection,
      TextField,
      Group,
      SelectBlock,
      SelectConditions,
      HelpText,
      HelpTextUrl,
      CommentRadioCheckBox,
      Radio,
      Conditions,
      Checkbox,
      File,
      DateField,
      TextAreaBlock,
      LabelBlock,
      TableBlock,
      ExpanderTable,
  },
  data: function() {
    return {
        //renderer_form_data: {field1: "text"},
        //isComponentVisible: true,
    }
  },
  props:{
      component: {
          type: Object,
          required: true
      },
      instance: {
          type: String,
          default: null
      }
  },
  computed: {
    ...mapGetters({
        call_email: 'callemailStore/call_email',
        call_email_id: 'callemailStore/call_email_id',
        //'application',
        //'application_id',
        renderer_form_data: 'complianceRendererStore/renderer_form_data',
        isComponentVisible: 'complianceRendererStore/isComponentVisible',
    }),
    
    is_readonly: function() {
        return this.component.readonly ? this.component.readonly : null;
    },
    
    comment_data: function() {
        return this.call_email.comment_data;
    },
    documents_url: function() {
        return this.call_email.documents_url;
    },
    can_user_edit: function() {
        return this.call_email.can_user_edit;
    },
    
    site_url: function() {
        return (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/");
    },
    component_name: function() {
        return `${this.component.name}${this.instance !== null ? `__instance-${this.instance}`: ''}`;
    },
    
    json_data: function() {
        console.log(this);
        return this.renderer_form_data;
    },
    value: {
        get: function() {
            if(this.json_data == null) {
                return this.json_data;
            }
            if(this.json_data[this.component_name] == null) {
                this.setFormValue({
                    key: this.component_name,
                    value: {
                        "value": '',
                        "schema_name": this.component.name,
                        "component_type": this.component.type
                    }
                });
            }
            return this.json_data[this.component_name];
        },
        set: function(value) {
            this.setFormValue({
                key: this.component_name,
                value: { "value": value }
            });
        }
    },
    
    comment_value: function() {
        if(this.comment_data == null || this.comment_data[this.component_name] == null) {
            return null;
        }
        return this.comment_data[this.component_name];
    },
    help_text: function() {
        return this.replaceSitePlaceholders(this.component.help_text);
    },
    help_text_url: function() {
        return this.replaceSitePlaceholders(this.component.help_text_url);
    },
  },
  methods: {
    ...mapActions({
        toggleVisibleComponent: 'complianceRendererStore/toggleVisibleComponent',
        setFormValue: 'complianceRendererStore/setFormValue',
        updateFormField: 'complianceRendererStore/updateFormField',
    }),
    strToBool: strToBool,
    element_id: function(depth=0) {
        return `id_${this.component_name}${(depth) ? `_${depth}` : ''}${this.instance !== null ? `__instance${this.instance}`: ''}`;
    },
    
    replaceSitePlaceholders: function(text_string) {
        if(text_string && text_string.includes("site_url:/")) {
            text_string = text_string.replace('site_url:/', this.site_url);

            if (text_string.includes("anchor=")) {
                text_string = text_string.replace('anchor=', "#");
            }
        }
        return text_string;
    },
    /*
    handleComponentChange: function(component, assignEventValue=true) {
        return (e) => {
            for(let condition in component.conditions) {
                this.toggleVisibleComponent({
                    'component_id': `cons_${this.component_name}_${condition}`,
                    'visible': false
                });
            }
            e.target && this.toggleVisibleComponent({
                'component_id': `cons_${e.target.name}_${e.target.value}`,
                'visible': e.target.checked
            });
            const value = e.value == null ? e.target.value : e.value;
            if(assignEventValue && value != null) {
                this.value =value;
            }
        }
    },
    */
  }
}

export default ComplianceRendererBlock;
</script>
