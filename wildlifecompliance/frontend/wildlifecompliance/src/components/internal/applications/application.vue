<template lang="html">
    <div v-if="application" class="container" id="internalApplication">
            <div class="row">
        <h3>Application: {{ application.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row" v-if="canSeeSubmission">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ application.submitter.first_name }} {{ application.submitter.last_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ application.lodgement_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ application.processing_status.name }}<br/>
                                <div class ="col-sm-12" v-for="item in application.licence_type_data">
                                    
                                    <div v-for="item1 in item">
                                        <div v-if="item1.name">
                                            <strong>{{item1.name}}: </strong>{{item1.processing_status.name}}
                                        </div>
                                    </div>
                                </div>
                            </div>
                             <div class="col-sm-12 top-buffer-s">
                                <strong>Assigned Officer</strong><br/>
                                <div class="form-group">
                                    <template>
                                        <select ref="assigned_officer" :disabled="!canAssignToOfficer" class="form-control" v-model="application.assigned_officer">
                                            <option v-for="member in application.licence_officers" :value="member.id" v-bind:key="member.id">{{member.first_name}} {{member.last_name}}</option>
                                        </select>
                                        <a v-if="canAssignToOfficer" @click.prevent="assignToMe()" class="actionBtn pull-right">Assign to me</a>
                                    </template>
                                </div>
                            </div>

                            <template v-if="application.processing_status.id == 'with_assessor_conditions' || application.processing_status.id == 'with_approver' || isFinalised">
                                <div>
                                    <div class="col-sm-12">
                                        <strong>Application</strong><br/>
                                        <a class="actionBtn" v-if="!showingApplication" @click.prevent="toggleApplication()">Show Application</a>
                                        <a class="actionBtn" v-else @click.prevent="toggleApplication()">Hide Application</a>
                                    </div>
                                    <div class="col-sm-12">
                                        <div class="separator"></div>
                                    </div>
                                </div>
                            </template>
                            <template v-if="application.processing_status.id == 'with_approver' || isFinalised">
                                <div class="col-sm-12">
                                    <strong>Conditions</strong><br/>
                                    <a class="actionBtn" v-if="!showingConditions" @click.prevent="toggleConditions()">Show Conditions</a>
                                    <a class="actionBtn" v-else @click.prevent="toggleConditions()">Hide Conditions</a>
                                </div>
                                <div class="col-sm-12">
                                    <div class="separator"></div>
                                </div>
                            </template>
                              <div class="col-sm-12 top-buffer-s" >
                                <template v-if="showingApplication">
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div v-if="!applicationIsDraft && canRequestAmendment" class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" @click.prevent="amendmentRequest()">Request Amendment</button><br/>
                                        </div>
                                    </div>
                                    <div v-if="!applicationIsDraft && canSendToAssessor" class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" @click.prevent="togglesendtoAssessor()">Send to Assessor</button><br/>
                                        </div>
                                    </div>
                                    <div v-if="canOfficerReviewConditions" class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-warning top-buffer-s" @click.prevent="toggleOfficerConditions()">Review Conditions</button>
                                        </div>
                                    </div>
                                    <div v-if="canProposeIssueOrDecline" class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-danger top-buffer-s" @click.prevent="proposedDecline()">Propose Decline</button>
                                            <button style="width:80%;" class="btn btn-success top-buffer-s" @click.prevent="proposedLicence()">Propose Issue</button>
                                        </div>
                                    </div>
                                    <div v-if="canIssueDecline" class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-warning top-buffer-s" @click.prevent="toggleFinalViewConditions()">View Final Conditions</button>
                                        </div>
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-success top-buffer-s" @click.prevent="toggleIssue()">Issue/Decline</button>
                                        </div>
                                    </div>
                                </template>
                                <template v-else>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div v-if="isSendingToAssessor || isOfficerConditions || isFinalViewConditions || showingConditions || isofficerfinalisation"class="row">
                                        <div class="col-sm-12">
                                            <button style="width:80%;" class="btn btn-primary top-buffer-s" @click.prevent="toggleApplication()">Back to Application</button><br/>
                                        </div>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <template v-if="isFinalised || isPartiallyFinalised">
                    <LicenceScreen :application="application"/>
                </template>
                <template v-if="canIssueDecline">
                    <IssueLicence :application="application" :licence_activity_tab="selected_activity_tab_id"/>
                </template>
                <template v-if="showingConditions">
                    <div>
                        <ul class="nav nav-tabs" id="conditiontabs">
                            <li v-for="activity in getVisibleConditionsFor('assessor', 'with_assessor')"><a data-toggle="tab" :data-target="`#${activity.id}`">{{activity.name}}</a></li>
                        </ul>
                    </div>
                    <div class="tab-content">
                        <div v-for="activity in getVisibleConditionsFor('assessor', 'with_assessor', selected_activity_tab_id)">
                            <div :id="`${activity.id}`" class="tab-pane fade in">
                                <Conditions :application="application" :licence_activity_tab="selected_activity_tab_id" :key="`assessor_condition_${selected_activity_tab_id}`"/>
                            </div>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom:50px;">
                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                            <div class="navbar-inner">
                                <div class="container">
                                    <p class="pull-right" style="margin-top:5px;">
                                        <button class="btn btn-primary" @click.prevent="completeAssessment()">Complete Assessment</button>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                </template>
                <template v-if="isOfficerConditions">
                    <div>
                        <ul class="nav nav-tabs" id="conditiontabs">
                            <li v-for="activity in getVisibleConditionsFor('licensing_officer', 'with_officer_conditions')"><a data-toggle="tab" :data-target="`#${activity.id}`">{{activity.name}}</a></li>
                        </ul>
                    </div>
                    <div class="tab-content">
                        <div v-for="activity in getVisibleConditionsFor('licensing_officer', 'with_officer_conditions', selected_activity_tab_id)" :id="`${activity.id}`" class="tab-pane fade active in">
                            <OfficerConditions :application="application" :licence_activity_tab="activity.id" :final_view_conditions="false" :key="`officer_condition_${selected_activity_tab_id}`"/>
                        </div>
                    </div>
                </template>
                <template v-if="isFinalViewConditions">
                    <div>
                        <ul class="nav nav-tabs" id="conditiontabs">
                            <li v-for="activity in getVisibleConditionsFor('issuing_officer', 'with_officer_finalisation')"><a data-toggle="tab" :data-target="`#${activity.id}`">{{activity.name}}</a></li>
                        </ul>
                    </div>
                    <div class="tab-content">
                        <div v-for="activity in getVisibleConditionsFor('issuing_officer', 'with_officer_finalisation', selected_activity_tab_id)" :id="`${activity.id}`" class="tab-pane fade active in">
                            <OfficerConditions :application="application" :licence_activity_tab="activity.id" :final_view_conditions="true" :key="`final_condition_${selected_activity_tab_id}`"/>
                        </div>
                    </div>
                </template>
                <template v-if="isSendingToAssessor && !showingConditions">
                    <div>
                        <ul id="tabs-assessor" class="nav nav-tabs">
                            <li v-for="(item1,index) in application.licence_type_data.activity" v-if="item1.name && (item1.processing_status.id=='with_officer' || item1.processing_status.id=='with_officer_conditions' || item1.processing_status.id=='with_assessor')" :class="setAssessorTab(index)" @click.prevent="clearSendToAssessorForm()">
                                <a v-if="isActivityVisible(item1.id)" data-toggle="tab" :data-target="`#${item1.id}`">{{item1.name}}</a>
                            </li>
                        </ul>
                    </div>
                        
                    <div class="tab-content">
                        <div v-for="(item1,index) in application.licence_type_data.activity" v-if="item1.name && (item1.processing_status.id=='with_officer' || item1.processing_status.id=='with_officer_conditions' || item1.processing_status.id=='with_assessor')" :id="`${item1.id}`" :class="setAssessorTabContent(index)">
                            <div>
                                <div class="panel panel-default">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">Send to Assessor
                                            <a class="panelClicker" :href="`#${item1.id}`+assessorsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="assessorsBody">
                                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                            </a>
                                        </h3>
                                    </div>
                                    <div class="panel-body panel-collapse collapse in" :id="`${item1.id}`+assessorsBody">
                                        <div class="row">
                                           <div class="col-sm-10" style="margin-bottom: 10px">
                                                    <label class="control-label pull-left"  for="Name">Assessor Group</label>
                                                    <select class="form-control" v-model="selectedAssessor">
                                                        <option v-for="assessor in assessorGroup" :id="assessor.id"
                                                        :value="assessor" v-if="isAssessorRelevant(assessor)">{{assessor.display_name}}</option>
                                                    </select>
                                            </div>
                                            <div class="col-sm-2">
                                                <a class="btn btn-primary" style="cursor:pointer;text-decoration:none;" @click.prevent="sendtoAssessor(item1.id)">Send</a>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <datatable ref="assessorDatatable" :data-index="index" :id="`${item1.id}`+_uid+'assessor_datatable'" :dtOptions="assessors_options[`${item1.id}`]" :dtHeaders="assessors_headers" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
                <template v-if="applicationDetailsVisible">
                    <div>
                    <ul class="nav nav-tabs" id="tabs-main">
                        <li><a data-toggle="tab" :href="'#'+applicantTab">Applicant</a></li>
                        <li><a data-toggle="tab" :href="'#'+applicationTab">Application</a></li>
                    </ul>
                    <div class="tab-content">
                    <div :id="applicantTab" class="tab-pane fade in active">

                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Applicant
                                        <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="detailsBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                                    </h3> 
                                </div>
                                <div v-if="applicantType == 'org'" class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Name</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.org_applicant.name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="application.org_applicant.abn">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                                <div v-if="applicantType == 'proxy'" class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.proxy_applicant.first_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Surname</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.proxy_applicant.last_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="application.proxy_applicant.dob">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                                <div v-if="applicantType == 'submitter'" class="panel-body panel-collapse collapse in" :id="detailsBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.submitter.first_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Surname</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="application.submitter.last_name">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="application.submitter.dob">
                                            </div>
                                          </div>
                                      </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Identification
                                        <a class="panelClicker" :href="'#'+identificationBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="identificationBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div v-if="applicantType == 'org' && application.org_applicant.organisation.identification" class="panel-body panel-collapse collapse" :id="identificationBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Identification</label>
                                            <div class="col-sm-8">
                                                <img width="100%" name="applicantIdentification" v-bind:src="application.org_applicant.organisation.identification" />
                                            </div>
                                          </div>
                                      </form>
                                </div>
                                <div v-if="applicantType == 'proxy' && application.proxy_applicant.identification && application.proxy_applicant.identification.file" class="panel-body panel-collapse collapse" :id="identificationBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Identification</label>
                                            <div class="col-sm-8">
                                                <img width="100%" name="applicantIdentification" v-bind:src="application.proxy_applicant.identification.file" />
                                            </div>
                                          </div>
                                      </form>
                                </div>
                                <div v-if="applicantType == 'submitter' && application.submitter.identification && application.submitter.identification.file" class="panel-body panel-collapse collapse" :id="identificationBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Identification</label>
                                            <div class="col-sm-8">
                                                <img width="100%" name="applicantIdentification" v-bind:src="application.submitter.identification.file" />
                                            </div>
                                          </div>
                                      </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Address Details
                                        <a class="panelClicker" :href="'#'+addressBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="addressBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3> 
                                </div>
                                <div v-if="applicantType == 'org' && application.org_applicant.address" class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="application.org_applicant.address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="application.org_applicant.address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="application.org_applicant.address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="application.org_applicant.address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="application.org_applicant.address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                                <div v-if="applicantType == 'proxy' && application.proxy_applicant.residential_address" class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="application.proxy_applicant.residential_address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="application.proxy_applicant.residential_address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="application.proxy_applicant.residential_address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="application.proxy_applicant.residential_address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="application.proxy_applicant.residential_address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                                <div v-if="applicantType == 'submitter' && application.submitter.residential_address" class="panel-body panel-collapse collapse" :id="addressBody">
                                      <form class="form-horizontal">
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">Street</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="street" placeholder="" v-model="application.submitter.residential_address.line1">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                            <div class="col-sm-6">
                                                <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="application.submitter.residential_address.locality">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label">State</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="country" placeholder="" v-model="application.submitter.residential_address.state">
                                            </div>
                                            <label for="" class="col-sm-2 control-label">Postcode</label>
                                            <div class="col-sm-2">
                                                <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="application.submitter.residential_address.postcode">
                                            </div>
                                          </div>
                                          <div class="form-group">
                                            <label for="" class="col-sm-3 control-label" >Country</label>
                                            <div class="col-sm-4">
                                                <input disabled type="text" class="form-control" name="country" v-model="application.submitter.residential_address.country"/>
                                            </div>
                                          </div>
                                       </form>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class="row">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h3 class="panel-title">Contact Details
                                        <a class="panelClicker" :href="'#'+contactsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="contactsBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                        </a>
                                    </h3>
                                </div>
                                <div v-if="applicantType == 'org'" class="panel-body panel-collapse collapse" :id="contactsBody">
                                    <table ref="contacts_datatable" :id="contacts_table_id" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%">
                                    </table>
                                </div>
                                <div v-if="applicantType == 'proxy'" class="panel-body panel-collapse collapse" :id="contactsBody">
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantPhoneNumber" placeholder="" v-model="application.proxy_applicant.phone_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantMobileNumber" placeholder="" v-model="application.proxy_applicant.mobile_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Email</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantEmail" placeholder="" v-model="application.proxy_applicant.email">
                                        </div>
                                      </div>
                                  </form>
                                </div>
                                <div v-if="applicantType == 'submitter'" class="panel-body panel-collapse collapse" :id="contactsBody">
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Phone (work)</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantPhoneNumber" placeholder="" v-model="application.submitter.phone_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantMobileNumber" placeholder="" v-model="application.submitter.mobile_number">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Email</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantEmail" placeholder="" v-model="application.submitter.email">
                                        </div>
                                      </div>
                                  </form>
                                </div>

                            </div>
                        </div>
                    </div>
                    <div class="col-md-12">
                        <div class ="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Check List
                                    <a class="panelClicker" :href="'#'+checksBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="checksBody">
                                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>

                            </div>
                            <div class="panel-body panel-collapse collapse" :id="checksBody">
                                <div class="row">
                                    <div class="col-sm-4">ID Check</div>
                                    <div class="col-sm-4">
                                        <button v-if="isIdNotChecked || isIdCheckUpdated" class="btn btn-primary" @click.prevent="acceptIdRequest()">Accept</button>
                                        <button v-if="isIdCheckAccepted" disabled class="btn btn-light">Accepted</button>
                                        <button v-if="isIdCheckRequested" disabled class="btn btn-light">Awaiting Update</button>
                                    </div>
                                    <div class="col-sm-4">
                                        <button v-if="isIdNotChecked" class="btn btn-primary" @click.prevent="updateIdRequest()">Request Update</button>
                                        <button v-if="isIdCheckUpdated" disabled class="btn btn-light">Request updated</button>
                                        <button v-if="isIdCheckAccepted || isIdCheckRequested"  class="btn btn-primary" @click.prevent="resetIdRequest()">Reset</button>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-4">Character Check</div>
                                    <div class="col-sm-4">
                                        <button v-if="!isCharacterCheckAccepted" class="btn btn-primary" @click.prevent="acceptCharacterRequest()">Accept</button>
                                        <button v-if="isCharacterCheckAccepted" disabled class="btn btn-light">Accepted</button>
                                    </div>
                                    <div class="col-sm-4">
                                        <button v-if="isCharacterCheckAccepted"  class="btn btn-primary">Reset</button>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-4">Returns Check</div>
                                    <div class="col-sm-4">
                                        <button v-if="isCharacterCheckAccepted" class="btn btn-primary">Request Completion</button>
                                    </div>
                                </div>
                            </div>


                        </div>
                    </div>


                    </div>
                </div>
                <div :id="applicationTab" class="tab-pane fade">
                    <div class="col-md-12">
                        <div class="row">
                            <form :action="application_form_url" method="post" name="new_application" enctype="multipart/form-data">
                                <Application form_width="inherit" :withSectionsSelector="false" v-if="application" :application="application">
                                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                    <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                                    <input type='hidden' name="application_id" :value="1" />
                                    <input type='hidden' id="selected_activity_tab_id" v-model="selected_activity_tab_id" />
                                    <div class="row" style="margin-bottom:50px;">
                                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                                            <div class="navbar-inner">
                                                <div class="container">
                                                    <p class="pull-right" style="margin-top:5px;">
                                                        <button v-if="canReturnToConditions" class="btn btn-primary" @click.prevent="returnToOfficerConditions()">Return to Officer - Conditions</button>
                                                        <button v-if="canCompleteAssessment" class="btn btn-info" @click.prevent="toggleConditions()">Assess</button>
                                                        <button v-if="!applicationIsDraft && canRequestAmendment" class="btn btn-primary" @click.prevent="save()">Save Changes</button>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Application>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>
        </div>
        </div>
        </div>
        <ProposedDecline ref="proposed_decline" :processing_status="application.processing_status" :application_id="application.id" :application_licence_type="application.licence_type_data" @refreshFromResponse="refreshFromResponse" :application="application"></ProposedDecline>
        <AmendmentRequest ref="amendment_request" :application_id="application.id" :application_licence_type="application.licence_type_data" @refreshFromResponse="refreshFromResponse"></AmendmentRequest>
        <SendToAssessor ref="send_to_assessor" :application_id="application.id" @refreshFromResponse="refreshFromResponse"></SendToAssessor>
        <ProposedLicence ref="proposed_licence" :processing_status="application.processing_status" :application_id="application.id" :application_licence_type="application.licence_type_data" @refreshFromResponse="refreshFromResponse" :application="application"></ProposedLicence>

    </div>
</div>
</template>
<script>
import Application from '../../form.vue';
import Vue from 'vue';
import ProposedDecline from './application_proposed_decline.vue';
import AmendmentRequest from './amendment_request.vue';
import SendToAssessor from './application_send_assessor.vue';
import datatable from '@vue-utils/datatable.vue';
import Conditions from './application_conditions.vue';
import OfficerConditions from './application_officer_conditions.vue';
import ProposedLicence from './proposed_issuance.vue';
import IssueLicence from './application_issuance.vue';
import LicenceScreen from './application_licence.vue';
import CommsLogs from '@common-utils/comms_logs.vue';
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js";
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import { isApplicationActivityVisible } from "@/utils/helpers.js";
export default {
    name: 'InternalApplication',
    data: function() {
        let vm = this;
        return {
            applicantTab: 'applicantTab'+vm._uid,
            applicationTab: 'applicationTab'+vm._uid,
            detailsBody: 'detailsBody'+vm._uid,
            identificationBody: 'identificationBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            checksBody: 'checksBody'+vm._uid,
            assessorsBody:'assessorsBody'+vm._uid,
            isSendingToAssessor: false,
            assessorGroup:{},
            "selectedAssessor":{},
            "application": null,
            "original_application": null,
            "loading": [],
            selected_activity_tab_id:null,
            selected_activity_tab_name:null,
            form: null,
            // activity_data:[],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingApplication:true,
            showingConditions:false,
            assessmentComplete:false,
            isOfficerConditions:false,
            isFinalViewConditions:false,
            isofficerfinalisation:false,
            contacts_table_id: vm._uid+'contacts-table',
            application_assessor_datatable:vm._uid+'assessment-table',
            contacts_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.contactsURL,
                    "dataSrc": ''
                },
                columns: [
                    {
                        title: 'Name',
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {
                        title: 'Phone',
                        data:'phone_number'
                    },
                    {
                        title: 'Mobile',
                        data:'mobile_number'
                    },
                    {
                        title: 'Fax',
                        data:'fax_number'
                    },
                    {
                        title: 'Email',
                        data:'email'
                    },
                  ],
                  processing: true
            },
            contacts_table: null,
            assessors_headers:["Assessor Group","Date Sent","Status","Action"],
            assessors_options:{},
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            comms_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/add_comms_log'),
            logs_url: helpers.add_endpoint_json(api_endpoints.applications,vm.$route.params.application_id+'/action_log'),
            panelClickersInitialised: false,
        }
    },
    components: {
        Application,
        datatable,
        ProposedDecline,
        AmendmentRequest,
        SendToAssessor,
        Conditions,
        OfficerConditions,
        ProposedLicence,
        IssueLicence,
        LicenceScreen,
        CommsLogs
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    watch: {
    },
    computed: {
        applicationDetailsVisible: function() {
            return !this.isSendingToAssessor && !this.showingConditions && !this.isofficerfinalisation && !this.isFinalised && !this.isOfficerConditions && !this.isFinalViewConditions;
        },
        applicationIsDraft: function(){
            return this.application.processing_status.id == 'draft';
        },
        selectedActivity: function(){
            var activities_list = this.application.licence_type_data.activity
            for(let activity of activities_list){
                if(activity.id == this.selected_activity_tab_id){
                    return activity;
                }
            }
            return null;
        },
        canIssueDecline: function(){
            var activities_list = this.application.licence_type_data.activity;
            for(let activity of activities_list){
                if(activity.processing_status.id == 'with_officer_finalisation' &&
                    this.userHasRole('issuing_officer', activity.id)){
                        return true;
                }
            }
            return false;
        },
        canRequestAmendment: function(){
            var activities_list = this.application.licence_type_data.activity
            for(let activity of activities_list){
                if(activity.processing_status.id == 'with_officer' &&
                    this.userHasRole('licensing_officer', activity.id)){
                        return true;
                }
            }
            return false;
        },
        canSendToAssessor: function(){
            return this.userHasRole('licensing_officer') && this.hasActivityStatus([
                'with_officer',
                'with_officer_conditions',
                'with_assessor',
                ]);
        },
        canReturnToConditions: function(){
            if(!this.userHasRole('issuing_officer', this.selected_activity_tab_id)) {
                return false;
            }
            return this.selected_activity_tab_id && this.selectedActivity.processing_status.id == 'with_officer_finalisation' ? true : false;
        },
        canOfficerReviewConditions: function(){
            return this.hasActivityStatus('with_officer_conditions', 1, 'licensing_officer');
        },
        canProposeIssueOrDecline: function(){
            return this.hasActivityStatus('with_officer_conditions', 1, 'licensing_officer');
        },
        canCompleteAssessment: function(){
            if(!this.userHasRole('assessor')) {
                return false;
            }
            return this.selected_activity_tab_id && this.selectedActivity.processing_status.id == 'with_assessor' ? true : false;
        },
        contactsURL: function(){
            return this.application!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.application.org_applicant.id+'/contacts') : '';
        },
        applicantType: function(){
            if (this.application.org_applicant){
                return 'org';
            } else if (this.application.proxy_applicant){
                return 'proxy';
            } else {
                return 'submitter';
            }
        },
        isLoading: function() {
          return this.loading.length > 0
        },
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        application_form_url: function() {
          return (this.application) ? `/api/application/${this.application.id}/application_officer_save.json` : '';
        },
        isFinalised: function(){
            return this.hasActivityStatus([
                'declined',
                'accepted'
            ], this.application.licence_type_data.activity.length);
        },
        isPartiallyFinalised: function(){
            const final_statuses = [
                'declined',
                'accepted'
            ];
            const activity_count = this.application.licence_type_data.activity.length;
            return this.hasActivityStatus(final_statuses) && !this.hasActivityStatus(final_statuses, activity_count);            
        },
        isIdCheckAccepted: function(){
            return this.application.id_check_status.id == 'accepted';
        },
        isIdNotChecked: function(){
            return this.application.id_check_status.id == 'not_checked';
        },
        isIdCheckRequested: function(){
            return this.application.id_check_status.id == 'awaiting_update';
        },
        isIdCheckUpdated: function(){
            return this.application.id_check_status.id == 'updated';
        },
        isCharacterCheckAccepted: function(){
            return this.application.character_check_status.id == 'accepted';
        },
        canAssignToOfficer: function(){
            if(!this.userHasRole('licensing_officer')) {
                return false;
            }
            return this.application && this.application.processing_status.id == 'under_review' && !this.isFinalised && !this.application.can_user_edit && this.application.user_in_licence_officers ? true : false;
        },
        canSeeSubmission: function(){
            return this.application && (this.application.processing_status.id != 'with_assessor_conditions' && this.application.processing_status.id != 'with_approver' && !this.isFinalised)
        }
    },
    methods: {
        eventListeners: function(){
            let vm = this;
            $("[data-target!=''][data-target]").off("click").on("click", function (e) {
                vm.selected_activity_tab_id = parseInt($(this).data('target').replace('#', ''), 10);
                vm.selected_activity_tab_name = $(this).text();
            });
            this.initFirstTab();
            // Listeners for Send to Assessor datatable actions
            if (vm.$refs.assessorDatatable) {
                for (var i=0; i < vm.$refs.assessorDatatable.length; i++) {
                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_remind',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/remind_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Sent',
                                 'An email has been sent to assessor with the request to assess this Application',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });

                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_resend',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/resend_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Sent',
                                 'An email has been sent to assessor with the request to re-assess this Application',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                                vm.refreshFromResponse(res);
                            });

                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });

                    vm.$refs.assessorDatatable[i].vmDataTable.on('click','.assessment_recall',(e) => {
                        e.preventDefault();

                        let assessment_id = $(e.target).data('assessmentid');
                        vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessment,(assessment_id+'/recall_assessment'))).then((response)=>{
                            //vm.$parent.loading.splice('processing contact',1);
                            swal(
                                 'Success',
                                 'An assessment for this Application has been recalled',
                                 'success'
                            )
                            vm.refreshAssessorDatatables();
                            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,vm.application.id+'/internal_application')).then((res) => {
                                vm.refreshFromResponse(res);
                            });
                        },(error)=>{
                            console.log(error);
                            vm.errors = true;
                            vm.errorString = helpers.apiVueResourceError(error);


                        });
                    });
                }
            }
        },
        userHasRole: function(role, activity_id) {
            return this.application.user_roles.filter(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            ).length;
        },
        getVisibleConditionsFor: function(for_role, processing_status, tab_id) {
            return this.application.licence_type_data.activity.filter(activity =>
                activity.name && activity.processing_status.id == processing_status && this.userHasRole(for_role, activity.id) &&
                (!tab_id || tab_id == activity.id)
            );
        },
        initFirstTab: function(force){
            if(this.selected_activity_tab_id && !force) {
                return;
            }
            const tab = $('#tabs-section li:first-child a')[0];
            if(tab) {
                tab.click();
            }
        },
        initialiseOrgContactTable: function(){
            let vm = this;
            if (vm.application && vm.applicantType == 'org' && !vm.contacts_table_initialised){
                vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations,vm.application.org_applicant.id+'/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
        commaToNewline(s){
            return s.replace(/[,;]/g, '\n');
        },
        proposedDecline: function(){
            this.$refs.proposed_decline.decline = this.application.applicationdeclineddetails != null ? helpers.copyObject(this.application.applicationdeclineddetails): {};
            this.$refs.proposed_decline.isModalOpen = true;
        },
        isActivityVisible: function(activity_id) {
            return isApplicationActivityVisible(this.application, activity_id);
        },
        isAssessorRelevant(assessor, activity_id) {
            if(!activity_id) {
                activity_id = this.selected_activity_tab_id;
            }
            if(!assessor.licence_activities) {
                return false;
            }
            return assessor.licence_activities.filter(
                activity => activity.id == activity_id
            ).length > 0;
        },
        sendtoAssessor: function(item1){
            let vm=this;
            this.$refs.send_to_assessor.assessment.licence_activity=item1;
            this.$refs.send_to_assessor.assessment.assessor_group=this.selectedAssessor.id;
            this.$refs.send_to_assessor.assessment.assessor_group_name=this.selectedAssessor.display_name;
            this.$refs.send_to_assessor.assessment.licence_activity=this.selected_activity_tab_id;
            this.$refs.send_to_assessor.assessment.text='';
            if (typeof this.selectedAssessor.id == 'undefined' || typeof this.selectedAssessor.display_name == 'undefined'){
              swal(
                'Error',
                'Please select an Assessor Group to send the request to.',
                'error'
              )
            } else {
                this.$refs.send_to_assessor.isModalOpen=true;
            }
        },
        clearSendToAssessorForm(){
            this.$refs.send_to_assessor.assessment.text='';
            this.selectedAssessor={};
        },
        hasActivityStatus: function(status_list, status_count=1, required_role=null) {
            if(typeof(status_list) !== 'object') {
                status_list = [status_list];
            }
            const activities_list = this.application.licence_type_data.activity;
            return activities_list.filter(activity =>
                status_list.includes(activity.processing_status.id)
                && (required_role === null || this.userHasRole(required_role, activity.id))
            ).length >= status_count;
        },
        setAssessorTab(_index){
            return _index === 0 ? 'active' : '';
        },
        setAssessorTabContent(_index){
            return _index === 0 ? 'tab-pane fade in active' : 'tab-pane fade in';
        },
        proposedLicence: function(){
            var activity_name=[]
            var selectedTabTitle = $("#tabs-section li.active");

            this.$refs.proposed_licence.propose_issue.licence_activity_id=this.selected_activity_tab_id;
            this.$refs.proposed_licence.propose_issue.licence_activity_name=selectedTabTitle.text();
            this.$refs.proposed_licence.isModalOpen = true;
        },
        toggleIssue:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            this.isofficerfinalisation=true;
        },
        acceptIdRequest: function() {
            let vm = this;
            swal({
                title: "Accept ID Check",
                text: "Are you sure you want to accept this ID Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/accept_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        resetIdRequest: function() {
            let vm = this;
            swal({
                title: "Reset ID Check",
                text: "Are you sure you want to reset this ID Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/reset_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        updateIdRequest: function() {
            let vm = this;
            swal({
                title: "Request Update ID Check",
                text: "Are you sure you want to request this ID Check update?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/request_id_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        acceptCharacterRequest: function() {
            let vm = this;
            swal({
                title: "Accept Character Check",
                text: "Are you sure you want to accept this Character Check?",
                type: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            }).then((result) => {
                if (result.value) {
                    vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/accept_character_check')))
                    .then((response) => {
                        vm.application = response.body;
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        refreshAssessorDatatables: function(){
            var vm = this;
            for (var i=0;i<vm.$refs.assessorDatatable.length;i++){
                vm.$refs.assessorDatatable[i].vmDataTable.ajax.reload();
            }
        },
        amendmentRequest: function(){
            let vm = this;
            vm.save_wo();
            let values = '';
            var activity_name=[];
            var activity_id=[];

            $('.deficiency').each((i,d) => {
                values +=  $(d).val() != '' ? `Question - ${$(d).data('question')}\nDeficiency - ${$(d).val()}\n`: '';
            });

            activity_id.push(vm.selected_activity_tab_id);
            activity_name.push(vm.selected_activity_tab_name);

            vm.$refs.amendment_request.amendment.text = values;
            vm.$refs.amendment_request.amendment.activity_name = activity_name;
            vm.$refs.amendment_request.amendment.activity_id = activity_id;
            vm.$refs.amendment_request.isModalOpen = true;

            if (values === ''){
               swal(
                  'Amendment Request',
                  'There are no deficiencies entered for this Application.',
                  'error'
               )
               vm.$refs.amendment_request.isModalOpen = false;
            }
        },
        togglesendtoAssessor:function(){
            let vm=this;
            $('#tabs-main li').removeClass('active');
            vm.isSendingToAssessor = !vm.isSendingToAssessor;
            vm.showingApplication = false;
            vm.showingConditions = false;
            vm.fetchAssessorGroup();
            vm.initFirstTab(true);
        },
        save: function(e) {
            let vm = this;
            let formData = new FormData(vm.form);
            vm.$http.post(vm.application_form_url,formData).then(res=>{
              swal(
                'Saved',
                'Your application has been saved',
                'success'
              )
            },err=>{
            });
        },
        save_wo: function() {
            let vm = this;
            let formData = new FormData(vm.form);
            vm.$http.post(vm.application_form_url,formData).then(res=>{

            },err=>{
            });
        },
        toggleApplication:function(){
            let vm = this;
            this.showingApplication = !this.showingApplication;
            if(this.isSendingToAssessor){
                this.isSendingToAssessor=!this.isSendingToAssessor
            }
            if(this.showingConditions){
                this.showingConditions=!this.showingConditions
            }
            if(this.isOfficerConditions){
                this.isOfficerConditions=!this.isOfficerConditions
            }
            if(this.isFinalViewConditions){
                this.isFinalViewConditions=!this.isFinalViewConditions
            }
            if(this.isofficerfinalisation){
                this.isofficerfinalisation=!this.isofficerfinalisation
            }
            setTimeout(function(){
                $('#tabs-main li a')[1].click();
                vm.initFirstTab(true);
            }, 50);
        },
        toggleConditions:function(){
            this.showingConditions = true;
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);
        },
        returnToOfficerConditions: function(){
            let vm = this;
            let id = vm.selectedActivity.id;
            vm.updateActivityStatus(id,'with_officer_conditions');
            swal(
                 'Return to Officer - Conditions',
                 'The licenced activity has been returned to Officer - Conditions.',
                 'success'
            );
        },
        toggleOfficerConditions:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=true;
            this.isFinalViewConditions=false;
            this.assessmentComplete=false;
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);

        },
        toggleFinalViewConditions:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.showingConditions=false;
            this.isOfficerConditions=false;
            this.isFinalViewConditions=true;
            this.assessmentComplete=false;
            setTimeout(function(){
                $('#conditiontabs li a')[0].click();
            }, 50);

        },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            $(vm.$refs.assigned_officer).val(vm.application.assigned_officer);
            $(vm.$refs.assigned_officer).trigger('change');
        },
        completeAssessment:function(){
            let vm = this;
            let data = new FormData();

            data.selected_assessment_tab=vm.selected_activity_tab_id;
            data.application_id=vm.application_id
            
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/complete_assessment')),JSON.stringify(data),{emulateJSON:true})
            .then((response) => {
                swal(
                             'Complete Assessment',
                             'The assessment is successfully marked as complete.',
                             'success'
                        );

                vm.application = response.body;
                vm.refreshFromResponse(response)
                vm.showingApplication = true;
                vm.isSendingToAssessor=false;
                vm.showingConditions=false;
                vm.assessmentComplete=true;
                swal(
                     'Complete Assessment',
                     'The assessment has been successfully completed',
                     'success'
                )
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        assignToMe: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assign_to_me')))
            .then((response) => {
                vm.application = response.body;
                vm.original_application = helpers.copyObject(response.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                vm.updateAssignedOfficerSelect();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.original_application = helpers.copyObject(response.body);
            vm.application = helpers.copyObject(response.body);
            if (vm.applicantType == 'org') {
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
            };
            if (vm.applicantType == 'proxy') {
                vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
            };
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        assignOfficer: function(){
            let vm = this;
            let unassign = true;
            let data = {};
            unassign = vm.application.assigned_officer != null && vm.application.assigned_officer != 'undefined' ? false: true;
            data = {'officer_id': vm.application.assigned_officer};
            if (!unassign){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assign_officer')),JSON.stringify(data),{
                    emulateJSON:true
                }).then((response) => {
                    vm.application = response.body;
                    vm.original_application = helpers.copyObject(response.body);
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.application = helpers.copyObject(vm.original_application)
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Application Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
            else{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/unassign_officer')))
                .then((response) => {
                    vm.application = response.body;
                    vm.original_application = helpers.copyObject(response.body);
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                }, (error) => {
                    vm.application = helpers.copyObject(vm.original_application)
                    if (vm.applicantType == 'org') {
                        vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                    };
                    if (vm.applicantType == 'proxy') {
                        vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                    };
                    vm.updateAssignedOfficerSelect();
                    swal(
                        'Application Error',
                        helpers.apiVueResourceError(error),
                        'error'
                    )
                });
            }
        },
        updateActivityStatus: function(activity_id, status){
            let vm = this;
            //vm.isSendingToAssessor = !vm.isSendingToAssessor;
            let data = {
                'activity_id' : activity_id,
                'status': status
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/update_activity_status')),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                vm.application = response.body;
                vm.original_application = helpers.copyObject(response.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
            }, (error) => {
                vm.application = helpers.copyObject(vm.original_application)
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        fetchAssessorGroup: function(){
            let vm = this;
            let data = {'application_id' : vm.application.id };
            vm.loading.push('Fetching assessor group');
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessor_group,'user_list'),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                vm.assessorGroup = response.body;
            },(error) => {
                console.log(error);
            });
        },
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.application.assigned_officer = selected.val();
                vm.assignOfficer();
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.application.assigned_officer = null;
                vm.assignOfficer();
            });
        },
        initialiseSelects: function(){
            let vm = this;
            if (!vm.initialisedSelects){
                vm.initialiseAssignedOfficerSelect();
                vm.initialisedSelects = true;
            }
        },
    },
    mounted: function() {
        let vm = this;
        vm.$nextTick(function () {
            for (var i=0;i<vm.application.licence_type_data.activity.length;i++) {
                var activity_id = vm.application.licence_type_data.activity[i].id
                vm.assessors_options[activity_id] = {
                     language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },
                    responsive: true,
                    ajax: {
                        "url": helpers.add_endpoint_join(api_endpoints.applications,vm.$route.params.application_id+'/assessment_details/?licence_activity='+activity_id),
                        "dataSrc": ''
                    },
                    columns: [
                        {data:'assessor_group.display_name'},
                        {data:'date_last_reminded'},
                        {data:'status.name'},
                        {
                            mRender:function (data,type,full) {
                                let links = '';
                                    if(full.status.id == 'completed'){
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_resend">Resend</a>&nbsp;`;

                                    } else if(full.status.id == 'awaiting_assessment'){
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_remind">Remind</a>&nbsp;`;
                                        links +=  `<a data-assessmentid='${full.id}' class="assessment_recall">Recall</a>&nbsp;`;
                                        // links +=  `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Recall</a><br/>`;
                                    }
                                return links;
                            }}
                    ],
                    processing: true
                }
            }

        });
    },
    updated: function(){
        let vm = this;
        if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            }); 
            vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
            vm.initialiseSelects();
            vm.form = document.forms.new_application;
            vm.eventListeners();
        });
    },
    beforeRouteEnter: function(to, from, next) {

        Vue.http.get(`/api/application/${to.params.application_id}/internal_application.json`).then(res => {
            next(vm => {
            vm.application = res.body;
            vm.original_application = helpers.copyObject(res.body);
            if (vm.applicantType == 'org') {
                vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
            };
            if (vm.applicantType == 'proxy') {
                vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
            };
            });
        },
        err => {
            console.log(err);
        });
    },
    beforeRouteUpdate: function(to, from, next) {
          Vue.http.get(`/api/application/${to.params.application_id}.json`).then(res => {
              next(vm => {
                vm.application = res.body;
                vm.original_application = helpers.copyObject(res.body);
                if (vm.applicantType == 'org') {
                    vm.application.org_applicant.address = vm.application.org_applicant.address != null ? vm.application.org_applicant.address : {};
                };
                if (vm.applicantType == 'proxy') {
                    vm.application.proxy_applicant.address = vm.application.proxy_applicant.address != null ? vm.application.proxy_applicant.address : {};
                };
              });
            },
            err => {
              console.log(err);
            });
    }
}

</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
