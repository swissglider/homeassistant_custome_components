import logging
import asyncio

from homeassistant.components.switch import SwitchDevice
from homeassistant.components.light import ATTR_BRIGHTNESS, Light
import homeassistant.helpers.entity as entity_helper
from homeassistant.components.switch import ENTITY_ID_FORMAT as SWITCH_ENTITY_ID_FORMAT
from homeassistant.components.group import ENTITY_ID_FORMAT as GROUP_ID_FORMAT
from homeassistant.const import (STATE_OFF, STATE_ON)
from homeassistant.core import callback

import custom_components.zeptrionairhub as zeptrionairhub

DATA_ZEPTRIONAIRHUB = 'ZeptrionAirHub'
DOMAIN = 'zeptrionairhub'

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    hub = hass.data[zeptrionairhub.DATA_ZEPTRIONAIRHUB]
    if discovery_info == None:
        return False
    entities = []
    for temp_panel in hub._panels:
        if temp_panel.name == discovery_info:
            try:
                for index, button in enumerate(temp_panel.all_buttons, start=0):
                    if button is not None:

                        # --------------------------------
                        # Set Status
                        # --------------------------------
                        # button_struct = {
                        #     "name":button.name,
                        #     "group":button.group,
                        #     "cat":button.cat,
                        #     "id":button.id,
                        #     "friendly_name":button.name
                        # }
                        # temp_panel_name = panel.name.replace('.', '_').replace('-', '_')
                        # hass.states.async_set(DOMAIN + "." + temp_panel_name + button.id, button._update(),button_struct)
                        temp_Handler = ButtonHandler(temp_panel, button, hass)

                        entities.append(temp_Handler)

                        # --------------------------------
                        # Notification Message
                        # --------------------------------
                        # button_message  = ""
                        # button_message += "\nPanel Name: " + str(panel.name)
                        # button_message += "\nURL: " + str(panel.url)
                        # button_message += "\nName: " + str(button.name)
                        # button_message += "\nGroup: " + str(button.group)
                        # button_message += "\nCat: " + str(button.cat)
                        # button_message += "\nID: " + str(button.id)

                        # hass.async_run_job(hass.services.async_call('persistent_notification', 'create',
                        #     {
                        #         "message":button_message,
                        #         "title":"New Zeptrion Button found"
                        #     }
                        # ))
            except Exception as ex:
                _LOGGER.critical(ex)
    # async_add_devices(entities)

class ButtonHandler(SwitchDevice):
    def __init__(self, panel, button, hass):
        self.panel = panel
        self.button = button
        self.hass = hass
        self.press_info = None
        self.temp_panel_name = self.panel.name.replace('.', '_').replace('-', '_')
        button.listen_to(self.async_register_callbacks)
        self._setAttributs()

    @callback
    def async_register_callbacks(self, press_info):
        self.press_info = press_info
        """Handle if the button is pressed."""
        try:
            # --------------------------------
            # Set Status
            # --------------------------------
            button_struct = {
                "name":self.button.name,
                "group":self.button.group,
                "cat":self.button.cat,
                "id":self.button.id,
                "friendly_name":self.button.name,
                "last_update":press_info.status_update_time,
                "last_press_type":press_info.type
            }
            temp_value = False
            if press_info.value is not None:
                button_struct['last_value'] = press_info.value
                if press_info.value == 0 or press_info.value == '0':
                    temp_value = "off"
                else:
                    temp_value = "on"
            else:
                temp_value = press_info.type
            self.hass.states.async_set("switch" + "." + self.temp_panel_name + self.button.id, temp_value, button_struct)
            # self.hass.states.async_set("light" + "." + self.temp_panel_name + self.button.id, temp_value, button_struct)

            # # --------------------------------
            # # Notification Message
            # # --------------------------------
            # button_message  = "Name: " + str(self.button.name)
            # if press_info.value is not None:
            #     button_message += "\nValue: \t" + str(press_info.value)

            # self.hass.async_run_job(self.hass.services.async_call('persistent_notification', 'create',
            #     {
            #         "message":button_message,
            #         "title":"Status Change"
            #     }
            # ))
        except Exception as ex:
            _LOGGER.critical(ex)
    
    @property
    def unique_id(self):
        return self.temp_panel_name + self.button.id

    @property
    def name(self):
        """Return the name of the switch."""
        return self.temp_panel_name + self.button.id
    
    @property
    def available(self):
        """Return true if entity is available."""
        return True
    
    @property
    def should_poll(self):
        """No polling needed for a demo switch."""
        return False
    
    @property
    def is_on(self):
        """Return true if device is on."""
        if self.press_info == None:
            if self.button._update():
                return "on"
            return "off"
        else:
            if self.press_info.value == 0 or self.press_info.value == '0':
                return "off"
            else:
                return "on"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        # await self.device.set_on()
        pass

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        # await self.device.set_off()
        pass
    
    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        # get Group Name
        # attributes = {}
        # attributes['group'] = self._group
        # attributes['friendly_name'] = self._name
        # return attributes
        pass
    
    def _setAttributs(self):
        button_struct = {
            "name":self.button.name,
            "group":self.button.group,
            "cat":self.button.cat,
            "id":self.button.id,
            "friendly_name":self.button.name
        }
        status = "off"
        if self.button._update():
            status = "on"
        # self.hass.states.async_set("light" + "." + self.temp_panel_name + self.button.id, status, button_struct)
        self.hass.states.async_set("switch" + "." + self.temp_panel_name + self.button.id, status, button_struct)