<template lang="html">
    <div>
        Search Person <input id="search-person" /><button>Create New Person</button>
        <div class="col-md-9">
            <div class="tab-content">
                <div :id="dTab" class="tab-pane fade in active">
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                <h3 class="panel-title">Personal Details
                                    <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                    </a>
                                </h3>
                                </div>
                                <div class="panel-body collapse in" :id="pdBody">
                                    <form class="form-horizontal" name="personal_form" method="post">
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="first_name" placeholder="" v-model="user.first_name">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Last Name</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="last_name" placeholder="" v-model="user.last_name">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                                        <div class="col-sm-6">
                                            <input type="date" class="form-control" name="dob" placeholder="" v-model="user.dob">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <div class="col-sm-12">
                                                <button v-if="!updatingPersonal" class="pull-right btn btn-primary" @click.prevent="updatePersonal()">Update</button>
                                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                <h3 class="panel-title">Address Details
                                    <a class="panelClicker" :href="'#'+adBody" data-toggle="collapse" expanded="false"  data-parent="#userInfo" :aria-controls="adBody">
                                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                    </a>
                                </h3>
                                </div>
                                <div v-if="loading.length == 0" class="panel-body collapse in" :id="adBody">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Street</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="street" placeholder="" v-model="user.residential_address.line1">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <input type="text" class="form-control" name="surburb" placeholder="" v-model="user.residential_address.locality">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <input type="text" class="form-control" name="country" placeholder="" v-model="user.residential_address.state">
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <input type="text" class="form-control" name="postcode" placeholder="" v-model="user.residential_address.postcode">
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <select class="form-control" name="country" v-model="user.residential_address.country">
                                                <option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option>
                                            </select>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <div class="col-sm-12">
                                            <button v-if="!updatingAddress" class="pull-right btn btn-primary" @click.prevent="updateAddress()">Update</button>
                                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div> 
            </div>
        </div>
    </div>
</template>
        
<script>
import Awesomplete from 'awesomplete';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import 'bootstrap/dist/css/bootstrap.css';
import 'awesomplete/awesomplete.css';
import utils from '../utils'

export default {
    name: "search-person",
    data: function(){
        let vm = this;
        vm.max_items = 15;

        return {
            awe: null,
            suggest_list: [],
            adBody: 'adBody'+vm._uid,
            pdBody: 'pdBody'+vm._uid,
            cdBody: 'cdBody'+vm._uid,
            odBody: 'odBody'+vm._uid,
            idBody: 'idBody'+vm._uid,
            dTab: 'dTab'+vm._uid,
            oTab: 'oTab'+vm._uid,
            user: {
                residential_address: {},
                wildlifecompliance_organisations: []
            },
            loading: [],
            countries: [],
            updatingAddress: false,
            updatingPersonal: false,
        }
    },
    beforeRouteEnter: function(to, from, next){
        console.log('beforeRouteEnter');
        console.log(to);
        console.log(from);
        console.log(next);
    },
    computed: {
        ...mapGetters('callemailStore', {
            call_email: "call_email",
        }),
    },
    mounted: function(){
        this.$nextTick(function() {
            this.initAwesomplete();
        });
        // TODO: user should be loaded if call_email has.
        // this.loadEmailUser(emailUser_id);
    },
    methods: {
        loadEmailUser: function(id){
            let initialisers = [
                utils.fetchCountries(),
                utils.fetchUser(id),
            ]
            Promise.all(initialisers).then(data => {
                this.countries = data[0];
                this.user = data[1];
                this.user.residential_address = this.user.residential_address != null ? this.user.residential_address : {};
            });
        },
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
                return false;
            }).on('awesomplete-select', function(ev){
                /* Retrieve element id of the selected item from the list
                 * By parsing it, we can get the order-number of the item in the list
                 */
                let elem_id = ev.originalEvent.origin.id;
                let reg = /^.+(\d+)$/gi;
                let result = reg.exec(elem_id)
                let idx = result[1];
                console.log('Selected person id: ');
                console.log(self.suggest_list[idx].id);
                self.loadEmailUser(self.suggest_list[idx].id);
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