import FormSection from '../components/forms/section.vue'
import Group from '../components/forms/group.vue'
import Group2 from '../components/forms/group2.vue'
import Radio from '../components/forms/radio.vue'
import Conditions from '../components/forms/conditions.vue'
import SelectConditions from '../components/forms/select-conditions.vue'
import Checkbox from '../components/forms/checkbox.vue'
import Declaration from '../components/forms/declarations.vue'
import File from '../components/forms/file.vue'
import Select from '../components/forms/select.vue'
import DateField from '../components/forms/date-field.vue'
import TextField from '../components/forms/text.vue'
import TextArea from '../components/forms/text-area.vue'
import Label from '../components/forms/label.vue'
import AssessorText from '../components/forms/readonly_text.vue'
import HelpText from '../components/forms/help_text.vue'
import HelpTextUrl from '../components/forms/help_text_url.vue'
import CommentRadioCheckBox from '../components/forms/comment_icon_checkbox_radio.vue'
import Table from '../components/forms/table.vue'
import { helpers, api_endpoints } from "@/utils/hooks.js"
import { strToBool } from "@/utils/helpers.js";

module.exports = {
    renderChildren(h,c,data=null,_readonly) {
        const is_readonly = this.status_data.readonly;
        const commentData = this.status_data.commentData;
        const applicationId = this.status_data.applicationId;
        const application = this.status_data.application;
        var readonly = false;
        var _elements = [];

        var site_url = (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/");

        // Visibility
        var visibility = this.getVisibility(h,c,is_readonly)
        if (!visibility.visible){ return "" }

        // Editablility
        readonly = !visibility.editable;

        var val = (data) ? (data[c.name]) ? data[c.name] : null : null;
        var comment_val = (commentData) ? (commentData[c.name]) ? commentData[c.name] : null : null;

        if (c && c.help_text && c.help_text.indexOf("site_url:/") >= 0) {
            var help_text = c.help_text.replace('site_url:/', site_url);
            if (help_text.indexOf("anchor=") >= 0) {
                help_text = help_text.replace('anchor=', "#");
            }
        } else {
            var help_text = c.help_text;
        }

        // repeat for help_text_url
        if (c && c.help_text_url && c.help_text_url.indexOf("site_url:/") >= 0) {
            var help_text_url = c.help_text_url.replace('site_url:/', site_url);
            if (help_text_url.indexOf("anchor=") >= 0) {
                help_text_url = help_text_url.replace('anchor=', "#");
            }
        } else {
            var help_text_url = c.help_text_url;
        }

        var id = 'id_' + c.name;
        var id1 = id + '_1'
        var id2 = id + '_2'
        var id3 = id + '_3'

        switch (c.type) {
            case 'text':
                readonly = (c.readonly) ? (c.readonly): (readonly);
                _elements.push(
                    <TextField type="text" name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} readonly={readonly} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'number':
                _elements.push(
                    <TextField type="number" name={c.name} value={val} id={id} min={c.min} max={c.max} comment_value={comment_val} label={c.label} help_text={help_text} readonly={readonly} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'email':
                _elements.push(
                    <TextField type="email" name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} readonly={readonly} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'select':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div>
                        <Select readonly={readonly} name={c.name} label={c.label} value={c.value} id={id} comment_value={comment_val} options={c.options} help_text={help_text} value={val} handleChange={this.selectionChanged}  conditions={c.conditions} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                        <SelectConditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id1} readonly={readonly} isRequired={c.isRequired}/>
                    </div>
                )
                break;
            case 'multi-select':
                _elements.push(
                    <Select name={c.name} label={c.label} value={val} id={id} comment_value={comment_val} options={c.options} value={val} help_text={help_text} handleChange={this.selectionChanged} readonly={readonly} isMultiple={true} isRequired={c.isRequired} help_text_url={help_text_url} />
                )
                break;
            case 'text_area':
                _elements.push(
                    <TextArea readonly={readonly} name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'table':
                _elements.push(
                    <Table headers={c.headers} readonly={readonly} name={c.name} value={val} id={id} comment_value={comment_val} label={c.label} help_text={help_text} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'label':
                _elements.push(
                    <Label value={c.label} id={id} />
                )
                break;
            case 'radiobuttons':
            var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div class="form-group">
                        <label id={id} class="inline">{c.label}</label>
                            <HelpText help_text={help_text}/>
                            <HelpTextUrl help_text_url={help_text_url}/>
                            <CommentRadioCheckBox name={c.name} comment_value={comment_val} label={c.label} renderer={this}/>
                            {c.options.map(op =>{
                                return(
                                    <Radio name={c.name} label={op.label} value={op.value} isRequired={op.isRequired || c.isRequired} id={id1} savedValue={val} handleChange={this.handleRadioChange} conditions={c.conditions} readonly={readonly}/>
                                )
                            })}
                            <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id2} readonly={readonly}/>
                    </div>
                )
                break;
            case 'group':
                var value = null;
                var isRepeatable = c.hasOwnProperty("isRepeatable");
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                var postfix = 0;
                _elements.push(
                    <Group label={c.label} name={c.name} id={id} help_text={help_text} help_text_url={help_text_url} isRemovable={true}>
                        {c.children.map(c=>{
                            return (
                                <div>
                                    {this.renderChildren(h,c,value)}
                                </div>
                            )
                        })}
                    </Group>
                )
                break;
            case 'group2':
                // still experimental
                var value = null;
                var isRepeatable = c.hasOwnProperty("isRepeatable");
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                var postfix = 0;
                _elements.push(
                    <Group2 label={c.label} name={c.name} id={id} help_text={help_text} help_text_url={help_text_url} isRemovable={true} isRepeatable={c.isRepeatable} repeatable_children={c.children} renderer={this}>
                        {c.children.map(d=>{
                            return (
                                <div>
                                    {this.renderChildren(h,d,value)}
                                </div>
                            )
                        })}
                    </Group2>
                )
                break;


            case 'section':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                this.sections.push({name:c.name,label:c.label});
                _elements.push(
                    <FormSection label={c.label} Index={c.name} id={c.name}>
                        {c.children.map(d=>{
                            return (
                                <div>
                                    {this.renderChildren(h,d,value)}
                                </div>
                            )
                        })}
                    </FormSection>

                )
                break;
            case 'tab':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                if(this.tabs_list.length>0){
                     _elements.push(
                        <div class="tab-pane fade" id={c.id}>
                            {c.children.map(d=>{
                                return (
                                    <div>
                                        {this.renderChildren(h,d,value)}
                                    </div>
                                )
                            })}
                        </div>
                    )
                }else{
                     _elements.push(
                        <div class="tab-pane fade in active" id={c.id}>
                            {c.children.map(d=>{
                                return (
                                    <div>
                                        {this.renderChildren(h,d,value)}
                                    </div>
                                )
                            })}
                        </div>
                    )
                }
                this.tabs_list.push({name:c.name,label:c.label,id:c.id});
                break;
            case 'checkbox':
                _elements.push(
                    <div class="form-group">
                        <Checkbox group={c.group} name={c.name} label={c.label} id={id1} help_text={help_text} help_text_url={help_text_url} value={val} handleChange={this.handleCheckBoxChange} conditions={c.conditions} readonly={readonly} isRequired={c.isRequired}/>
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data} id={id2} isRequired={c.isRequired}/>
                    </div>
                )
                break;
            case 'declaration':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name] : null ;
                }
                _elements.push(
                    <div class="form-group">
                        <label>{c.label}</label>
                        <Checkbox name={c.name} label={c.label} value={val} help_text={c.help_text} handleChange={this.handleCheckBoxChange} conditions={c.conditions} />
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={value}/>
                    </div>
                )
                break;
            case 'file':
                _elements.push(
                    <File name={c.name} label={c.label} value={val} id={id} comment_value={comment_val} isRepeatable={strToBool(c.isRepeatable)} handleChange={this.handleFileChange} readonly={readonly} help_text={help_text} docsUrl={this.status_data.docs_url} readonly={readonly} application_id={applicationId} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            case 'date':
                _elements.push(
                    <DateField name={c.name} label={c.label} value={val} id={id} comment_value={comment_val}  handleChange={this.handleFileChange} readonly={readonly} help_text={help_text} isRequired={c.isRequired} help_text_url={help_text_url} renderer={this}/>
                )
                break;
            default:
            return "";
        }
        return _elements;
    },
    handleRadioChange(e){
        var conditions = $(e.target).data('conditions');
        if (conditions && conditions !== undefined) {
            var cons = Object.keys(conditions);
            var btns = $('input[name='+e.target.name+']');
            $.each(btns,function (i,input) {
                $("#cons_"+e.target.name+'_'+input.value).addClass('hidden');
            });
            $("#cons_"+e.target.name+'_'+e.target.value).removeClass('hidden');
        }
    },
    handleCheckBoxChange(e){
        var conditions = $(e.target).data('conditions');
        if (conditions && conditions !== undefined) {
            var cons = Object.keys(conditions);
            var btns = $('input[name='+e.target.name+']');
            $.each(btns,function (i,input) {
                $("#cons_"+e.target.name+'_'+input.value).addClass('hidden');
            });
            if(e.target.checked){
                $("#cons_"+e.target.name+'_'+e.target.value).removeClass('hidden');
            }
        }

    },
    handleDeclaration(e){
        return true;
    },
    selectionChanged(target){
        var conditions = $(target).data('conditions');

        if (conditions) {
            var cons = Object.keys(conditions);
            for (var i = 0; i < cons.length; i++) {
                if (cons[i] == target.value) {
                    $("#cons_"+target.name+'_'+target.value).removeClass('hidden');
                }else{
                    $("#cons_"+target.name+'_'+cons[i]).addClass('hidden');
                }
            }
        }
    },
    getSections(){
        return this.sections;
    },
    sections:[],
    tabs_list:[],
    getTabslist(){
        return this.tabs_list;
    },
    status_data : {},
    store_status_data(readonly, commentData, can_user_edit, docs_url, applicationId, application){
        this.status_data = {
            'readonly': readonly,
            'commentData': commentData,
            'can_user_edit': can_user_edit,
            'docs_url': docs_url,
            'applicationId': applicationId,
            'application': application,
        }
    },
    getVisibility(h,c,readonly){
        var _status = {
            'visible':true,
            'editable':true
        }
        _status.editable = readonly ? false : true;
        return _status;
    },
    canViewComments: function() {
        return this.userHasRole('licensing_officer');
    },
    userHasRole: function(role, activity_id) {
        if(this.status_data.application === undefined || this.status_data.application === null) {
            return false;
        }
        const user_roles = this.status_data.application.user_roles;
        if(user_roles === undefined || user_roles === null) {
            return false;
        }
        return this.status_data.application.user_roles.filter(
            role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
        ).length;
    },
}
