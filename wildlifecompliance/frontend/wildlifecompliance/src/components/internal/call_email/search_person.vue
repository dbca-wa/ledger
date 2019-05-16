<template lang="html">
    <div>
        Search Person <input id="search-person" />
    </div>
</template>
        
<script>
import Awesomplete from 'awesomplete';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';

export default {
    name: "search-person",
    data: function(){
        let vm = this;
        vm.max_items = 15;

        return {
            awe: null,
            suggest_list: [],
        }
    },
    computed: {
        //...mapGetters('callemailStore', {
            //call_email: 'call_email',
        //}),
    },
    mounted: function(){
        this.$nextTick(function() {
            this.initAwesomplete();
        })
    },
    methods: {
        search: function(searchTerm){
            var self = this;

            console.log('=====');
            console.log('search by: ' + searchTerm);

            self.suggest_list.length = 0;
            self.$http.get('/api/search_user/?search=' + searchTerm).then(response => {
                console.log('number: ' + response.body.results.length);
                if (response.body && response.body.results) {
                    let persons = response.body.results;
                    let limit = Math.min(self.max_items, persons.length);
                    for (var i = 0; i < limit; i++){
                        let f_name = persons[i].first_name?persons[i].first_name:'';
                        let l_name = persons[i].last_name?persons[i].last_name:'';

                        let full_name = [f_name, l_name].filter(Boolean).join(' ');
                        let email = persons[i].email?'e:' + persons[i].email:'';
                        let p_number = persons[i].phone_number?'p:' + persons[i].phone_number:'';
                        let m_number = persons[i].mobile_number?'m:' + persons[i].mobile_number:'';
                        let dob = persons[i].dob?'DOB:' + persons[i].dob:'';
                        let myLabel = [full_name, email, p_number, m_number, dob].filter(Boolean).join(', ');
                        console.log('Add: ' + myLabel);
                        self.suggest_list.push({
                            label: myLabel,   // Displayed in the list below the search box
                            value: [full_name, dob].filter(Boolean).join(', '), // Inserted into the search box once selected
                        });
                    }
                }
                self.awe.list = self.suggest_list;
                console.log('list');
                console.log(self.awe.list);
                self.awe.evaluate();
            });
        },
        initAwesomplete: function(){
            var self = this;

            var element_search = document.getElementById('search-person');
            self.awe = new Awesomplete(element_search, { 
                maxItems: self.max_items, 
                sort: false, 
            });
            $(element_search).on('keyup', function(ev){
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105) || (keyCode == 8) || (keyCode == 46)){
                    self.search(ev.target.value);
                    return false;
                }
            }).on('awesomplete-selectcomplete', function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                /* User selected one of the search results */
                for (var i=0; i<self.suggest_list.length; i++){
                    if (self.suggest_list[i].value == ev.target.value){

                    }
                }
                return false;
            });
        },

    }
}
</script>        

<style>
.awesomplete {
    z-index: 2000 !important;
}
#search-person {
    z-index: 9999;
    width: 400px;
}
</style>