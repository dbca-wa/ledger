<template lang="html">
    <span>
        <div v-if="component.type === 'tab'">
            <renderer-block v-for="(subcomponent, index) in component.children"
                :component="subcomponent"
                :json_data="value"
                v-bind:key="`subcomponent_${index}`"
                />
        </div>

        <FormSection v-if="component.type === 'section'"
            :label="component.label" :Index="component.name" :id="component.name">
                <renderer-block v-for="(subcomponent, index) in component.children"
                    :component="subcomponent"
                    :json_data="value"
                    v-bind:key="`section_${index}`"
                    />
        </FormSection>

        <Group v-if="component.type === 'group'"
            :label="component.label"
            :name="component.name"
            :id="element_id()"
            :help_text="help_text"
            :help_text_url="help_text_url"
            :isRemovable="true">
                <renderer-block v-for="(subcomponent, index) in component.children"
                    :component="subcomponent"
                    :json_data="value"
                    v-bind:key="`group_${index}`"
                    />
        </Group>

        <TextField v-if="component.type === 'text'"
            type="text"
            :name="component.name"
            :value="value"
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
            :name="component.name"
            :value="value"
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
            :name="component.name"
            :value="value"
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
                :name="component.name"
                :label="component.label"
                :value="value"
                :id="element_id()"
                :comment_value="comment_value"
                :options="component.options"
                :help_text="help_text"
                :handleChange="handleComponentChange(component)"
                :conditions="component.conditions"
                :isRequired="component.isRequired"
                :help_text_url="help_text_url"/>
                
                <SelectConditions
                    :conditions="component.conditions" 
                    :name="component.name"
                    :data="json_data"
                    :id="element_id(1)"
                    :readonly="is_readonly" 
                    :isRequired="component.isRequired"/>
        </div>

        <SelectBlock v-if="component.type === 'multi-select'"
            :name="component.name"
            :label="component.label"
            :value="value"
            :id="element_id()"
            :comment_value="comment_value"
            :options="component.options"
            :help_text="help_text"
            :handleChange="handleComponentChange(component)"
            :readonly="is_readonly"
            :isMultiple="true"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <TextAreaBlock v-if="component.type === 'text_area' || component.type === 'text-area'"
            :readonly="is_readonly"
            :name="component.name"
            :value="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <Table v-if="component.type === 'table'"
            :headers="component.headers"
            :readonly="is_readonly"
            :name="component.name"
            :value="value"
            :id="element_id()"
            :comment_value="comment_value"
            :label="component.label"
            :help_text="help_text"
            :isRequired="component.isRequired"
            :help_text_url="help_text_url"/>

        <Label v-if="component.type === 'label'"
            :value="component.label"
            :id="element_id()"/>

        <div class="form-group" v-if="component.type === 'radiobuttons'">
            <label :id="element_id()" class="inline">{{component.label}}</label>
                <HelpText :help_text="help_text"/>
                <HelpTextUrl :help_text_url="help_text_url"/>
                <CommentRadioCheckBox
                    :name="component.name"
                    :comment_value="comment_value"
                    :label="component.label"/>

                <Radio v-for="(option, index) in component.options"
                    :name="component.name"
                    :label="option.label"
                    :value="option.value"
                    :isRequired="option.isRequired || component.isRequired"
                    :id="element_id(1)"
                    :savedValue="value"
                    :handleChange="handleComponentChange(component)"
                    :conditions="component.conditions"
                    :readonly="is_readonly"
                    v-bind:key="`radio_${component.name}_${index}`"/>
 
                <Conditions
                    :conditions="component.conditions"
                    :name="component.name"
                    :data="json_data"
                    :id="element_id(2)"
                    :readonly="is_readonly"/>
        </div>

        <div class="form-group" v-if="component.type === 'checkbox'">
            <Checkbox
                :group="component.group"
                :name="component.name"
                :label="component.label"
                :id="element_id(1)"
                :help_text="help_text"
                :help_text_url="help_text_url"
                :value="value"
                :handleChange="handleComponentChange(component)"
                :conditions="component.conditions"
                :readonly="is_readonly"
                :isRequired="component.isRequired"/>
            <Conditions
                :conditions="component.conditions"
                :name="component.name"
                :data="json_data"
                :id="element_id(2)"
                :isRequired="component.isRequired"/>
        </div>

        <div class="form-group" v-if="component.type === 'declaration'">
            <label>{{component.label}}</label>
            <Checkbox
                :name="component.name"
                :label="component.label"
                :value="value"
                :help_text="component.help_text"
                :handleChange="handleComponentChange(component)"
                :conditions="component.conditions"/>
            <Conditions
                :conditions="component.conditions"
                :name="component.name"
                :data="value"/>
        </div>

        <File v-if="component.type === 'file'"
            :name="component.name"
            :label="component.label"
            :value="value"
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
            :name="component.name"
            :label="component.label"
            :value="value"
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
import Label from '@/components/forms/label.vue'
import AssessorText from '@/components/forms/readonly_text.vue'
import HelpText from '@/components/forms/help_text.vue'
import HelpTextUrl from '@/components/forms/help_text_url.vue'
import CommentRadioCheckBox from '@/components/forms/comment_icon_checkbox_radio.vue'
import Table from '@/components/forms/table.vue'

const RendererBlock = {
  name: 'renderer-block',
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
  },
  data: function() {
    return {
    }
  },
  props:{
      component: {
          type: Object,
          required: true
      },
      json_data: {
          type: Object | null,
          required: true
      }
  },
  computed: {
    ...mapGetters([
        'application',
        'application_id',
        'isComponentVisible',
    ]),
    is_readonly: function() {
        return this.component.readonly ? this.component.readonly : this.application.readonly;
    },
    comment_data: function() {
        return this.application.comment_data;
    },
    documents_url: function() {
        return this.application.documents_url;
    },
    can_user_edit: function() {
        return this.application.can_user_edit;
    },
    site_url: function() {
        return (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/");
    },
    value: function() {
        if(this.json_data == null || this.json_data[this.component.name] == null) {
            return null;
        }
        return this.json_data[this.component.name].constructor === Array ?
            this.json_data[this.component.name][0] : this.json_data[this.component.name];
    },
    comment_value: function() {
        if(this.comment_data == null || this.comment_data[this.component.name] == null) {
            return null;
        }
        return this.comment_data[this.component.name];
    },
    help_text: function() {
        return this.replaceSitePlaceholders(this.component.help_text);
    },
    help_text_url: function() {
        return this.replaceSitePlaceholders(this.component.help_text_url);
    },
  },
  methods: {
    ...mapActions([
        'toggleVisibleComponent'
    ]),
    strToBool: strToBool,
    element_id: function(depth=0) {
        return 'id_' + this.component.name + ((depth) ? `_${depth}` : '');
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
    handleComponentChange: function(component) {
        return (e) => {
            for(let condition in component.conditions) {
                this.toggleVisibleComponent({
                    'component_id': `cons_${component.name}_${condition}`,
                    'visible': false
                });
            }
            this.toggleVisibleComponent({
                'component_id': `cons_${e.target.name}_${e.target.value}`,
                'visible': e.target.checked
            });
        }
    },
  },
}

export default RendererBlock;
</script>
