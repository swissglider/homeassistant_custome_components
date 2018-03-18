"""
Swiss glider Panel.

Version V.0.0.1

Package:
    custom_components.sg_panel.py
    custom_components.switch.sg_panel.py

configuration.yaml:
    # musst: name / opt: group, donain_filter, attr_filter, group_filter
    sg_panel:
    - name: Hello World
        domain_filter:
            hello_world
    - name: Zeptrion Lights Stube
        domain_filter:
            light
        attr_filter:
            is_zeptrion_group
        group_filter:
            Stube

ToDo:
- Splitt into two Components
- Change to hide insteed of remove group
- Change the add Main Panel to be added

For more details about this Class, please refer to the documentation at
https://github.com/swissglider/homeassistant_custome_components
"""

import logging

import homeassistant.helpers.entity as entity_helper
from homeassistant.helpers.event import track_state_change
from homeassistant.components.group import ENTITY_ID_FORMAT as GROUP_ID_FORMAT
from homeassistant.helpers.discovery import load_platform

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

# The domain of your component. Equal to the filename of your component.
DOMAIN = "sg_panel"
#PANEL_SWITCH = "overview_panel.switch"


def setup(hass, config):
    
    conf = config.get(DOMAIN, {})
    switche_names_attr = {}

    for panel in conf:
        if 'name' not in panel:
            _LOGGER.critical('Error in config: following Parameter nor set - name')
            return False
        name = panel['name']

        group = None
        if 'group' in panel:
            group = panel['group']

        domain_filter = []
        if 'domain_filter' in panel:
            filters = panel['domain_filter'].split( )
            for filter in filters:
                domain_filter.append(filter)

        attr_filter = []
        if 'attr_filter' in panel:
            filters = panel['attr_filter'].split( )
            for filter in filters:
                attr_filter.append(filter)

        group_filters = []
        if 'group_filter' in panel: 
            filters = panel['group_filter'].split( )
            for filter in filters:
                group_filters.append(filter)

        overview_panel = OverviewPanel(name, DOMAIN, domain_filter, attr_filter, group_filters, hass)
        #track_state_change(hass, overview_panel._switch_name, overview_panel.handel_switch_change_event_show, 'False', 'True')
        #track_state_change(hass, overview_panel._switch_name, overview_panel.handel_switch_change_event_hide, 'True', 'False')
        #hass.services.register(DOMAIN, entity_id + '_show', overview_panel.show)
        #hass.services.register(DOMAIN, entity_id + '_hide', overview_panel.hide)

        entity_id = entity_helper.generate_entity_id('{}',name, hass=hass)
        switche_names_attr[entity_id] = {}
        switche_names_attr[entity_id]['name'] = name
        switche_names_attr[entity_id]['group'] = group
        switche_names_attr[entity_id]['overview_panel'] = overview_panel
        switche_names_attr[entity_id]['domain'] = DOMAIN

    hass.data['switche_names_attr'] = switche_names_attr
    load_platform(hass, 'switch', DOMAIN)

    # Return boolean to indicate that initialization was successfully.
    return True

class OverviewPanel:
    def __init__(self, name, domain, domain_filter, attr_filters, group_filters, hass):
        self.hass = hass
        self._name = name
        self._domain_filter = domain_filter
        self._attr_filters = attr_filters
        self._group_filters = group_filters
        self._entity_id = entity_helper.generate_entity_id('{}',name, hass=self.hass)
        self._generated = False
        self._domain_name = domain
        self._full_name = self._domain_name + '.' + self._entity_id

    # ========================================================
    # ========================== Service Methodes
    # ========================================================

    def show(self, call = None):
        if self._generated is False:
            #self._generate_panel(self._domain_filter)
            self._generate_panel(self._domain_filter, self._attr_filters, self._group_filters)
        self.hass.services.call("group", "update")
        self._generated = True
        return True
        
    def hide(self, call = None):
        payload = {
            "object_id": self._entity_id,
        }
        self.hass.services.call("group", "remove", payload)
        self.hass.services.call("group", "update")
        self._generated = False
        return True

    # ========================================================
    # ========================== Panel Generator Methodes
    # ========================================================

    def _generate_panel(self, domain_filters = None, attr_filters  = None, group_filters = None):
        entities = []
        if domain_filters:
            for domain_filters in domain_filters:
                entities = entities + self._get_entities(domain_filters, attr_filters, group_filters)
        else:
            entities = self._get_entities(None, attr_filters, group_filters)
        self._rename_all_frienly_names(entities)
        filtered_entities = self._filterBindedDevices(entities)
        self._generate_all_group_channels(filtered_entities)
    
    def _get_all_entities(self, domain_filter = None):
        entities = self.hass.states.entity_ids(domain_filter)
        return entities

    def _generate_all_group_channels(self, entites):
        
        sup_group_entities = {}
        groups = []
        for entity in entites:
            entity_name = entity['entity_name']
            group_name = self._get_group_conform_name(entity['group_name'])
            opject_group_name = self._get_object_name(group_name)
            entity_group_list = None
            if opject_group_name not in sup_group_entities:
                sup_group_entities[opject_group_name] = self._get_group_entity_dict(
                    opject_group_name, entity['group_name'], False, True, []
                )
                groups.append(group_name)
            entity_group_list = sup_group_entities[opject_group_name]['add_entities']
            entity_group_list.append(entity_name)
            sup_group_entities[opject_group_name]['add_entities'] = entity_group_list

        for sup_group_entity in sup_group_entities:
            self.hass.services.call("group", "set", sup_group_entities[sup_group_entity])
        
        dictMainGroup = self._get_group_entity_dict(self._entity_id, self._name, True, True, groups)
        self.hass.services.call("group", "set", dictMainGroup)

    # ========================================================
    # ========================== Helper Methods
    # ========================================================

    def _get_group_entity_dict(self, object_id, name, view, visible, add_entities):
        ''' return a group entity dict. '''
        return {
            'object_id': str(object_id),
            'name': str(name),
            'view': view,
            'visible': visible,
            'add_entities': add_entities
        }

    def _get_group_conform_name(self, group_name):
        ''' return a name that is group_name conform. '''
        return entity_helper.generate_entity_id(
            GROUP_ID_FORMAT,
            group_name,
            hass=self.hass)
    
    def _get_object_name(self, entity_name):
        ''' return the object_name from entity_name. '''
        return entity_name.partition('.')[2]
    
    def _get_friendly_name(self, name):
        ''' return a friendly name from name. '''
        if name:
            name = name.replace(".", " ")
            name = name.replace("_", " ")
            name = name.title()
        return name
    
    def _get_panel_entity_dict(self, entity_name, name, friendly_name, group_name):
        ''' return a friendly name from name. '''
        return {
            'entity_name': str(entity_name),
            'name' : str(name),
            'friendly_name' : str(friendly_name),
            'group_name' : str(group_name)
        }

    # ========================================================
    # ========================== Change Registry Name
    # ========================================================

    def _changeFriendlyName(self, enitity_name, friendly_name):
        ''' Change the Registry Name of the entity. '''
        import requests
        import json
        url = 'http://localhost:8123/api/config/entity_registry/' + str(enitity_name)
        payload = {'name': str(friendly_name)}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code is not 200:
            _LOGGER.warning('Frienly Name(' + friendly_name + ') change was not successfull for Entity: ' + str(enitity_name) + " Status-Code: " + str(r.status_code))

    def _rename_all_frienly_names(self, entites):
        ''' Change all entities Registry Names to friendly name. '''
        for entity in entites:
            if 'entity_name' in entity and 'friendly_name' in entity:
                self._changeFriendlyName(entity['entity_name'], entity['friendly_name'])

    # ========================================================
    # ========================== Filter Entities
    # ========================================================
    
    def _get_entities(self, domain_filter = None, attr_filters = None, group_filters = None):
        _entities = [] # --> [{entity_name: '',name: '', friendly_name: '', group_name: ''}]
        all_entities = self._get_all_entities(domain_filter)
        for entity_name in all_entities:
            entity_attributes = self.hass.states.get(entity_name).attributes
            name = self._get_object_name(entity_name)
            friendly_name = ''
            group_name = ''
            if 'friendly_name' in entity_attributes:
                friendly_name = entity_attributes['friendly_name']
                if '_' in friendly_name:
                    friendly_name = friendly_name.partition('_')[2]
            else:
                friendly_name = name.partition('_')[2]
            if 'group' in entity_attributes:
                group_name = entity_attributes['group']
            else:
                group_name = name.partition('_')[0]
            friendly_name = self._get_friendly_name(friendly_name)
            group_name = self._get_friendly_name(group_name)
            
            # Filter attributes if available
            if attr_filters and (len(set(attr_filters) & set(entity_attributes)) is 0):
                continue

            # Filter groups if avaialable
            if group_filters and (group_name not in group_filters):
                continue

            _entities.append(self._get_panel_entity_dict(entity_name, name, friendly_name, group_name))

            # if not attr_filters:
            #     _entities.append(self._get_panel_entity_dict(entity_name, name, friendly_name, group_name))
            # else:
            #     for attr_filter in attr_filters:
            #         if attr_filter in entity_attributes:
            #             _entities.append(self._get_panel_entity_dict(entity_name, name, friendly_name, group_name))
        return _entities
        
    def _filterBindedDevices(self, entities):
        mergedList = []
        bindet_devices = []
        for entity in entities:
            entity_name = entity['entity_name']
            attr = self.hass.states.get(entity_name).attributes
            if 'binded_devices' in attr:
                if attr['binded_devices']:
                    bindet_devices = bindet_devices + attr['binded_devices']
        
        for entity in entities:
            entity_name = entity['entity_name']
            if entity_name not in bindet_devices:
                mergedList.append(entity)

        return mergedList

# =====================================================================================================
