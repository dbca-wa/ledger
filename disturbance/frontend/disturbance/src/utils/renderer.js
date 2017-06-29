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

module.exports = {
    renderChildren(h,c,data=null,assessor_data=null,readonly=false,assessorMode=false,assessorLevel) {
        assessorMode = true;
        assessorLevel = 'assessor';
        var val = (data) ? (data[c.name]) ? data[c.name] : null : null;
        switch (c.type) {
            case 'text':
                if (assessorMode && c.canBeEditedByAssessor){
                    var proponent_field = <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                    var boxes = this.generateAssessorTextBoxes(h,c,val,assessorLevel,assessor_data);
                    boxes.unshift(proponent_field);
                    return (
                        boxes
                    )
                }
                else{
                    return (
                        <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                    )
                }
                break;
            case 'number':
                return (
                    <TextField type="number" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                )
                break;
            case 'email':
                return (
                    <TextField type="email" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={readonly}/>
                )
                break;
            case 'select':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                return (
                    <div>
                        <Select readonly={readonly} name={c.name} label={c.label} value={c.value} options={c.options} help_text={c.help_text} value={val} handleChange={this.selectionChanged}  conditions={c.conditions}/>
                        <SelectConditions conditions={c.conditions} renderer={this} name={c.name} data={data} readonly={readonly} />
                    </div>
                )
                break;
            case 'multi-select':
                return (
                    <Select name={c.name} label={c.label} value={val} options={c.options} value={val} help_text={c.help_text} handleChange={this.selectionChanged} readonly={readonly} isMultiple={true} />
                )
                break;
            case 'text_area':
                return (
                    <TextArea readonly={readonly} name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'label':
                return (
                    <label>{c.label}</label>
                )
                break;
            case 'radiobuttons':
            var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data )? data : null ;
                }
                return (
                    <div class="form-group">
                        <label>{c.label}</label>
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
                return (
                    <Group label={c.label} name={c.name} help_text={c.help_text} isRemovable={true}>
                        {c.children.map(c=>{
                            return (
                                <div>
                                    {this.renderChildren(h,c,value,assessor_data,readonly,assessorMode,assessorLevel)}
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
                return (
                    <Section label={c.label} Key={c.name} id={c.name}>
                        {c.children.map(d=>{
                            return (
                                <div>
                                    {this.renderChildren(h,d,value,assessor_data,readonly,assessorMode,assessorLevel)}
                                </div>
                            )
                        })}
                    </Section>
                )
                break;

            case 'checkbox':
                return (
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
                return (
                    <div class="form-group">
                        <label>{c.label}</label>
                        <Checkbox name={c.name} label={c.label} value={val} help_text={c.help_text} handleChange={this.handleCheckBoxChange} conditions={c.conditions} />
                        <Conditions conditions={c.conditions} renderer={this} name={c.name} data={value}/>
                    </div>
                )
                break;
            case 'file':
                return (
                    <File name={c.name} label={c.label} value={val} isRepeatable={c.isRepeatable} handleChange={this.handleFileChange} readonly={readonly}/>
                )
                break;
            case 'date':
                return (
                    <DateField name={c.name} label={c.label} value={val}  handleChange={this.handleFileChange} readonly={readonly}/>
                )
                break;
            default:
            return "";
        }
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
    generateAssessorTextBoxes(h,c,val,assessor_mode,assessor_data=null,assessor_email){
        var boxes = [];

        if (assessor_data){
            var _dt = assessor_data.find(at => at.name == c.name)
            // Assessor Data
            var assessor_name = `${c.name}-Assessor`;
            var assessor_val = _dt.assessor == '' ? val : _dt.assessor;
            var assessor_visiblity = assessor_mode != 'assessor' ? true : false;
            boxes.push(
                <AssessorText type="text" name={assessor_name} value={assessor_val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visiblity}/>
            )
            $.each(_dt.referrals,(i,v)=> {
                var readonly = v.email != assessor_email ? true : false;
                var referral_name = `${c.name}-Referral-${v.email}`;
                boxes.push(
                    <AssessorText type="text" name={referral_name} value={v.value} label={v.full_name} help_text={c.help_text} readonly={readonly}/>
                )
            });
        }
        else{
            if (assessor_mode == 'assessor'){
                var name = `${c.name}-Assessor`;
                var assessor_visiblity = assessor_mode != 'assessor' ? true : false;
                boxes.push(
                    <AssessorText type="text" name={name} value={val} label={'Assessor'} help_text={c.help_text} readonly={assessor_visiblity}/>
                )
            }
        }



        if (assessor_mode == 'assessor'){
        }
        else if (assessor_mode == 'referral'){
            
        }
        boxes = [<div class="row"> {boxes} </div>]
        return boxes;
        /* Visibility stuff
        if (visibility.visible){
            if (visibility.editable){
                return (
                    <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text}/>
                )
            }
            else{
                return (
                    <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text} readonly={!visibility.editable}/>
                )
            }
        }*/
    },
    getVisibility(c,readonly,assessor_mode,referral_mode){
        var status = {
            'visible': false,
            'editable': false
        };
        if (c.isVisibleForAssessorOnly){
            console.log(c.name);
            if (assessor_mode || referral_mode){
                if (assessor_mode){
                    if (c.canBeEditedByAssessor){
                        status['visible'] = true;
                        status['editable'] = true;
                    }
                    else {
                       status['visible'] = true;
                    }
                }
                if (referral_mode){
                    if (c.canBeEditedByAssessor){
                        status['visible'] = true;
                        status['editable'] = true;
                    }
                    else {
                       status['visible'] = true;
                    }
                }
            }
            else{
                return status;
            }
        }
        else{
            status['visible'] = true;
            if (!readonly){
                status['editable'] = true;
            }
        }
        return status;
    }
}
