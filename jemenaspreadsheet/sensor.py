"""
Support for JemenaSpreadsheet.

Get data from 'Jemena Energy Outlook - Your Electricity Use' page/s:
https://electricityoutlook.jemena.com.au/electricityView/index

This integration is based off the ha-jemenaoutlook located at
https://github.com/mvandersteen/ha-jemenaoutlook

The ha-jemenaoutlook seems to be inspired by
https://github.com/NAStools/homeassistant/blob/master/homeassistant/components/sensor/bbox.py

For more details about this platform, please refer to the documentation at

"""

from datetime import timedelta

from bs4 import BeautifulSoup
import requests
import logging
from io import StringIO
import pandas as pd

import http.client as http_client

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_NAME,
    CONF_MONITORED_VARIABLES)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['beautifulsoup4==4.6.0']

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

REQUESTS_TIMEOUT = 15

DEFAULT_NAME = 'JemenaSpreadsheet'

REQUESTS_TIMEOUT = 15
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)
SCAN_INTERVAL = timedelta(minutes=30)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_VARIABLES):cv.ensure_list,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

HOST = 'https://electricityoutlook.jemena.com.au'
HOME_URL = '{}/login/index'.format(HOST)


##
## setup_platform creates JemenaSpreadsheetData object
##                creates JemenaSpreadsheetSensor object per sensor configured
##
## JemenaSpreadsheetSensor creates JemenaOutlookClient
##


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Jemena Outlook sensor."""
    # Create a data fetcher to support all of the configured sensors. Then make
    # the first call to init the data.

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    try:
        jemenaspreadsheet_data = JemenaSpreadsheetData(username, password)
        jemenaspreadsheet_data.get_data()

    except requests.exceptions.HTTPError as error:
        _LOGGER.error("Failt login: %s", error)
        return False

    name = config.get(CONF_NAME)

    sensors = []
    for variable in config[CONF_MONITORED_VARIABLES]:
        sensors.append(JemenaSpreadsheetSensor(jemenaspreadsheet_data, variable, name))

    add_devices(sensors)


##
## Object that pulls the spreadsheet from Jemena and makes it available to the sensor objects which performs a
## calculation on the data.
##

class JemenaSpreadsheetData(object):
    """Get data from JemenaOutlook."""

    def __init__(self, username, password, timeout=REQUESTS_TIMEOUT):
        """Initialize the data object."""
        self.username = username
        self.password = password
        self.data = {}
        self._timeout = timeout
        self._session = None

        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch latest data from Jemena Outlook."""
        try:
            # setup requests session
            self._session = requests.Session()

            # Get login page
            login_url = self._get_login_page()

            # Post login page
            self._post_login_page(login_url)

            # Get latest power from csv downloaded
            self._get_spreadsheet()

        except Exception as exp:
            _LOGGER.error("Error on receive last Jemena Outlook data: %s", exp)
            return

    def get_data(self):
        """Return the collected pandas object."""
        return self.data

    def _get_login_page(self):
        """Go to the login page."""
        try:
            raw_res = self._session.get(HOME_URL, timeout=REQUESTS_TIMEOUT)

        except OSError:
            raise Exception("Can not connect to login page")

        # Get login url
        soup = BeautifulSoup(raw_res.content, 'html.parser')

        form_node = soup.find('form', {'id': 'loginForm'})
        if form_node is None:
            raise Exception("No login form found")

        login_url = form_node.attrs.get('action')
        if login_url is None:
            raise Exception("Cannot find login url")

        return login_url

    def _post_login_page(self, login_url):
        """Login to Jemena Electricity Outlook website."""
        form_data = {"login_email": self.username,
                     "login_password": self.password,
                     "submit": "Sign In"}
        try:
            raw_res = self._session.post('{}/login_security_check'.format(HOST),
                                         data=form_data,
                                         timeout=REQUESTS_TIMEOUT)

        except OSError as e:
            raise Exception("Cannot submit login form {0}".format(e.errno))

        if raw_res.status_code != 200:
            raise Exception("Login error: Bad HTTP status code. {}".format(raw_res.status_code))

        return True

    def _get_spreadsheet(self):
        """Get latest data from spreadsheet"""

        try:
            url = '{}/electricityView/download'.format(HOST)
            raw_res = self._session.get(url, timeout=REQUESTS_TIMEOUT)

        except OSError:
            raise Exception("Can not connect to login page")

        response = raw_res.content.decode('utf-8')

        # last_half_hour_power = response[-48:].split(",,")[0].split(",")[-1]

        text = StringIO(response)
        df = pd.read_csv(text)

        ##
        ## Pandas data minipulation from 3d day by hour array to 2d datetime list inspired by
        ## https://stackoverflow.com/questions/41425326/pandas-combine-row-dates-with-column-times
        ##

        # Set Index to date
        df.DATE = pd.to_datetime(df.DATE)
        df = df.set_index('DATE')

        # Remove, clean up columns and convert to timedelta.
        df = df.drop(['NMI', 'METER SERIAL NUMBER', 'CON/GEN', 'ESTIMATED?'], axis = 1)
        df = df.rename(columns=lambda x: x.split(" - ")[1])
        df.columns = pd.to_timedelta(df.columns + ':00')

        # Reshape the dataframe
        df = df.stack()
        df.index = df.index.get_level_values(0) + df.index.get_level_values(1)
        df = df.reset_index()
        df.columns = ['datetime', 'power']
        df = df.set_index('datetime')

        self.data = df

        return self.data

class JemenaSpreadsheetSensor(Entity):
    """Implementation of a Jemena Outlook sensor."""

    def __init__(self, jemenaspreadsheet_data, sensor_type, name):
        """Initialize the sensor."""
        self.client_name = name
        self.type = sensor_type
        self._name = sensor_type
        self._unit_of_measurement = 'kWh'
        self._icon = 'mdi:flash'
        self.jemenaspreadsheet_data = jemenaspreadsheet_data

        _LOGGER.info('init data: %s', jemenaspreadsheet_data.data)

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.client_name, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""

        df = self.jemenaspreadsheet_data.get_data()

        sensor_name_list = self.type.split("_")

        # Get Time Period
        if sensor_name_list[1] == "first":
            df = df.first(sensor_name_list[2])
        elif sensor_name_list[1] == "last":
            df = df.last(sensor_name_list[2])
        elif sensor_name_list[1] == "head":
            df = df.head(sensor_name_list[2])
        elif sensor_name_list[1] == "tail":
            df = df.tail(sensor_name_list[2])
        else:
            raise Exception("Invalid 2nd or 3rd parameter in name, valid 2nd perams are first, last, head, tail")

        # Perform Calculation
        if sensor_name_list[3] == "mean":
            return df.power.mean()
        elif sensor_name_list[3] == "max":
            return df.power.max()
        elif sensor_name_list[3] == "min":
            return df.power.min()
        else:
            raise Exception("Invalid 4th parameter in name, valid 4nd perams are mean, max, min")


    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Get the latest data from Jemena Outlook and update the state."""
        self.jemenaspreadsheet_data.update()



if __name__ == '__main__':
    jemenaspreadsheet_data   = JemenaSpreadsheetData("cameron.mitchell54@gmail.com", "C3PGfynt2qwWCKyVX5qQVMD6")
    jemenaspreadsheet_sensor_1 = JemenaSpreadsheetSensor(jemenaspreadsheet_data, 'power_last_1Y_max', "JemenaSpreadsheet")
    jemenaspreadsheet_sensor_2 = JemenaSpreadsheetSensor(jemenaspreadsheet_data, 'power_last_1D_mean', "JemenaSpreadsheet")

    print(jemenaspreadsheet_sensor_1.state)
    print(jemenaspreadsheet_sensor_2.state)
