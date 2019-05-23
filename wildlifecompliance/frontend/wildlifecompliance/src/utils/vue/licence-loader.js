import { mapGetters, mapActions } from 'vuex';

export default {
    computed: {
        ...mapGetters(
            'application'
        ),
    },
    methods: {
        ...mapActions(
            'loadApplication'
        ),
        doSomething: function() {
        },
    },
};