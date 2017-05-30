import Section from '../components/section.vue'
import Group from '../components/group.vue'
import Radio from '../components/radio.vue'
import Conditions from '../components/conditions.vue'
import SelectConditions from '../components/select-conditions.vue'
import Checkbox from '../components/checkbox.vue'
import Declaration from '../components/declarations.vue'
import File from '../components/file.vue'
import Select from '../components/select.vue'
import DateField from '../components/date-field.vue'
import TextField from '../components/text.vue'
import TextArea from '../components/text-area.vue'

module.exports = {
    renderChildren(h,c,data=null) {
        var val = (data) ? (data[c.name]) ? data[c.name] : null : null;
        switch (c.type) {
            case 'text':
                return (
                    <TextField type="text" name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'number':
                return (
                    <TextField type="number" name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'email':
                return (
                    <TextField type="email" name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'select':
                return (
                    <div>
                        <Select name={c.name} label={c.label} value={c.value} options={c.options} help_text={c.help_text} value={val} handleChange={this.selectionChanged}  conditions={c.conditions}/>
                        <SelectConditions conditions={c.conditions} renderer={this} name={c.name} />
                    </div>
                )
                break;
            case 'multi-select':
                return (
                    <Select name={c.name} label={c.label} value={val} options={c.options} value={val} help_text={c.help_text} isMultiple={true} />
                )
                break;
            case 'text_area':
                return (
                    <TextArea name={c.name} value={val} label={c.label} help_text={c.help_text} />
                )
                break;
            case 'label':
                return (
                    <label>{c.label}</label>
                )
                break;
            case 'radiobuttons':
                return (
                    <div class="form-group">
                        <label>{c.label}</label>
                            {c.options.map(op =>{
                                return(
                                    <Radio name={c.name} label={op.label} value={op.value} savedValue={val} handleChange={this.handleRadioChange} conditions={c.conditions} />
                                )
                            })}
                            <Conditions conditions={c.conditions} renderer={this} name={c.name}/>
                    </div>
                )
                break;
            case 'group':
                var value = null;
                if(data !== null && data !== undefined) {
                  value = ( data[c.name] )? data[c.name] : null ;
                }
                return (
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
                  value = ( data[c.name] )? data[c.name] : null ;
                }
                this.sections.push({name:c.name,label:c.label});
                return (
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
                return (
                    <div class="form-group">
                        <Checkbox name={c.name} label={c.label} help_text={c.help_text} value={c.value} handleChange={this.handleCheckBoxChange} conditions={c.conditions} />
                        <Conditions conditions={c.conditions} renderer={this} name={c.name}/>
                    </div>
                )
                break;
            case 'declaration':
                return (
                    <div class="form-group">
                        <label>{c.label}</label>
                        <Checkbox name={c.name} label={c.label} value={c.value} help_text={c.help_text} handleChange={this.handleCheckBoxChange} conditions={c.conditions} />
                        <Conditions conditions={c.conditions} renderer={this} name={c.name}/>
                    </div>
                )
                break;
            case 'file':
                return (
                    <File name={c.name} label={c.label} value={val} isRepeatable={c.isRepeatable} handleChange={this.handleFileChange}/>
                )
                break;
            case 'date':
                return (
                    <DateField name={c.name} label={c.label} value={val}  handleChange={this.handleFileChange}/>
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
    sections:[]
}
