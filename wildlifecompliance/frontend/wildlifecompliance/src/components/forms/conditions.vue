<template lang="html">
    <span>
        <div v-for="condition in condition_keys">
            <div :id="'cons_' + name + '_' + condition" :class="{'hidden': !isVisible(condition)}">
                <renderer-block v-for="(subcomponent, index) in conditionBlocks(condition)"
                    :component="subcomponent"
                    :json_data="data"
                    v-bind:key="`condition_${condition}_${index}`"
                    />
            </div>
        </div>
    </span>
</template>

<script>
    import { mapGetters } from 'vuex';
    export default {
        name: 'conditions',
        props: ["conditions","name","data","readonly"],
        computed: {
            ...mapGetters([
                'isComponentVisible',
            ]),
            has_conditions: function() {
                return this.condition_keys.length;
            },
            condition_keys: function() {
                if(this.conditions == null) {
                    return [];
                }
                return Object.keys(this.conditions);
            },
        },
        methods: {
            conditionBlocks: function(key) {
                return this.conditions[key] ? this.conditions[key] : [];
            },
            isVisible: function(condition) {
                return this.isComponentVisible(`cons_${this.name}_${condition}`);
            }
        },
    }
</script>
