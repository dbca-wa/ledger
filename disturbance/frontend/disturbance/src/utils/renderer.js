import Section from '../components/forms/section.vue'
import Group from '../components/forms/group.vue'
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
import AssessorText from '../components/forms/readonly_text.vue'
import HelpText from '../components/forms/help_text.vue'

module.exports = {
    renderChildren(h,c,data=null,assessorData=null,_readonly) {
        var is_readonly = this.status_data.readonly;
        var assessorStatus = this.status_data.assessorStatus;
        var assessorData = this.status_data.assessorData;
        var assessorInfo = this.status_data.assessorInfo;
        var assessorMode = false; 
        var assessorCanAssess = false; 
        var assessorLevel = '';
        var readonly = false;
        var _elements = [];
        if (assessorStatus != null){
            assessorMode = assessorStatus['assessor_mode'];
            assessorCanAssess = assessorStatus['assessor_can_assess'];
            assessorLevel = assessorStatus['assessor_level'];
        }

        // Visibility 
        var visibility = this.getVisibility(h,c,is_readonly,assessorMode,assessorCanAssess)
        if (!visibility.visible){ return "" }

        // Editablility
        readonly = !visibility.editable;

        var val = (data) ? (data[c.name]) ? data[c.name] : null : null;
        switch (c.type) {
            case 'text':
                _elements.push(
                    <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                )
                break;
            case 'number':
                _elements.push(
                    <TextField type="number" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                )
                break;
            case 'email':
                _elements.push(
                    <TextField type="email" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                )
                break;
            case 'select':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div>
                        <Select readonly={readonly} name={c.name} label={c.label} value={c.value} options={c.options} help_text={c.help_text} value={val} handleChange={this.selectionChanged}  conditions={c.conditions}/>
                        <SelectConditions conditions={c.conditions} renderer={this} name={c.name} data={data} readonly={readonly} />
                    </div>
                )
                break;
            case 'multi-select':
                _elements.push(
                    <Select name={c.name} label={c.label} value={val} options={c.options} value={val} help_text={c.help_text} help_text_assessor={c.help_text_assessor} assessorMode={assessorMode} handleChange={this.selectionChanged} readonly={readonly} isMultiple={true} />
                )
                break;
            case 'text_area':
                _elements.push(
                    <TextArea readonly={readonly} name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'label':
                _elements.push(
                    <label>{c.label}</label>
                )
                break;
            case 'radiobuttons':
            var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                _elements.push(
                    <div class="form-group">
                        <label>{c.label}</label>
                            <HelpText help_text={c.help_text}/>
                            <HelpText help_text={c.help_text_assessor} assessorMode={assessorMode} isForAssessor={true}/>
                            {c.options.map(op =>{
                                return(
                                    <Radio name={c.name} label={op.label} value={op.value} savedValue={val} handleChange={this.handleRadioChange} conditions={c.conditions} readonly={readonly}/>
                                )
                            })}
                            <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data} readonly={readonly} />
                    </div>
                )
                break;
            case 'group':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                _elements.push(
                    <Group label={c.label} name={c.name} help_text={c.help_text} isRemovable={true}>
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
            case 'section':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name][0] : null ;
                }
                this.sections.push({name:c.name,label:c.label});
                _elements.push(
                    <Section label={c.label} Key={c.name} id={c.name}>
                        {c.children.map(d=>{
                            return (
                                <div>
                                    {this.renderChildren(h,d,value)}
                                </div>
                            )
                        })}
                    </Section>
                )
                break;

            case 'checkbox':
                _elements.push(
                    <div class="form-group">
                        <Checkbox name={c.name} label={c.label} help_text={c.help_text} value={val} handleChange={this.handleCheckBoxChange} conditions={c.conditions} readonly={readonly}/>
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={data}/>
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
                    <File name={c.name} label={c.label} value={val} isRepeatable={c.isRepeatable} handleChange={this.handleFileChange} readonly={readonly} help_text={c.help_text} help_text_assessor={c.help_text_assessor} assessorMode={assessorMode}/>
                )
                break;
            case 'date':
                _elements.push(
                    <DateField name={c.name} label={c.label} value={val}  handleChange={this.handleFileChange} readonly={readonly} help_text={c.help_text} help_text_assessor={c.help_text_assessor} assessorMode={assessorMode}/>
                )
                break;
            default:
            return "";
        }
        if (assessorMode && c.canBeEditedByAssessor){
            var boxes = this.generateAssessorTextBoxes(h,c,val,assessorLevel,assessorData,assessorInfo);
            // Merge assessor boxes to _elements array
            Array.prototype.push.apply(_elements,boxes);
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
            $("#cons_"+e.target.name+'_'+e.target.value).removeClass('hidden');
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
    generateAssessorTextBoxes(h,c,val,assessor_mode,assessor_data,assessor_info){
        var boxes = [];
        if (!this.status_data.can_user_edit){
            if (assessor_data){
                var _dt = assessor_data.find(at => at.name == c.name)
                // Assessor Data
                var assessor_name = `${c.name}-Assessor`;
                var assessor_val = _dt.assessor == '' ? val : _dt.assessor;
                var assessor_visiblity = assessor_mode == 'assessor' && this.status_data.assessorStatus.assessor_can_assess ? true : false;
                assessor_visiblity = !assessor_visiblity;
                boxes.push(
                    <AssessorText type="text" name={assessor_name} value={assessor_val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visiblity}/>
                )
                // Referral Data
                var current_referral_present = false;
                $.each(_dt.referrals,(i,v)=> {
                    if (v.email == assessor_info.email){ current_referral_present = true; }
                    var readonly = v.email == assessor_info.email && assessor_mode == 'referral' ? false : true;
                    var referral_name = `${c.name}-Referral-${v.email}`;
                    boxes.push(
                        <AssessorText type="text" name={referral_name} value={v.value} label={v.full_name} help_text={c.help_text} readonly={readonly}/>
                    )
                });
                if (assessor_mode == 'referral'){
                    if (!current_referral_present){
                        // Add Referral Box 
                        var referral_name = `${c.name}-Referral-${assessor_info.email}`;
                        var referral_visibility = assessor_mode != 'referral' ? true : false;
                        var referral_label = `${assessor_info.name}`;
                        boxes.push(
                            <AssessorText type="text" name={referral_name} value={assessor_val} label={referral_label} readonly={referral_visibility}/>
                        )
                    }
                }
            }
            else{
                if (assessor_mode == 'assessor'){
                    var name = `${c.name}-Assessor`;
                    var assessor_visiblity = assessor_mode != 'assessor' ? true : false;
                    boxes.push(
                        <AssessorText type="text" name={name} value={val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visiblity}/>
                    )
                }
                else if (assessor_mode == 'referral'){
                    // Add Assessor Box
                    var name = `${c.name}-Assessor`;
                    var assessor_visiblity = assessor_mode != 'assessor' ? true : false;
                    boxes.push(
                        <AssessorText type="text" name={name} value={val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visiblity}/>
                    )
                    // Add Referral Box
                    var referral_name = `${c.name}-Referral-${assessor_info.email}`;
                    var referral_visibility = assessor_mode != 'referral' ? true : false;
                    var referral_label = `${assessor_info.name}`;
                    boxes.push(
                        <AssessorText type="text" name={referral_name} value={val} label={referral_label} readonly={referral_visibility}/>
                    )
                }
            }
        }
        if (boxes.length > 0){
            boxes = [<div class="row"> {boxes} </div>]
        }
        return boxes;
    },
    status_data : {},
    store_status_data(readonly,assessorData,assessorEmail,assessorMode,can_user_edit){
        this.status_data = {
            'readonly': readonly,
            'assessorData': assessorData,
            'assessorInfo': assessorEmail,
            'assessorStatus': assessorMode,
            'can_user_edit': can_user_edit
        }
    },
    getVisibility(h,c,readonly,assessor_mode,assessor_can_assess){
        var _status = {
            'visible':true,
            'editable':true
        }
        if (assessor_mode){
            if (c.isVisibleForAssessorOnly){
                if (this.status_data.can_user_edit){
                    _status.visible = false;
                }
                if (!assessor_can_assess){ _status.editable = false }
                return _status;
            }
            else {
                _status.editable = readonly ? false : true;
            }
        }
        else{
            if (c.isVisibleForAssessorOnly){
                _status.visible = false;
                _status.editable = false;
            }
            else{
                _status.editable = readonly ? false : true;
            }
        }
        return _status;
    }
}
