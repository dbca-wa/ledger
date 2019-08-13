<template lang="html">
    <div v-if="isApplicationLoaded" class="container" id="internalApplication">
        <div class="row" style="padding-bottom: 50px;">
        <h3>{{ headerLabel }}: {{ application.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
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
                                <div class ="col-sm-12" v-for="item in licence_type_data">
                                    
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

                            <template v-if="isFinalised">
                                <div>
                                    <div class="col-sm-12">
                                        <strong>Application</strong><br/>
                                        <a class="actionBtn" v-if="!showingApplication || !this.unfinishedActivities.length" @click.prevent="toggleApplication({show: true, showFinalised: true})">Show Application</a>
                                        <a class="actionBtn" v-else @click.prevent="toggleApplication({show: false})">Hide Application</a>
                                    </div>
                                    <div class="col-sm-12">
                                        <div class="separator"></div>
                                    </div>
                                </div>
                            </template>
                            <template v-if="isFinalised">
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
                                            <button class="btn btn-primary top-buffer-s col-xs-12" @click.prevent="amendmentRequest()">Request Amendment</button><br/>
                                        </div>
                                    </div>
                                    <div v-if="!applicationIsDraft" class="row">
                                        <div class="col-sm-12">
                                            <button class="btn btn-primary top-buffer-s col-xs-12" @click.prevent="togglesendtoAssessor()">Assessments &amp; Conditions</button><br/>
                                        </div>
                                    </div>
                                    <div v-if="canProposeIssueOrDecline" class="row">
                                        <div class="col-sm-12">
                                            <button class="btn btn-danger top-buffer-s col-xs-12" @click.prevent="proposedDecline()">Propose Decline</button>
                                            <button class="btn btn-success top-buffer-s col-xs-12" @click.prevent="proposedLicence()">Propose Issue</button>
                                        </div>
                                    </div>
                                    <div v-if="canIssueDecline" class="row">
                                        <div class="col-sm-12">
                                            <button v-if="!userIsAssignedOfficer" class="btn btn-success top-buffer-s col-xs-12" @click.prevent="toggleIssue()">Issue/Decline</button>
                                            <button v-else disabled class="btn btn-success top-buffer-s col-xs-12">Issue/Decline</button>
                                        </div>
                                    </div>
                                </template>
                                <template v-else>
                                    <div class="row">
                                        <div class="col-sm-12">
                                            <strong>Action</strong><br/>
                                        </div>
                                    </div>
                                    <div v-if="isSendingToAssessor || isOfficerConditions || isofficerfinalisation" class="row">
                                        <div class="col-sm-12">
                                            <button class="btn btn-primary top-buffer-s col-xs-12" @click.prevent="toggleApplication({show: true})">Back to Application</button><br/>
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
                    <LicenceScreen/>
                </template>
                <template v-if="canIssueDecline && isofficerfinalisation">
                    <IssueLicence :application="application" :licence_activity_tab="selected_activity_tab_id"/>
                </template>

                <ApplicationAssessments
                    v-if="isSendingToAssessor || isOfficerConditions"
                    />

                <template v-if="applicationDetailsVisible">
                    <div>
                    <ul class="nav nav-tabs" id="tabs-main">
                        <li><a ref="applicantTab" data-toggle="tab" :href="'#'+applicantTab">Applicant</a></li>
                        <li><a ref="applicationTab" data-toggle="tab" :href="'#'+applicationTab">Application</a></li>
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
                                        <button v-if="isIdNotChecked" :disabled="application.proxy_applicant" class="btn btn-primary" @click.prevent="updateIdRequest()">Request Update</button>
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
                                <Application form_width="inherit" :withSectionsSelector="false" v-if="isApplicationLoaded">
                                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                    <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                                    <input type='hidden' name="application_id" :value="1" />
                                    <input type='hidden' id="selected_activity_tab_id" v-model="selected_activity_tab_id" />
                                    <div v-if="showNavBarBottom" class="row" style="margin-bottom:50px;">
                                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                                            <div class="navbar-inner">
                                                <div class="container">
                                                    <p class="pull-right" style="margin-top:5px;">
                                                        <button v-if="canReturnToConditions" class="btn btn-primary" @click.prevent="returnToOfficerConditions()">Return to Officer - Conditions</button>
                                                        <button v-if="!applicationIsDraft && canSaveApplication" class="btn btn-primary" @click.prevent="save()">Save Changes</button>
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
        <ProposedDecline ref="proposed_decline" @refreshFromResponse="refreshFromResponse"></ProposedDecline>
        <AmendmentRequest ref="amendment_request" @refreshFromResponse="refreshFromResponse"></AmendmentRequest>
        <ProposedLicence ref="proposed_licence" @refreshFromResponse="refreshFromResponse"></ProposedLicence>

    </div>
</div>
</template>
<script>
import Application from '../../form.vue';
import Vue from 'vue';
import { mapActions, mapGetters } from 'vuex'
import ProposedDecline from './application_proposed_decline.vue';
import AmendmentRequest from './amendment_request.vue';
import ApplicationAssessments from './application_assessments.vue';
import datatable from '@vue-utils/datatable.vue';
import ProposedLicence from './proposed_issuance.vue';
import IssueLicence from './application_issuance.vue';
import LicenceScreen from './application_licence.vue';
import CommsLogs from '@common-components/comms_logs.vue';
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js";
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
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
            isSendingToAssessor: false,
            assessorGroup:{},
            "selectedAssessor":{},
            "loading": [],
            form: null,
            // activity_data:[],
            contacts_table_initialised: false,
            initialisedSelects: false,
            showingApplication:true,
            isOfficerConditions:false,
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
        ApplicationAssessments,
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
        ...mapGetters([
            'application',
            'original_application',
            'licence_type_data',
            'selected_activity_tab_id',
            'selected_activity_tab_name',
            'hasRole',
            'visibleConditionsFor',
            'checkActivityStatus',
            'isPartiallyFinalised',
            'isFinalised',
            'licenceActivities',
            'isApplicationLoaded',
            'isApplicationActivityVisible',
            'unfinishedActivities',
            'current_user',
        ]),
        applicationDetailsVisible: function() {
            return !this.isSendingToAssessor && !this.isofficerfinalisation && this.unfinishedActivities.length && !this.isOfficerConditions;
        },
        applicationIsDraft: function(){
            return this.application.processing_status.id == 'draft';
        },
        selectedActivity: function(){
            var activities_list = this.licence_type_data.activity
            for(let activity of activities_list){
                if(activity.id == this.selected_activity_tab_id){
                    return activity;
                }
            }
            return null;
        },
        canIssueDecline: function(){
            var activities_list = this.licence_type_data.activity;
            for(let activity of activities_list){
                if(['with_officer_finalisation', 'awaiting_licence_fee_payment'].includes(activity.processing_status.id) &&
                    this.userHasRole('issuing_officer', activity.id)){
                        return true;
                }
            }
            return false;
        },
        canSaveApplication: function() {
            // Assessors can save the Assessor Comments field.
            if(this.selected_activity_tab_id &&
                this.userHasRole('assessor', this.selected_activity_tab_id) &&
                this.selectedActivity.processing_status.id == 'with_assessor') {
                    return true;
            }

            // Licensing officers can save officer comments.
            return this.canRequestAmendment;
        },
        canRequestAmendment: function(){
            var activities_list = this.licence_type_data.activity
            for(let activity of activities_list){
                if(activity.processing_status.id == 'with_officer' &&
                    this.userHasRole('licensing_officer', activity.id)){
                        return true;
                }
            }
            return false;
        },
        canReturnToConditions: function(){
            if(!this.userHasRole('issuing_officer', this.selected_activity_tab_id)) {
                return false;
            }
            return this.selected_activity_tab_id && this.selectedActivity.processing_status.id == 'with_officer_finalisation' ? true : false;
        },
        canProposeIssueOrDecline: function(){
            return this.hasActivityStatus('with_officer_conditions', 1, 'licensing_officer');
        },
        contactsURL: function(){
            return this.application!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.application.org_applicant.id+'/contacts') : '';
        },
        applicantType: function(){
            return this.$store.getters.applicant_type;
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
        userIsAssignedOfficer: function(){
            return this.current_user.id == this.application.assigned_officer;
        },
        form_data_comments_url: function() {
            return (this.application) ? `/api/application/${this.application.id}/officer_comments.json` : '';
        },
        headerLabel: function() {
            switch(this.application.application_type.id) {
                case 'amend_activity':
                    return 'Application - Activity Amendment';
                break;
                case 'renew_activity':
                    return 'Application - Activity Renewal';
                break;
                default:
                    return 'Application'
                break;
            }
        },
        showNavBarBottom: function() {
            return this.canReturnToConditions || (!this.applicationIsDraft && this.canSaveApplication)
        }
    },
    methods: {
        ...mapActions({
            load: 'loadApplication',
            revert: 'revertApplication',
        }),
        ...mapActions([
            'setOriginalApplication',
            'setApplication',
            'setActivityTab',
            'loadCurrentUser',
            'toggleFinalisedTabs',
            'saveFormData',
        ]),
        eventListeners: function(){
            let vm = this;
            $("[data-target!=''][data-target]").off("click").on("click", function (e) {
                vm.setActivityTab({
                    id: parseInt($(this).data('target').replace('#', ''), 10),
                    name: $(this).text()
                });
            });
            this.initFirstTab();
        },
        userHasRole: function(role, activity_id) {
            return this.hasRole(role, activity_id);
        },
        getVisibleConditionsFor: function(for_role, processing_status, tab_id) {
            return this.visibleConditionsFor(for_role, processing_status, tab_id);
        },
        initFirstTab: function(force){
            if(this.selected_activity_tab_id && !force) {
                return;
            }
            const tab = $('#tabs-section li:first-child a')[0];
            if(tab) {
                tab.click();
            }
            else {
                this.licenceActivities().filter(activity => {
                    this.setActivityTab({
                        id: activity.id,
                        name: activity.name
                    });
                })
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
            this.save_wo();
            this.$refs.proposed_decline.isModalOpen = true;
        },
        isActivityVisible: function(activity_id) {
            return this.isApplicationActivityVisible({activity_id: activity_id});
        },
        hasActivityStatus: function(status_list, status_count=1, required_role=null) {
            return this.checkActivityStatus(status_list, status_count, required_role);
        },
        proposedLicence: function(){
            var activity_name=[]
            var selectedTabTitle = $("#tabs-section li.active");
            this.save_wo();
            this.$refs.proposed_licence.propose_issue.licence_activity_id=this.selected_activity_tab_id;
            this.$refs.proposed_licence.propose_issue.licence_activity_name=selectedTabTitle.text();
            this.$refs.proposed_licence.isModalOpen = true;
            this.$refs.proposed_licence.preloadLastActivity();
        },
        toggleIssue:function(){
            this.save_wo();
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.isOfficerConditions=false;
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
                        vm.setApplication(response.body);
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
                        vm.setApplication(response.body);
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
                        vm.setApplication(response.body);
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
                        vm.setApplication(response.body);
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        amendmentRequest: function(){
            let vm = this;
            vm.save_wo();

            vm.$refs.amendment_request.amendment.text = '';
            vm.$refs.amendment_request.isModalOpen = true;
        },
        togglesendtoAssessor:function(){
            this.save_wo();
            $('#tabs-main li').removeClass('active');
            this.isSendingToAssessor = !this.isSendingToAssessor;
            this.showingApplication = false;
        },
        save: function(props = { showNotification: true }) {
            const { showNotification } = props;
            this.saveFormData({ url: this.form_data_comments_url }).then(response => {
                showNotification && swal(
                    'Saved',
                    'Your application has been saved',
                    'success'
                )
            }, error => {
                console.log('Failed to save comments: ', error);
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        save_wo: function() {
            return this.save({ showNotification: false });
        },
        toggleApplication: function({show=false, showFinalised=false}){

            this.showingApplication = show;
            if(this.isSendingToAssessor){
                this.isSendingToAssessor = !show;
            }
            if(this.isOfficerConditions){
                this.isOfficerConditions = !show;
            }
            if(this.isofficerfinalisation){
                this.isofficerfinalisation = !show;
            }
            this.toggleFinalisedTabs(showFinalised);
            setTimeout(() => {
                const firstTab = $('#tabs-main li a')[1];
                if(firstTab != null) {
                    firstTab.click();
                }
                this.initFirstTab(true);
            }, 50);
            !showFinalised && this.load({ url: `/api/application/${this.application.id}/internal_application.json` });
        },
        toggleConditions:function(){
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.isOfficerConditions=false;
        },
        returnToOfficerConditions: function(){

            swal({
                title: 'Return to Officer - Conditions',
                html:`
                    Please provide the reason for returning this licensed activity back to officer for review.
                    <br>This will be emailed to the licensing officer.
                `,
                input: 'text',
                inputAttributes: {
                    autocapitalize: 'off'
                },
                showCancelButton: true,
                confirmButtonText: 'Return',
                }).then((result) => {
                    if(!result.value) {
                        return;
                    }
                    const text = result.value;
                    const data = {
                        "activity_id" : this.selectedActivity.id,
                        "text": text
                    }
                    this.$http.post(helpers.add_endpoint_json(
                            api_endpoints.applications, (this.application.id+'/return_to_officer')
                        ), JSON.stringify(data)).then((response) => {
                        swal(
                            'Return to Officer - Conditions',
                            'The licenced activity has been returned to Officer - Conditions.',
                            'success'
                        );
                        this.refreshFromResponse(response);
                    }, (error) => {
                        this.revert();
                        swal(
                            'Application Error',
                            helpers.apiVueResourceError(error),
                            'error'
                        )
                    });
                })
        },
        toggleOfficerConditions:function(){
            this.save_wo();
            this.showingApplication = false;
            this.isSendingToAssessor=false;
            this.isOfficerConditions=true;

        },
        updateAssignedOfficerSelect:function(){
            let vm = this;
            $(vm.$refs.assigned_officer).val(vm.application.assigned_officer);
            $(vm.$refs.assigned_officer).trigger('change');
        },
        assignToMe: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/assign_to_me')))
            .then((response) => {
                this.refreshFromResponse(response);
                vm.updateAssignedOfficerSelect();
            }, (error) => {
                vm.revert();
                vm.updateAssignedOfficerSelect();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        refreshFromResponse:function(response){
            this.setOriginalApplication(response.body);
            this.setApplication(response.body);
            this.$nextTick(() => {
                this.initialiseAssignedOfficerSelect(true);
                this.updateAssignedOfficerSelect();
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
                    this.refreshFromResponse(response);
                    this.updateAssignedOfficerSelect();
                }, (error) => {
                    this.revert();
                    this.updateAssignedOfficerSelect();
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
                    this.refreshFromResponse(response);
                    this.updateAssignedOfficerSelect();
                }, (error) => {
                    this.revert();
                    this.updateAssignedOfficerSelect();
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
            let data = {
                'activity_id' : activity_id,
                'status': status
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,(vm.application.id+'/update_activity_status')),JSON.stringify(data),{
                emulateJSON:true,
            }).then((response) => {
                this.refreshFromResponse(response);
            }, (error) => {
                this.revert();
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        initialiseAssignedOfficerSelect: function(reinit=false){
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
            if (!this.initialisedSelects){
                this.initialiseAssignedOfficerSelect();
                this.initialisedSelects = true;
                this.initMainTab();
            }
        },
        initMainTab: function() {
            if(!this.$refs.applicantTab) {
                return;
            }
            this.$refs.applicantTab.click();
            this.initFirstTab(true);
        }
    },
    mounted: function() {
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
        next(vm => {
            vm.load({ url: `/api/application/${to.params.application_id}/internal_application.json` }).then(() => {
            });
            vm.loadCurrentUser({ url: `/api/my_user_details` });
        });
    },
    beforeRouteUpdate: function(to, from, next) {
        next(vm => {
            vm.load({ url: `/api/application/${to.params.application_id}.json` }).then(() => {
            });
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
