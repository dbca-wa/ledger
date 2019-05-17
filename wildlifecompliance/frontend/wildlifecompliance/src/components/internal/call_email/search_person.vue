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

            self.suggest_list.length = 0;
            self.$http.get('/api/search_user/?search=' + searchTerm).then(response => {
                if (response.body && response.body.results) {
                    let persons = response.body.results;
                    let limit = Math.min(self.max_items, persons.length);
                    for (var i = 0; i < limit; i++){
                        self.suggest_list.push(persons[i])
                    }
                }
                self.awe.list = self.suggest_list;
                self.awe.evaluate();
            });
        },
        initAwesomplete: function(){
            var self = this;

            var element_search = document.getElementById('search-person');
            self.awe = new Awesomplete(element_search, { 
                maxItems: self.max_items, 
                sort: false, 
                filter: ()=>{ return true; }, // Display all the items in the list without filtering.
                data: function(item, input){
                    let f_name = item.first_name?item.first_name:'';
                    let l_name = item.last_name?item.last_name:'';

                    let full_name = [f_name, l_name].filter(Boolean).join(' ');
                    let email = item.email?'E:' + item.email:'';
                    let p_number = item.phone_number?'P:' + item.phone_number:'';
                    let m_number = item.mobile_number?'M:' + item.mobile_number:'';
                    let dob = item.dob?'DOB:' + item.dob:'DOB: ---';
                    let myLabel = [full_name, email, p_number, m_number, dob].filter(Boolean).join(', ');

                    return { 
                        label: myLabel,   // Displayed in the list below the search box
                        value: [full_name, dob].filter(Boolean).join(', '), // Inserted into the search box once selected
                        id: item.id
                    };
                }
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
                // console.log(ev);
                /* User selected one of the search results */
                // for (var i=0; i<self.suggest_list.length; i++){
                //     if (self.suggest_list[i].value == ev.target.value){

                //     }
                // }
                return false;
            }).on('awesomplete-select', function(ev){
                /* Retrieve element id of the selected item from the list
                 * By parsing it, we can get the order-number of the item in the list
                 */
                let elem_id = ev.originalEvent.origin.id;
                let reg = /^.+(\d+)$/gi;
                let result = reg.exec(elem_id)
                let idx = result[1];
                console.log('Selected person obj: ');
                console.log(self.suggest_list[idx]);
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