import re
from django.db import transaction
from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser, Document
from commercialoperator.components.proposals.models import ProposalDocument, ProposalPark, ProposalParkActivity, ProposalParkAccess, ProposalTrail, ProposalTrailSectionActivity, ProposalTrailSection, ProposalParkZone, ProposalParkZoneActivity
from commercialoperator.components.proposals.serializers import SaveProposalSerializer, SaveProposalParkSerializer, SaveProposalTrailSerializer
from commercialoperator.components.main.models import Activity, Park, AccessType, Trail, Section, Zone
import traceback
import os

def create_data_from_form(schema, post_data, file_data, post_data_index=None,special_fields=[],assessor_data=False):
    data = {}
    special_fields_list = []
    assessor_data_list = []
    comment_data_list = {}
    special_fields_search = SpecialFieldsSearch(special_fields)
    if assessor_data:
        assessor_fields_search = AssessorDataSearch()
        comment_fields_search = CommentDataSearch()
    try:
        for item in schema:
            #import ipdb; ipdb.set_trace()
            data.update(_create_data_from_item(item, post_data, file_data, 0, ''))
            #_create_data_from_item(item, post_data, file_data, 0, '')
            special_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
            if assessor_data:
                assessor_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
                comment_fields_search.extract_special_fields(item, post_data, file_data, 0, '')
        special_fields_list = special_fields_search.special_fields
        if assessor_data:
            assessor_data_list = assessor_fields_search.assessor_data
            comment_data_list = comment_fields_search.comment_data
    except:
        traceback.print_exc()
    if assessor_data:
        return [data],special_fields_list,assessor_data_list,comment_data_list

    return [data],special_fields_list


def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)

def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if 'name' in item:
        extended_item_name = item['name']
    else:
        raise Exception('Missing name in item %s' % item['label'])

    #import ipdb; ipdb.set_trace()
    if 'children' not in item:
        if item['type'] in ['checkbox' 'declaration']:
            #item_data[item['name']] = post_data[item['name']]
            #import ipdb; ipdb.set_trace()
            item_data[item['name']] = extended_item_name in post_data
        elif item['type'] == 'file':
            if extended_item_name in file_data:
                item_data[item['name']] = str(file_data.get(extended_item_name))
                # TODO save the file here
            elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                item_data[item['name']] = post_data.get(extended_item_name + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            if extended_item_name in post_data:
                if item['type'] == 'multi-select':
                    item_data[item['name']] = post_data.getlist(extended_item_name)
                else:
                    item_data[item['name']] = post_data.get(extended_item_name)
    else:
        if 'repetition' in item:
            item_data = generate_item_data(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
        else:
            #import ipdb; ipdb.set_trace()
            item_data = generate_item_data(extended_item_name, item, item_data, post_data, file_data,1,suffix)


    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child in item['conditions'][condition]:
                item_data.update(_create_data_from_item(child, post_data, file_data, repetition, suffix))

    #import ipdb; ipdb.set_trace()
    return item_data

def generate_item_data(item_name,item,item_data,post_data,file_data,repetition,suffix):
    item_data_list = []
    for rep in xrange(0, repetition):
        #import ipdb; ipdb.set_trace()
        child_data = {}
        for child_item in item.get('children'):
            child_data.update(_create_data_from_item(child_item, post_data, file_data, 0,
                                                     '{}-{}'.format(suffix, rep)))
        item_data_list.append(child_data)

        item_data[item['name']] = item_data_list
    return item_data

class AssessorDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.assessor_data = []

    def extract_assessor_data(self,item,post_data):
        values = []
        res = {
            'name': item,
            'assessor': '',
            'referrals':[]
        }
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}-'.format(item))
                    if len(parts) > 1:
                        # split parts to see if referall
                        ref_parts = parts[1].split('Referral-')
                        if len(ref_parts) > 1:
                            # Referrals
                            res['referrals'].append({
                                'value':v,
                                'email':ref_parts[1],
                                'full_name': EmailUser.objects.get(email=ref_parts[1]).get_full_name()
                            })
                        elif k.split('-')[-1].lower() == 'assessor':
                            # Assessor
                            res['assessor'] = v

        return res

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            if 'conditions' in item:
                for condition in item['conditions'].keys():
                    for child in item['conditions'][condition]:
                        item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

            if item.get(self.lookup_field):
                self.assessor_data.append(self.extract_assessor_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)

            if 'conditions' in item:
                for condition in item['conditions'].keys():
                    for child in item['conditions'][condition]:
                        item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

class CommentDataSearch(object):

    def __init__(self,lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.comment_data = {}

    def extract_comment_data(self,item,post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item,k):
                values.append({k:post_data[k]})
        if values:
            for v in values:
                for k,v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-comment-field')
                        if len(ref_parts) > 1:
                            res = {'{}'.format(item):v}
        return res

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            self.comment_data.update(self.extract_comment_data(extended_item_name,post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

class SpecialFieldsSearch(object):

    def __init__(self,lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(self,item, post_data, file_data, repetition, suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            for f in self.lookable_fields:
                if item['type'] in ['checkbox' 'declaration']:
                    val = None
                    val = item.get(f,None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f,None)
                        if val:
                            if item['type'] == 'multi-select':
                                item_data[f] = ','.join(post_data.getlist(extended_item_name))
                            else:
                                item_data[f] = post_data.get(extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(extended_item_name,item,item_data,post_data,file_data,len(post_data[item['name']]),suffix)
            else:
                item_data = self.generate_item_data_special_field(extended_item_name, item, item_data, post_data, file_data,1,suffix)


        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(self.extract_special_fields(child, post_data, file_data, repetition, suffix))

        return item_data

    def generate_item_data_special_field(self,item_name,item,item_data,post_data,file_data,repetition,suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

def save_park_activity_data(instance,select_parks_activities):
    with transaction.atomic():
        try:
            if select_parks_activities:
                try:
                    #current_parks=instance.parks.all()
                    selected_parks=[]
                    for item in select_parks_activities:
                        if item['park']:
                            selected_parks.append(item['park'])
                            try:
                                #Check if PrposalPark record already exists. If exists, check for activities
                                park=ProposalPark.objects.get(park=item['park'],proposal=instance)
                                current_activities=park.land_activities.all()
                                current_activities_id=[a.activity_id for a in current_activities]
                                #Get the access records related to ProposalPark
                                current_access=park.access_types.all()
                                current_access_id=[a.access_type_id for a in current_access]
                                if item['activities']:
                                    for a in item['activities']:
                                        if a in current_activities_id:
                                            #if activity already exists then pass otherwise create the record.
                                            pass
                                        else:
                                            try:
                                                #TODO add logging
                                                if a not in park.park.allowed_activities_ids:
                                                    #raise Exception('Activity not allowed for this park')
                                                    pass
                                                else:    
                                                    activity=Activity.objects.get(id=a)
                                                    ProposalParkActivity.objects.create(proposal_park=park, activity=activity)
                                            except:
                                                raise
                                if item['access']:
                                    for a in item['access']:
                                        if a in current_access_id:
                                            #if access type already exists then pass otherwise create the record.
                                            pass
                                        else:
                                            try:
                                                #TODO add logging
                                                access=AccessType.objects.get(id=a)
                                                ProposalParkAccess.objects.create(proposal_park=park, access_type=access)
                                            except:
                                                raise
                            except ProposalPark.DoesNotExist:
                                try:
                                    #If ProposalPark does not exists then create a new record and activities for it.
                                    park_instance=Park.objects.get(id=item['park'])
                                    park=ProposalPark.objects.create(park=park_instance, proposal=instance)
                                    current_activities=[]
                                    for a in item['activities']:
                                        try:
                                            if a not in park.park.allowed_activities_ids:
                                                    #raise Exception('Activity not allowed for this park')
                                                    pass
                                            else:
                                                activity=Activity.objects.get(id=a)
                                                ProposalParkActivity.objects.create(proposal_park=park, activity=activity)
                                        except:
                                            raise
                                    for a in item['access']:
                                        try:
                                            access=AccessType.objects.get(id=a)
                                            ProposalParkAccess.objects.create(proposal_park=park, access_type=access)
                                        except:
                                            raise   
                                except:
                                    raise
                            #compare all activities (new+old) with the list of activities selected activities to get
                            #the list of deleted activities.
                            new_activities=park.land_activities.all()
                            new_activities_id=set(a.activity_id for a in new_activities)
                            diff_activity=set(new_activities_id).difference(set(item['activities']))
                            for d in diff_activity:
                                act=ProposalParkActivity.objects.get(activity_id=d, proposal_park=park)
                                act.delete()
                            new_access=park.access_types.all()
                            new_access_id=set(a.access_type_id for a in new_access)
                            diff_access=set(new_access_id).difference(set(item['access']))
                            for d in diff_access:
                                acc=ProposalParkAccess.objects.get(access_type_id=d, proposal_park=park)
                                acc.delete()
                    new_parks=instance.parks.filter(park__park_type='land')
                    new_parks_id=set(p.park_id for p in new_parks)
                    diff_parks=set(new_parks_id).difference(set(selected_parks))
                    for d in diff_parks:
                        pk=ProposalPark.objects.get(park=d, proposal=instance)
                        pk.delete()
                except:
                    raise
        except:
            raise


def save_trail_section_activity_data(instance,select_trails_activities):
    with transaction.atomic():
        try:
            if select_trails_activities:
                try:
                    #current_parks=instance.parks.all()
                    selected_trails=[]
                    #print("selected_trails",selected_trails)
                    for item in select_trails_activities:
                        if item['trail']:
                            selected_trails.append(item['trail'])
                            selected_sections=[]
                            try:
                                #Check if PrposalPark record already exists. If exists, check for sections
                                trail=ProposalTrail.objects.get(trail=item['trail'],proposal=instance)
                                current_sections=trail.sections.all()
                                current_sections_ids=[a.section_id for a in current_sections]
                                if item['activities']:
                                    for a in item['activities']:
                                        if a['section']:
                                            selected_sections.append(a['section'])
                                            if a['section'] in current_sections_ids:
                                                section=ProposalTrailSection.objects.get(proposal_trail=trail, section=a['section'])
                                                current_activities=section.trail_activities.all()
                                                current_activities_id=[s.activity_id for s in current_activities]
                                                if a['activities']:
                                                    for act in a['activities']:
                                                        if act in current_activities_id:
                                                            #if activity already exists then pass otherwise create the record.
                                                            pass
                                                        else:
                                                            try:
                                                                activity=Activity.objects.get(id=act)
                                                                ProposalTrailSectionActivity.objects.create(trail_section=section, activity=activity)
                                                            except:
                                                                raise                                                   
                                            else:
                                                section_instance=Section.objects.get(id=a['section'])
                                                section=ProposalTrailSection.objects.create(proposal_trail=trail, section=section_instance)
                                                if a['activities']:
                                                    for act in a['activities']:                            
                                                        try:
                                                            activity=Activity.objects.get(id=act)
                                                            ProposalTrailSectionActivity.objects.create(trail_section=section, activity=activity)
                                                        except:
                                                            raise
                                            new_activities=section.trail_activities.all()
                                            new_activities_id=set(n.activity_id for n in new_activities)
                                            diff_activity=set(new_activities_id).difference(set(a['activities']))
                                            #print("trail:",trail.trail_id,"section:",section.section_id,"new_activities:",new_activities_id, "diff:", diff_activity)
                                            for d in diff_activity:
                                                act=ProposalTrailSectionActivity.objects.get(activity_id=d, trail_section=section)
                                                act.delete()
                            except ProposalTrail.DoesNotExist:
                                try:
                                    #If ProposalPark does not exists then create a new record and activities for it.
                                    trail_instance=Trail.objects.get(id=item['trail'])
                                    trail=ProposalTrail.objects.create(trail=trail_instance, proposal=instance)
                                    current_sections=[]
                                    if item['activities']:
                                        for a in item['activities']:
                                            if a['section']:
                                                selected_sections.append(a['section'])
                                                section_instance=Section.objects.get(id=a['section'])
                                                section=ProposalTrailSection.objects.create(proposal_trail=trail, section=section_instance)
                                                if a['activities']:
                                                    for act in a['activities']:                            
                                                        try:
                                                            activity=Activity.objects.get(id=act)
                                                            ProposalTrailSectionActivity.objects.create(trail_section=section, activity=activity)
                                                        except:
                                                            raise
                                            #Just to check the new activities. Next 3 lines can be deleted.                                            
                                            new_activities=section.trail_activities.all()
                                            new_activities_id=set(nw.activity_id for nw in new_activities)
                                            diff_activity=set(new_activities_id).difference(set(a['activities']))
                                            #print("not deleting","trail:",trail.trail_id,"section:",section.section_id,"new_activities:",new_activities_id, "diff:", diff_activity)                               
                                except:
                                    raise
                            #compare all sections (new+old) with the list of sections selected to get
                            #the list of deleted sections.
                            new_sections=trail.sections.all()
                            new_sections_ids=set(a.section_id for a in new_sections)
                            diff_sections=set(new_sections_ids).difference(set(selected_sections))
                            #print("trail:",trail.trail_id, "new_sections:", new_sections_ids,"diff_sections:", diff_sections)
                            for d in diff_sections:
                                    pk=ProposalTrailSection.objects.get(section=d, proposal_trail=trail)
                                    pk.delete()
                    new_trails=instance.trails.all()
                    new_trails_id=set(p.trail_id for p in new_trails)
                    diff_trails=set(new_trails_id).difference(set(selected_trails))
                    #print("new_trails", new_trails_id, "diff:", diff_trails)
                    for d in diff_trails:
                        pk=ProposalTrail.objects.get(trail=d, proposal=instance)
                        pk.delete()
                except:
                    raise
        except:
            raise


#save marine parks and activities for Tclass license to be deleted.
def save_marine_park_activity_data(instance,marine_parks_activities):
    with transaction.atomic():
        try:
            if marine_parks_activities:
                try:
                    #current_parks=instance.parks.all()
                    selected_parks=[]
                    for item in marine_parks_activities:
                        #import ipdb; ipdb.set_trace()
                        if item['park']:
                            selected_parks.append(item['park'])
                            try:
                                #Check if PrposalPark record already exists. If exists, check for activities
                                park=ProposalPark.objects.get(park=item['park'],proposal=instance)
                                current_activities=park.marine_activities.all()
                                current_activities_id=[a.activity_id for a in current_activities]
                                if item['activities']:
                                    for a in item['activities']:
                                        if a in current_activities_id:
                                            #if activity already exists then pass otherwise create the record.
                                            pass
                                        else:
                                            try:
                                                #TODO add logging
                                                if a in park.park.allowed_activities_ids:
                                                    #raise Exception('Activity not allowed for this park')
                                                    pass
                                                else:    
                                                    activity=Activity.objects.get(id=a)
                                                    ProposalParkActivity.objects.create(proposal_park=park, activity=activity)
                                            except:
                                                raise                                
                            except ProposalPark.DoesNotExist:
                                try:
                                    #If ProposalPark does not exists then create a new record and activities for it.
                                    park_instance=Park.objects.get(id=item['park'])
                                    park=ProposalPark.objects.create(park=park_instance, proposal=instance)
                                    current_activities=[]
                                    for a in item['activities']:
                                        try:
                                            if a in park.park.allowed_activities_ids:
                                                    #raise Exception('Activity not allowed for this park')
                                                    pass
                                            else:
                                                activity=Activity.objects.get(id=a)
                                                ProposalParkActivity.objects.create(proposal_park=park, activity=activity)
                                        except:
                                            raise                                    
                                except:
                                    raise
                            #compare all activities (new+old) with the list of activities selected activities to get
                            #the list of deleted activities.
                            new_activities=park.marine_activities.all()
                            new_activities_id=set(a.activity_id for a in new_activities)
                            diff_activity=set(new_activities_id).difference(set(item['activities']))
                            #print('new activities:', new_activities_id, 'diff_activity:',diff_activity)
                            for d in diff_activity:
                                act=ProposalParkActivity.objects.get(activity_id=d, proposal_park=park)
                                act.delete()                            
                    new_parks=instance.parks.filter(park__park_type='marine')
                    new_parks_id=set(p.park_id for p in new_parks)
                    diff_parks=set(new_parks_id).difference(set(selected_parks))
                    #print('new parks:', new_parks_id, 'diff_parks:', diff_parks)
                    for d in diff_parks:
                        pk=ProposalPark.objects.get(park=d, proposal=instance)
                        pk.delete()
                except:
                    raise
        except:
            raise

#Save Marine parks, zones and related activity for TClass license
def save_park_zone_activity_data(instance,marine_parks_activities):
    with transaction.atomic():
        try:
            if marine_parks_activities:
                try:
                    #current_parks=instance.parks.all()
                    selected_parks=[]
                    #print("selected_parks",selected_parks)
                    for item in marine_parks_activities:
                        if item['park']:
                            selected_parks.append(item['park'])
                            selected_zones=[]
                            try:
                                #Check if PrposalPark record already exists. If exists, check for zones
                                park=ProposalPark.objects.get(park=item['park'],proposal=instance)
                                current_zones=park.zones.all()
                                current_zones_ids=[a.zone_id for a in current_zones]
                                if item['activities']:
                                    for a in item['activities']:
                                        if a['zone']:
                                            selected_zones.append(a['zone'])
                                            if a['zone'] in current_zones_ids:
                                                zone=ProposalParkZone.objects.get(proposal_park=park, zone=a['zone'])
                                                current_activities=zone.park_activities.all()
                                                current_activities_id=[s.activity_id for s in current_activities]
                                                if a['activities']:
                                                    for act in a['activities']:
                                                        if act in current_activities_id:
                                                            #if activity already exists then pass otherwise create the record.
                                                            pass
                                                        else:
                                                            try:
                                                                activity=Activity.objects.get(id=act)
                                                                ProposalParkZoneActivity.objects.create(park_zone=zone, activity=activity)
                                                            except:
                                                                raise                                                   
                                            else:
                                                zone_instance=Zone.objects.get(id=a['zone'])
                                                zone=ProposalParkZone.objects.create(proposal_park=park, zone=zone_instance)
                                                if a['activities']:
                                                    for act in a['activities']:                            
                                                        try:
                                                            activity=Activity.objects.get(id=act)
                                                            ProposalParkZoneActivity.objects.create(park_zone=zone, activity=activity)
                                                        except:
                                                            raise
                                            new_activities=zone.park_activities.all()
                                            new_activities_id=set(n.activity_id for n in new_activities)
                                            diff_activity=set(new_activities_id).difference(set(a['activities']))
                                            print("park:",park.park_id,"zone:",zone.zone_id,"new_activities:",new_activities_id, "diff:", diff_activity)
                                            for d in diff_activity:
                                                act=ProposalParkZoneActivity.objects.get(activity_id=d, park_zone=zone)
                                                act.delete()
                            except ProposalPark.DoesNotExist:
                                try:
                                    #If ProposalPark does not exists then create a new record and activities for it.
                                    park_instance=Park.objects.get(id=item['park'])
                                    park=ProposalPark.objects.create(park=park_instance, proposal=instance)
                                    current_zones=[]
                                    if item['activities']:
                                        for a in item['activities']:
                                            if a['zone']:
                                                selected_zones.append(a['zone'])
                                                zone_instance=Zone.objects.get(id=a['zone'])
                                                zone=ProposalParkZone.objects.create(proposal_park=park, zone=zone_instance)
                                                if a['activities']:
                                                    for act in a['activities']:                            
                                                        try:
                                                            activity=Activity.objects.get(id=act)
                                                            ProposalParkZoneActivity.objects.create(park_zone=zone, activity=activity)
                                                        except:
                                                            raise
                                            #Just to check the new activities. Next 3 lines can be deleted.                                            
                                            new_activities=zone.park_activities.all()
                                            new_activities_id=set(nw.activity_id for nw in new_activities)
                                            diff_activity=set(new_activities_id).difference(set(a['activities']))
                                            print("not deleting","park:",park.park_id,"zone:",zone.zone_id,"new_activities:",new_activities_id, "diff:", diff_activity)                               
                                except:
                                    raise
                            #compare all zones (new+old) with the list of zones selected to get
                            #the list of deleted zones.
                            new_zones=park.zones.all()
                            new_zones_ids=set(a.zone_id for a in new_zones)
                            diff_zones=set(new_zones_ids).difference(set(selected_zones))
                            print("park:",park.park_id, "new_zones:", new_zones_ids,"diff_zones:", diff_zones)
                            for d in diff_zones:
                                    pk=ProposalParkZone.objects.get(zone=d, proposal_park=park)
                                    pk.delete()
                    new_parks=instance.parks.filter(park__park_type='marine')
                    new_parks_id=set(p.park_id for p in new_parks)
                    diff_parks=set(new_parks_id).difference(set(selected_parks))
                    print("new_parks", new_parks_id, "diff:", diff_parks)
                    for d in diff_parks:
                        pk=ProposalPark.objects.get(park=d, proposal=instance)
                        pk.delete()
                except:
                    raise
        except:
            raise

def save_proponent_data(instance,request,viewset,select_parks_activities,select_trails_activities, marine_parks_activities):
    with transaction.atomic():
        try:
#            lookable_fields = ['isTitleColumnForDashboard','isActivityColumnForDashboard','isRegionColumnForDashboard']
#            extracted_fields,special_fields = create_data_from_form(instance.schema, request.POST, request.FILES, special_fields=lookable_fields)
#            instance.data = extracted_fields
#            #import ipdb; ipdb.set_trace()
#            data = {
#                #'region': special_fields.get('isRegionColumnForDashboard',None),
#                'title': special_fields.get('isTitleColumnForDashboard',None),
#                'activity': special_fields.get('isActivityColumnForDashboard',None),
#
#                'data': extracted_fields,
#                'processing_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.processing_status,
#                'customer_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.customer_status,
#            }
            data = {}

            #import ipdb; ipdb.set_trace()
            # s=request.data.get('selected')
            # print type(s)
            serializer = SaveProposalSerializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            if select_parks_activities:
                try:
                    save_park_activity_data(instance, select_parks_activities)                        
                except:
                    raise
            if select_trails_activities:
                try:
                    save_trail_section_activity_data(instance, select_trails_activities)                    
                except:
                    raise
            if marine_parks_activities:
                try:
                    save_park_zone_activity_data(instance, marine_parks_activities)                    
                except:
                    raise
        except:
            raise

def save_assessor_data(instance,request,viewset):
    with transaction.atomic():
        try:
            lookable_fields = ['isTitleColumnForDashboard','isActivityColumnForDashboard','isRegionColumnForDashboard']
            extracted_fields,special_fields,assessor_data,comment_data = create_data_from_form(
                instance.schema, request.POST, request.FILES,special_fields=lookable_fields,assessor_data=True)
            data = {
                'data': extracted_fields,
                'assessor_data': assessor_data,
                'comment_data': comment_data,
            }
            serializer = SaveProposalSerializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            # Save Documents
            for f in request.FILES:
                try:
                    #document = instance.documents.get(name=str(request.FILES[f]))
                    document = instance.documents.get(input_name=f)
                except ProposalDocument.DoesNotExist:
                    document = instance.documents.get_or_create(input_name=f)[0]
                document.name = str(request.FILES[f])
                if document._file and os.path.isfile(document._file.path):
                    os.remove(document._file.path)
                document._file = request.FILES[f]
                document.save()
            # End Save Documents
        except:
            raise

def clone_proposal_with_status_reset(proposal):
    with transaction.atomic():
        try:
            proposal.customer_status = 'draft'
            proposal.processing_status = 'draft'
            proposal.assessor_data = {}
            proposal.comment_data = {}

            #proposal.id_check_status = 'not_checked'
            #proposal.character_check_status = 'not_checked'
            #proposal.compliance_check_status = 'not_checked'
            #Sproposal.review_status = 'not_reviewed'

            proposal.lodgement_number = ''
            proposal.lodgement_sequence = 0
            proposal.lodgement_date = None

            proposal.assigned_officer = None
            proposal.assigned_approver = None

            proposal.approval = None

            original_proposal_id = proposal.id

            proposal.previous_proposal = proposal.objects.get(id=original_proposal_id)

            proposal.id = None

            #proposal.save(no_revision=True)
            proposal.save()


            # clone documents
            for proposal_document in ProposalDocuments.objects.filter(proposal=original_proposal_id):
                proposal_document.proposal = proposal
                proposal_document.id = None
                proposal_document.save()

            return proposal
        except:
            raise

