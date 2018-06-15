import logging
import asyncio

from homeassistant.components.switch import SwitchDevice
from homeassistant.const import (STATE_OFF, STATE_ON)
from homeassistant.core import callback
from homeassistant.helpers import event

import custom_components.zeptrionairhub as zeptrionairhub

DATA_ZEPTRIONAIRHUB = 'ZeptrionAirHub'
DOMAIN = 'zeptrionairhub'

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    hub = hass.data[zeptrionairhub.DATA_ZEPTRIONAIRHUB]
    if discovery_info == None:
        return False
    entities = []
    for temp_panel in hub._panels:
        if temp_panel.name == discovery_info:
            try:
                for index, button in enumerate(temp_panel.all_buttons, start=0):
                    if button is not None:
                        temp_Handler = ButtonHandler(index, button, hass, 'switch')

                        entities.append(temp_Handler)
            except Exception as ex:
                _LOGGER.critical(ex)
    async_add_devices(entities)

class ButtonHandler(SwitchDevice):
    def __init__(self, button_number, button, hass, hass_type):
        self.hass_type = hass_type
        self.button_number = button_number
        self.button = button
        self.hass = hass
        self.press_info = None
        self.temp_panel_name = self.button._panel.name.replace('.', '_').replace('-', '_')
        button.listen_to(self.async_register_callbacks)
        self.register_friendly_name_change()

    @callback
    def async_register_callbacks(self, press_info):
        """Handle if the button is pressed."""
        self.press_info = press_info
        self.async_schedule_update_ha_state(force_refresh=True)
    
    @property
    def unique_id(self):
        return self.temp_panel_name + self.button.id

    @property
    def name(self):
        """Return the name of the switch."""
        return self.button.name
    
    @property
    def available(self):
        """Return true if entity is available."""
        return True
    
    @property
    def should_poll(self):
        """No polling needed for a demo switch."""
        return False
    
    @property
    def bh_entity_id(self):
        """Return the whole entity id."""
        return self.hass_type + '.' + self.unique_id
    
    @property
    def is_on(self):
        """Return true if device is on."""
        if self.press_info == None:
            if self.button._update():
                return True
        else:
            try:
                if int(self.press_info.value) == 0:
                    return False
                elif int(self.press_info.value) == 100:
                    return True
                else:
                    return False
                    # return self.press_info.value
            except TypeError:
                return False

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        # await self.device.set_on()
        pass

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        # await self.device.set_off()
        pass
    
    def register_friendly_name_change(self):
        def change_friendly_name(entity_id, state_old, state_new):
            if state_old and state_new :
                if 'friendly_name' in state_old.attributes and 'friendly_name' in state_new.attributes :
                    if state_old.attributes["friendly_name"] != state_new.attributes["friendly_name"]:
                        self.button.change_info_configuration(state_new.attributes["friendly_name"], self.button.group)

        event.async_track_state_change(self.hass, self.bh_entity_id, change_friendly_name)


    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        button_struct = {
            "name":self.unique_id,
            "group":self.button.group,
            "cat":self.button.cat,
            "id":self.button.id,
            "friendly_name":self.name,
            "org_friendly_name":self.name,
            "panel_url":self.button.panel_url,
            "is_smart":self.button.is_smart,
            "button_number":self.button_number
        }

        ''' Workaround because of bug in self.button.type '''
        temp_cat = int(self.button.cat)
        if temp_cat == -1:
            button_struct['button_type'] =  'unused'
        elif temp_cat == 1:
            button_struct['button_type'] =  'light on/of'
        elif temp_cat == 3:
            button_struct['button_type'] =  'light dimmable'
        elif temp_cat == 5:
            button_struct['button_type'] =  'blind'
        elif temp_cat == 6:
            button_struct['button_type'] =  'Markise'
        elif temp_cat == 17:
            button_struct['button_type'] =  'Smart Btn'
        else:
            button_struct['button_type'] =  'unknown'

        if self.press_info != None:
            button_struct['last_press_update'] = self.press_info.status_update_time
            button_struct['last_press_type'] = self.press_info.type
            button_struct['last_press_value'] = self.press_info.value

        return button_struct