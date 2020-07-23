# Sensor for scrape Mindergas
import logging
import datetime
import json
import voluptuous as vol

from homeassistant.util import dt
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_NAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Information provided by Mindergas'

DEFAULT_NAME = 'mindergas'

SCAN_INTERVAL = datetime.timedelta(seconds=3600)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_USERNAME): cv.string,
	vol.Required(CONF_PASSWORD): cv.string,
	vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL):
            cv.time_period,
	vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
	username = config.get(CONF_USERNAME)
	password = config.get(CONF_PASSWORD)
	name = config.get(CONF_NAME)
	add_entities([GasPrognose(username, password, name)], True)
	add_entities([GasUsed(username, password, name)], True)
	add_entities([GraadDag(username, password, name)], True)

class GasPrognose(RestoreEntity):
	def __init__(self, username, password, name):
		# initialiseren sensor
		self._username = username
		self._password = password
		self._name = name + '_prognose'
		self._state = 0
		self._attributes = {'last_update': None}
		self.update()
		
	@property
	def name(self):
		return self._name

	@property
	def unit_of_measurement(self):
	# Return the unit of measurement of this entity, if any.
		return 'm3'

	@property
	def state(self):
		return self._state

	@property
	def device_state_attributes(self):
	# Return the state attributes.
		return self._attributes

	@property
	def icon(self):
	# Icon to use in the frontend.
		return 'mdi:chart-line'

	def update(self):
		import requests
		from lxml import html
		from bs4 import BeautifulSoup
		LOGIN_URL = "https://www.mindergas.nl/users/sign_in/"
		URL_DATA = "https://www.mindergas.nl/member/year_overview/new"
		URL_DASHBOARD = "https://www.mindergas.nl/member/dashboard"
		URL_RESULT = 'none'
		n = 0
		while not URL_RESULT == URL_DASHBOARD :
			if n == 10:
				_LOGGER.error('Update of ' + str(self._name) + 'failed after ' + n + 'attempts')
				break
			session_requests = requests.session()

			# Get login csrf token
			result = session_requests.get(LOGIN_URL)
			tree = html.fromstring(result.text)
			authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]

			# Create payload
			payload = {
				"user[email]": self._username,
				"user[password]": self._password,
				"authenticity_token": authenticity_token}

			# Perform login
			result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
			URL_RESULT = result.url
			n += 1

			if URL_RESULT == URL_DASHBOARD:
				# Scrape url
				raw_html = session_requests.get(URL_DATA, headers=dict(referer=URL_DATA)).text
				data = BeautifulSoup(raw_html, 'html.parser')

				# Scrape prognose
				div = data.find_all("div", class_="table_cell")[9]
				result = round(eval(div.get_text().replace('m3','').replace(',' , '.').rstrip()))
				self._attributes['last_update'] = dt.now().isoformat('T')
				self._state = result
			else: 
				pass

	async def async_added_to_hass(self) -> None:
		"""Handle entity which will be added."""
		await super().async_added_to_hass()
		state = await self.async_get_last_state()
		if not state:
			return
		self._state = state.state

class GasUsed(RestoreEntity):
	def __init__(self, username, password, name):
		# initialiseren sensor
		self._username = username
		self._password = password
		self._name = name + '_used'
		self._state = None
		self._attributes = {'last_update': None}
		self.update()
		
	@property
	def name(self):
		return self._name

	@property
	def unit_of_measurement(self):
	# Return the unit of measurement of this entity, if any.
		return 'm3'

	@property
	def state(self):
		return self._state

	@property
	def device_state_attributes(self):
	# Return the state attributes.
		return self._attributes

	@property
	def icon(self):
	# Icon to use in the frontend.
		return 'mdi:chart-line'

	def update(self):
		import requests
		from lxml import html
		from bs4 import BeautifulSoup
		LOGIN_URL = "https://www.mindergas.nl/users/sign_in/"
		URL_DATA = "https://www.mindergas.nl/member/year_overview/new"
		URL_DASHBOARD = "https://www.mindergas.nl/member/dashboard"
		URL_RESULT = 'none'
		n = 0
		while not URL_RESULT == URL_DASHBOARD :
			if n == 10:
				_LOGGER.error('Update of ' + str(self._name) + 'failed after ' + n + 'attempts')
				break
			session_requests = requests.session()

			# Get login csrf token
			result = session_requests.get(LOGIN_URL)
			tree = html.fromstring(result.text)
			authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]

			# Create payload
			payload = {
				"user[email]": self._username,
				"user[password]": self._password,
				"authenticity_token": authenticity_token}

			# Perform login
			result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
			URL_RESULT = result.url
			n += 1

			if URL_RESULT == URL_DASHBOARD:		
				# Scrape url
				raw_html = session_requests.get(URL_DATA, headers=dict(referer=URL_DATA)).text
				data = BeautifulSoup(raw_html, 'html.parser')
				
				# Scrape gas used
				div = data.find_all("div", class_="table_cell")[1]
				result = round(eval(div.get_text().replace('m3','').replace(',' , '.').rstrip()))
				self._attributes['last_update'] = dt.now().isoformat('T')
				self._state = result
			else: 
				pass

	async def async_added_to_hass(self) -> None:
		"""Handle entity which will be added."""
		await super().async_added_to_hass()
		state = await self.async_get_last_state()
		if not state:
			return
		self._state = state.state
		
class GraadDag(RestoreEntity):
	def __init__(self, username, password, name):
		# initialiseren sensor
		self._username = username
		self._password = password
		self._name = name + '_graaddag'
		self._state = None
		self._attributes = {'last_update': None}
		self.update()
		
	@property
	def name(self):
		return self._name

	@property
	def unit_of_measurement(self):
	# Return the unit of measurement of this entity, if any.
		return 'm3'

	@property
	def state(self):
		return self._state

	@property
	def device_state_attributes(self):
	# Return the state attributes.
		return self._attributes

	@property
	def icon(self):
	# Icon to use in the frontend.
		return 'mdi:chart-line'

	def update(self):
		import requests
		from lxml import html
		from bs4 import BeautifulSoup
		LOGIN_URL = "https://www.mindergas.nl/users/sign_in/"
		URL_DATA = "https://www.mindergas.nl/member/year_overview/new"
		URL_DASHBOARD = "https://www.mindergas.nl/member/dashboard"
		URL_RESULT = 'none'
		n = 0
		while not URL_RESULT == URL_DASHBOARD :
			if n == 10:
				_LOGGER.error('Update of ' + str(self._name) + 'failed after ' + n + 'attempts')
				break
			session_requests = requests.session()

			# Get login csrf token
			result = session_requests.get(LOGIN_URL)
			tree = html.fromstring(result.text)
			authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]

			# Create payload
			payload = {
				"user[email]": self._username,
				"user[password]": self._password,
				"authenticity_token": authenticity_token}

			# Perform login
			result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
			URL_RESULT = result.url
			n += 1

			if URL_RESULT == URL_DASHBOARD:			
				# Scrape url
				raw_html = session_requests.get(URL_DATA, headers=dict(referer=URL_DATA)).text
				data = BeautifulSoup(raw_html, 'html.parser')

				# Scrape graaddag
				div = data.find_all("div", class_="table_cell")[5]
				result = eval(div.get_text().replace('m3/graaddag', '').replace(',', '.').rstrip())
				self._attributes['last_update'] = dt.now().isoformat('T')
				self._state = result
			else: 
				pass
			
	async def async_added_to_hass(self) -> None:
		"""Handle entity which will be added."""
		await super().async_added_to_hass()
		state = await self.async_get_last_state()
		if not state:
			return
		self._state = state.state