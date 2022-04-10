# ha-jemenaspreadsheet

This is a [Home Assistant](https://home-assistant.io) sensor component to retrieve information from the [Jemena Electricity Outlook](https://electricityoutlook.jemena.com.au/) website, they are an electricity distributor within Victoria, Australia.

This component will retrieve your electricity usage details from their website, and only cover a limited area around the northern and north western suburbs of Melbourne, Victoria.

To use this component you will need to register for an account via the Electricity Outlook website.

If Jemena are not your electricity distributor then this will be of no use to you.

The component will download a spreadsheet of your power usage from the Jemena. This spreadsheet contains your half hourly kw/h usage for up to the last two years. By setting the sensor names in the "monitored_variables" list in the configuration.yaml you can perform calculatiuons on the data collected. 

The component is based on an [ha-jemenaoutlook](https://github.com/mvandersteen/ha-jemenaoutlook) energy sensor. Both this sensor, and the JemenaOutlook sensor can be run at the same time. The JemenaOutlook sensor pulls data from the GUI and can includes information about expendature. Please review the JemenaOutlook sensor to see if it provides the data you are looking for. Thank you to the writer of the JemenaOutlook component, it helpd a lot.

This component is not endorsed by Jemena, nor have a I asked for their endorsement.

## Installing the component

Copy the included files (except README.md) to it's own directory called jemenaoutlook within custom_components directory where the configuration for your installation of home assistant sits. 

The custom_components directory does not exist in default installation state and may need to be created.

```
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/sensor.py
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/__init__.py
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/manifest.py
```
For me this is :-
```
/home/ha/.homeassistant/custom_components/jemenaoutlook/sensor.py
/home/ha/.homeassistant/custom_components/jemenaoutlook/__init__.py
/home/ha/.homeassistant/custom_components/jemenaoutlook/manifest.py
```

Or just use git to clone into a jemenaoutlook directory, when using this method make sure teh user home-assistant is running as can read these files.
```
git clone https://github.com/camo6016/ha-jemenaspreadsheet.git jemenaspreadsheet
```

## Details about monitoring variables

```
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
```

## Configuring the sensor

```
# Example configuration.yaml entry

sensor:
  - platform: jemenaspreadsheet
    username: MYUSERNAME
    password: MYPASSWORD
    monitored_variables:
      - power_last_2Y_max    # Get last 2   years  from dataframe and get max
      - power_last_2Y_min    # Get last 2   years  from dataframe and get min
      - power_last_2Y_mean   # Get last 2   years  from dataframe and get mean
      - power_first_10D_mean # Get first 10 days   from dataframe and average them
      - power_last_10D_mean  # Get last 10  days   from dataframe and average them
      - power_head_5_mean    # Get first 5  values from dataframe and average them
      - power_tail_5_mean    # Get last 5   values from dataframe and average them


```

**Configuration variables:**

- **username** (Required): Username used to log into the Jemena Electricity Outlook website.
- **password** (Required): Password used to log into the Jemena Electricity Outlook website
- **monitored_variables** array (Required): Variables to monitor.
    - **supply_charge** (AUD): **\*\*\*** Daily supply charge to properly
    - **weekday_peak_cost** (AUD): **\*\*\*** Cost per kilowatt hour for peak usage
    - **weekday_offpeak_cost** (AUD): **\*\*\*** Cost per kilowatt hour for offpeak usage
    - **weekday_shoulder_cost** (AUD): **\*\*\*** Cost per kilowatt hour for shoulder usage
    - **controlled_load_cost** (AUD): **\*\*\*** Cost per kilowatt hour for controlled load usage
    - **weekend_offpeak_cost** (AUD): **\*\*\*** Cost per kilowatt hour for weekend offpeak usage
    - **single_rate_cost** (AUD): **\*\*\*** Cost per kilowatt hour for single rate usage
    - **generation_cost** (AUD): **\*\*\*** Amount paid per kilowatt hour feed into the grid
    - **yesterday_user_type** (text): Type of grid user [consumer | generator]
    - **yesterday_usage** (kwh): Net consumption of power usage for yesterday all consumption type - generation
    - **yesterday_consumption** (kwh): Total of consuption for yesterday
    - **yesterday_consumption_peak** (kwh): Total peak consumption for yesterday
    - **yesterday_consumption_offpeak** (kwh): Total offpeak consumption for yesterday
    - **yesterday_consumption_shoulder** (kwh): Total shoulder consumption for yesterday
    - **yesterday_consumption_controlled_load** (kwh): Total controlled load consumption for yesterday
    - **yesterday_generation** (kwh): total of generated electricity feed into the grid for yesterday
    - **yesterday_cost_total** (AUD): **\*\*\*** Total cost of new consumption for yesterday (concumption - generation) (does not include daily supply)
    - **yesterday_cost_consumption** (AUD): **\*\*\*** Total cost of consumption for yesterday (does not include daily supply)
    - **yesterday_cost_generation** (AUD): **\*\*\*** Total cost of generated electricity feed into the grid.
    - **yesterday_cost_difference** (AUD): **\*\*\*** Difference in cost from previous day
    - **yesterday_percentage_difference** (%): percentage increase in net consumption compared to previous day
    - **yesterday_difference_message** (text): Message displayed in Electicity Outlook to describe differnce from previous day
    - **yesterday_consumption_difference** (KWH): difference in kilowatt hours of net consumption to previous day
    - **yesterday_consumption_change** (text): One of increase or decrease
    - **yesterday_suburb_average** (kwh): Average net consumption for entire suburb
    - **previous_day_usage** (kwh): Net consumption for previous day previous to Yesterday (2 days ago)
    - **previous_day_consumption** (kwh): Consumption for previous day previous to Yesterday (2 days ago)
    - **previous_day_generation** (kwh): Generation for previous day previous to Yesterday (2 days ago) feed into grid
    - this_week_user_type
    - this_week_usage
    - this_week_consumption
    - this_week_consumption_peak
    - this_week_consumption_offpeak
    - this_week_consumption_shoulder
    - this_week_consumption_controlled_load
    - this_week_generation
    - this_week_cost_total
    - this_week_cost_consumption
    - this_week_cost_generation
    - this_week_cost_difference
    - this_week_percentage_difference
    - this_week_difference_message
    - this_week_consumption_difference
    - this_week_consumption_change
    - this_week_suburb_average
    - last_week_usage
    - last_week_consumption
    - last_week_generation
    - this_month_user_type
    - this_month_usage
    - this_month_consumption
    - this_month_consumption_peak
    - this_month_consumption_offpeak
    - this_month_consumption_shoulder
    - this_month_consumption_controlled_load
    - this_month_generation
    - this_month_cost_total
    - this_month_cost_consumption
    - this_month_cost_generation
    - this_month_cost_difference
    - this_month_percentage_difference
    - this_month_difference_message
    - this_month_consumption_difference
    - this_month_consumption_change
    - this_month_suburb_average
    - last_month_usage
    - last_month_consumption
    - last_month_generation


\*** For the cost based variables to be reported correctly you must setup your account with your current tarrif from your electricity retailer. These values can be obtained from your latest electricity bill. 

