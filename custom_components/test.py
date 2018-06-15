"""
Set up the demo environment that mimics interaction with devices.

For more details about this component, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import asyncio
import logging

import homeassistant.bootstrap as bootstrap

_LOGGER = logging.getLogger(__name__)

DOMAIN = "test"


@asyncio.coroutine
def async_setup(hass, config):
    """Set up the demo environment."""
    configurator = hass.components.configurator
    group = hass.components.group

    # Set up input select
    tasks = []
    tasks.append(bootstrap.async_setup_component(
        hass, 'input_select',
        {'input_select':
         {'smart_button1': {'icon': 'mdi:panda',
                        'initial': 'Single Press',
                        'name': 'Press Button0',
                        'options': ['Single Press', 'Long Press']}}}))
    
    tasks.append(bootstrap.async_setup_component(
        hass, 'input_number',
        {
            'input_number':
            {
                'slider1': {'initial': 30,
                        'name': 'Press Button2',
                        'min': 10,
                        'max': 50,
                        'step': 1},
                'box1': {'initial': 30,
                        'name': 'Press Button3',
                        'min': 10,
                        'max': 50,
                        'step': 1,
                        'mode': 'box'}
            }
        }))
    tasks.append(bootstrap.async_setup_component(
        hass, 'input_boolean',
        {
            'input_boolean':
            {
                'input_boolean': {'initial': True,
                        'name': 'input_boolean'}
            }
        }))
    tasks1 = []
    tasks1.append(bootstrap.async_setup_component(
        hass, 'input_select',
        {'input_select':
         {'smart_button2': {'icon': 'mdi:panda',
                        'initial': 'Single Press',
                        'name': 'Press Button1',
                        'options': ['Single Press', 'Long Press']}}}))
    
    results = yield from asyncio.gather(*tasks, loop=hass.loop)

    if any(not result for result in results):
        return False
    
    results = yield from asyncio.gather(*tasks1, loop=hass.loop)

    if any(not result for result in results):
        return False

    tasks2 = []
    tasks2.append(group.Group.async_create_group(hass, 'Smart Button 1', [
        'input_select.smart_button1', 'input_number.slider1']))
    tasks2.append(group.Group.async_create_group(hass, 'Smart Button 2', [
        'input_select.smart_button2', 'input_number.box1', 'input_boolean.input_boolean']))

    results = yield from asyncio.gather(*tasks2, loop=hass.loop)

    if any(not result for result in results):
        return False

    # Set up configurator
    def hue_configuration_callback(data):
        """Fake callback, mark config as done."""
        _LOGGER.critical('Off-LED color: ' + data['Off-LED color'])
        _LOGGER.critical('Off-LED bridness: ' + data['Off-LED bridness'])
        _LOGGER.critical('On-LED color: ' + data['On-LED color'])
        _LOGGER.critical('On-LED bridness: ' + data['Off-LED bridness'])

    def setup_configurator():
        """Set up a configurator."""
        configurator.request_config(
            "SmartButton1 Config", hue_configuration_callback,
            description=("<h1>Test</h1> Press the button on the bridge to register Philips "
                         "Hue with Home Assistant. <b>hallo</b><br>vello\ngenau"),
            fields=[
                {'id': 'SmartButton1', 'name': 'Change Friendly Name'},
                {'id': 'Off-LED color', 'name': 'Color when Swich is OFF'},
                {'id': 'Off-LED bridness', 'name': 'Bridness when Swich is OFF'},
                {'id': 'On-LED color', 'name': 'Color when Swich is On'},
                {'id': 'On-LED bridness', 'name': 'Bridness when Swich is On'}
            ],
            submit_caption="I have pressed the button"
        )

    hass.async_add_job(setup_configurator)

    def setup_configurator1():
        """Set up a configurator."""
        configurator.request_config(
            "SmartButton2 Config", hue_configuration_callback,
            description=("<h1>Test</h1> Press the button on the bridge to register Philips "
                         "Hue with Home Assistant. <b>hallo</b><br>vello\ngenau"),
            description_image="/static/images/config_philips_hue.jpg",
            fields=[
                {'id': 'SmartButton2', 'name': 'Change Friendly Name'},
                {'id': 'Off-LED color', 'name': 'Color when Swich is OFF'},
                {'id': 'Off-LED bridness', 'name': 'Bridness when Swich is OFF'},
                {'id': 'On-LED color', 'name': 'Color when Swich is On'},
                {'id': 'On-LED bridness', 'name': 'Bridness when Swich is On'}
            ],
            submit_caption="I have pressed the button"
        )
    hass.async_add_job(setup_configurator1)

    return True