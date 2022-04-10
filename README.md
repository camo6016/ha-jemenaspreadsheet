# This componant is in development and not currently in a functioning state. Please do not use while this banner exists.
 
 
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
<homeassistant-user-configuration-directory>/jemenaspreadsheet/jemenaoutlook/sensor.py
<homeassistant-user-configuration-directory>/jemenaspreadsheet/jemenaoutlook/__init__.py
<homeassistant-user-configuration-directory>/jemenaspreadsheet/jemenaoutlook/manifest.py
```
On some systems this may be :-
```
/home/ha/.homeassistant/custom_components/jemenaspreadsheet/sensor.py
/home/ha/.homeassistant/custom_components/jemenaspreadsheet/__init__.py
/home/ha/.homeassistant/custom_components/jemenaspreadsheet/manifest.py
```
On my Home Assistant OS deployment, the files that needed to be added where at 
```
/config/custom_components/jemenaspreadsheet/sensor.py
/config/custom_components/jemenaspreadsheet/__init__.py
/config/custom_components/jemenaspreadsheet/manifest.py
```
The config file on my Home Assistant OS deployment was at /config/configuration.yaml . On Home Assistant OS, the way I installed this componant was to install one of the standard SSH plugins which provides access to the operating system.

You can use git to clone the files onto your system.
```
git clone https://github.com/camo6016/ha-jemenaspreadsheet.git jemenaspreadsheet
```

## Details about monitoring variables

The name that you set for the sensor in the configuration will determine the operations that are performed on the retreived data set. The dataset is a pandas time serise. In the below code snippet you can see the operations being exicuated.

1. Any string that is valid in a sensor name but does not contain a underscore
2. Pandas period operation to perform. Valid operations are;
    * first and last, which use [offset alias's](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).
    * head and tail, with use a single number to determinne how many lines should be retrived from the start of end of the dataset.
3. Value which will be passed into the aformentioned period operation.
4. Operation that will be performed on the list of kwh values to make it a single value. Valid options are mean, max, min.

Please see the below a snippet of the code used to perform the calculations.

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


