"""
Supports the Zeptrion Air Devices.

Version V.0.0.2

Package:
    custom_components.zeptrionairhub.py
    custom_components.light.zeptrionairhub.py
    custom_components.cover.zeptrionairhub.py

configuration.yaml:
    zeptrionairhub:

ToDo:

For more details about this Class, please refer to the documentation at
https://github.com/swissglider/homeassistant_custome_components
"""

import logging
import asyncio
import yaml

import voluptuous as vol

from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.helpers.discovery import (load_platform, async_load_platform)
from homeassistant.const import (CONF_HOST, CONF_NAME, SERVICE_RELOAD)
import homeassistant.helpers.config_validation as cv
DOMAIN = 'zeptrionairhub'

REQUIREMENTS = ['zeptrionAirApi']
ATTR_DISCOVER_DEVICES = 'devices'

_LOGGER = logging.getLogger(__name__)

# CONF_BROWSE_TIME = 'browsetime'

# Validation of the user's configuration
# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#     vol.Optional(CONF_BROWSE_TIME, default=5): cv.positive_int,
# })

DATA_ZEPTRIONAIRHUB = 'ZeptrionAirHub'

# def setup(hass, config):
#     from zeptrionAirApi import ZeptrionAirHub
#     """Your controller/hub specific code."""
#     hass.data[DATA_ZEPTRIONAIRHUB] = ZeptrionAirHub(5)

#     #--- snip ---
#     load_platform(hass, 'light', DOMAIN)
#     load_platform(hass, 'cover', DOMAIN)
#     #load_platform(hass, 'switch', DOMAIN)
#     return True

async def do_close(hub):
    """Close the System."""
    await hub.close()

@asyncio.coroutine
def async_setup(hass, config):
    from zeptrion_air_api import Hub
    # Setup your platform inside of the event loop

    @asyncio.coroutine
    def reload_service_handler(service):
        _LOGGER.critical("reload_service_handler called")
    
    def found_new_panels(panel):
        """Handle if a new Zeptrion Air Panel is found."""
        # _LOGGER.critical(panel)
        try:
            # for index, button in enumerate(panel.all_buttons, start=0):
            #     if button is not None:

            #         # --------------------------------
            #         # Set Status
            #         # --------------------------------
            #         button_struct = {
            #             "name":button.name,
            #             "group":button.group,
            #             "cat":button.cat,
            #             "id":button.id,
            #             "friendly_name":button.name
            #         }
            #         temp_panel_name = panel.name.replace('.', '_').replace('-', '_')
            #         hass.states.async_set(DOMAIN + "." + temp_panel_name + button.id, button._update(),button_struct)
            #         temp_Handler = ButtonHandler(panel, button, hass)
            #         button.listen_to(temp_Handler.callback)

            #         # --------------------------------
            #         # Notification Message
            #         # --------------------------------
            #         # button_message  = ""
            #         # button_message += "\nPanel Name: " + str(panel.name)
            #         # button_message += "\nURL: " + str(panel.url)
            #         # button_message += "\nName: " + str(button.name)
            #         # button_message += "\nGroup: " + str(button.group)
            #         # button_message += "\nCat: " + str(button.cat)
            #         # button_message += "\nID: " + str(button.id)

            #         # hass.async_run_job(hass.services.async_call('persistent_notification', 'create',
            #         #     {
            #         #         "message":button_message,
            #         #         "title":"New Zeptrion Button found"
            #         #     }
            #         # ))
            hass.async_add_job(
                async_load_platform(hass, 'switch', DOMAIN, panel.name, config)
            )
            # hass.async_add_job(
            #     async_load_platform(hass, 'light', DOMAIN, panel.name, config)
            # )
        except Exception as ex:
            _LOGGER.critical(ex)
    
    hass.services.async_register(DOMAIN, SERVICE_RELOAD, reload_service_handler)
    
    # Hub(hass.loop, found_new_panels)
    hass.data[DATA_ZEPTRIONAIRHUB] = Hub(hass.loop, found_new_panels)
    return True

# class ButtonHandler:
#     def __init__(self, panel, button, hass):
#         self.panel = panel
#         self.button = button
#         self.hass = hass

#     def callback(self, press_info):
#         """Handle if the button is pressed."""
#         pass
#         try:
#             # --------------------------------
#             # Set Status
#             # --------------------------------
#             button_struct = {
#                 "name":self.button.name,
#                 "group":self.button.group,
#                 "cat":self.button.cat,
#                 "id":self.button.id,
#                 "friendly_name":self.button.name,
#                 "last_update":press_info.status_update_time,
#                 "last_press_type":press_info.type
#             }
#             temp_value = False
#             if press_info.value is not None:
#                 button_struct['last_value'] = press_info.value
#                 if press_info.value == 0 or press_info.value == '0':
#                     temp_value = False
#                 else:
#                     temp_value = True
#             else:
#                 temp_value = press_info.type
#             temp_panel_name = self.panel.name.replace('.', '_').replace('-', '_')
#             self.hass.states.async_set(DOMAIN + "." + temp_panel_name + self.button.id, temp_value, button_struct)

#             # # --------------------------------
#             # # Notification Message
#             # # --------------------------------
#             # button_message  = "Name: " + str(self.button.name)
#             # if press_info.value is not None:
#             #     button_message += "\nValue: \t" + str(press_info.value)

#             # self.hass.async_run_job(self.hass.services.async_call('persistent_notification', 'create',
#             #     {
#             #         "message":button_message,
#             #         "title":"Status Change"
#             #     }
#             # ))
#         except Exception as ex:
#             _LOGGER.critical(ex)
    
class ConfigHandler:
    def __init__(self, hass):
        self.hass = hass
        self.config = {}

        self.config_file = self.hass.config.path('zeptrion_air.yaml')
        
    
    def read_config(self, panel, button):
        try:
            with open(self.config_file, 'r') as stream:
                self.config = yaml.load(stream)
        except FileNotFoundError as ex:
            _LOGGER.critical(ex)
        except yaml.YAMLError as ex:
            _LOGGER.critical(ex)

    def write_config(self):
        try:
            with open(self.config_file, 'w') as yaml_file:
                yaml.dump(self.config, yaml_file, default_flow_style=False, canonical=False)
        except FileNotFoundError as ex:
            _LOGGER.critical(ex)
        except yaml.YAMLError as ex:
            _LOGGER.critical(ex)
    
    def _create_button_config(self, button):
        """Create the config-struct from button."""
        return {
            'name' : button.name,
            'group' : button.group
        }

    def _create_panel_config(self, panel):
        """Create the config-struct from panel."""
        temp_conf = {}
        for index, button in enumerate(panel.all_buttons, start=0):
            if button is not None:
                temp_conf[index] = self._create_button_config(button)
        return temp_conf

    def add_panel_config(self, panel):
        if panel.name not in self.config:
            self.config[panel.name] = self._create_panel_config(panel)
            self.write_config()
        return
    
    def change_button_config(self, panel, button):
        self.add_panel_config(panel)
        if not self.do_button_config_differs(panel, button):
            return
        
    def _get_button_number(self, panel, button):
        for index, button_conf in enumerate(self.config[panel.name], start=0):
            if button_conf.name == button.name:
                return index
        return None

    
    def get_button_config(self, panel, button):
        if self._do_button_config_exists(panel, button):
            return None
        for button_conf in self.config[panel.name]:
            if button_conf.name == button.name:
                return button_conf

    def do_button_config_differs(self, panel, button):
        if not self._do_button_config_exists(panel, button):
            return True
        button_conf = self.get_button_config(panel, button)
        return not (button.name == button_conf['name'] and \
            button.group == button_conf['group'])
    
    def _do_button_config_exists(self, panel, button):
        if panel.name not in self.config:
            return False
        is_button_in = False
        for button_conf in self.config[panel.name]:
            if button_conf.name == button.name:
                is_button_in = True
                continue
        if not is_button_in:
            return False
        return True