<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <label :id="id" class="col-md-3" for="label" >{{labelText}}</label>
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
import {
    COMMENT_TYPE_OFFICER,
    COMMENT_TYPE_ASSESSOR,
    COMMENT_TYPE_DEFICIENCY,
} from '@/store/constants';

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
        "commentType": {
            type: String,
            default: COMMENT_TYPE_OFFICER,
        }
    },
    computed: {
        labelText: function() {
            switch(this.commentType) {
                case COMMENT_TYPE_OFFICER:
                    return 'Officer Comments';
                break;
                case COMMENT_TYPE_ASSESSOR:
                    return 'Assessor Comments';
                break;
                case COMMENT_TYPE_DEFICIENCY:
                    return 'Deficiency';
                break;
            }
        },
        value: {
            get: function() {
                switch(this.commentType) {
                    case COMMENT_TYPE_OFFICER:
                        return this.field_data.officer_comment;
                    break;
                    case COMMENT_TYPE_ASSESSOR:
                        return this.field_data.assessor_comment;
                    break;
                    case COMMENT_TYPE_DEFICIENCY:
                        return this.field_data.deficiency_value;
                    break;
                }
            },
            set: function(value) {
                switch(this.commentType) {
                    case COMMENT_TYPE_OFFICER:
                        this.field_data.officer_comment = value;
                    break;
                    case COMMENT_TYPE_ASSESSOR:
                        this.field_data.assessor_comment = value;
                    break;
                    case COMMENT_TYPE_DEFICIENCY:
                        this.field_data.deficiency_value = value;
                    break;
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
