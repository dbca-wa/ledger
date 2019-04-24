<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <label :id="id" class="col-md-3" for="label" >{{isDeficiency ? 'Deficiency' : 'Comments'}}</label>
                  <div class="col-md-9">
                      <textarea
                        :readonly="readonly"
                        :data-question="question"
                        class="form-control deficiency"
                        :name="name"
                        v-model="value"
                        :required="isRequired"></textarea>
                  </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        "name": {
            type: String
        },
        "question": {
            type: String
        },
        "field_data": {
            type: Object,
            required: true
        },
        "readonly": {
            type: Boolean,
            default: false
        },
        "id": {
            type: String,
        },
        "isRequired": {
            type: Boolean,
            default: false
        },
        "isDeficiency": {
            type: Boolean,
            default: false
        }
    },
    computed: {
        value: {
            get: function() {
                return this.isDeficiency ? this.field_data.deficiency_value : this.field_data.comment_value;
            },
            set: function(value) {
                if(this.isDeficiency) {
                    this.field_data.deficiency_value = value;
                }
                else {
                    this.field_data.comment_value = value;
                }
            }
        }
    }
}
</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
</style>
