# Sensor for scrape Mindergas
import logging
import datetime
import json
import re as re
import voluptuous as vol
import requests

from homeassistant.util import dt
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_NAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

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

	try:
		data = GasData(username, password)
		add_entities([GasSensor(data, name + '_used', 1, True)], True)
		add_entities([GasSensor(data, name + '_prognose', 9, True)], True)
		add_entities([GasSensor(data, name + '_graaddag', 5, True)], True)

	except requests.exceptions.HTTPError as error:
		_LOGGER.error(error)
	return False

class GasData(object):
	def __init__(self, username, password):
		self.data = None
		self._username = username
		self._password = password

	def update(self):
		from lxml import html
		from bs4 import BeautifulSoup
		LOGIN_URL = "https://www.mindergas.nl/users/sign_in/"
		URL = "https://www.mindergas.nl/member/year_overview/new"
		_LOGGER.debug('Scraping mindergas.nl')

		try:
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

			# Scrape url
			raw_html = session_requests.get(URL, headers=dict(referer=URL)).text
			data = BeautifulSoup(raw_html, 'html.parser')
			self.data = data

		except requests.exceptions.RequestException as exc:
			_LOGGER.error('Error occurred while scraping data: %r', exc)
			self.data = None
			return False

class GasSensor(Entity):
	def __init__(self, data, name, table_cell, round=False):
		# initialiseren sensor
		self.data = data
		self._name = name
		self.round = round
		self.table_cell = table_cell
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
		self.data.update()
		data = self.data.data
		try:
			# Scrape data
			div = data.find_all("div", class_="table_cell")[self.table_cell]
			value = eval(re.sub(r'[^Z0-9-.]', "", div.get_text().replace(',', '.')))
			if self.round == True:
				result = round(value)
			else:
				result = value
		except ValueError:
			result = None

		self._attributes['last_update'] = dt.now().isoformat('T')
		self._state = result