# python -m streamlit run <file.py>
import requests
import streamlit as st
import pandas as pd
import numpy as np

api_key = 'f93d2d326a17b52fc5b377bf349faab4'

st.title("Aviation API Lite") #change to 'flight companion lite'? or something


# st.header("Test Title")


# gets .json file for airlines******
# u = f'http://api.aviationstack.com/v1/airlines?access_key={api_key}'
# f = requests.get(u).json()
# with open('f', 'w') as airli:
#   json.dump(f, airli, ensure_ascii=False, indent=4) # missing UTF encoding, gave error when first created
#      file 'f'***


@st.cache #had to change so it wouldn't error on my end
def requestData(endpoint):
    endpointUrl = f'http://api.aviationstack.com/v1/{endpoint}?access_key={api_key}'

    if endpoint == "airports":
        airports = requests.get(endpointUrl).json()  # this is for api req. directly***
        # airports = open("airports.json", "r")
        return airports

    if endpoint == "flights":
        # flights = open("flights.json", "r")
        flights = requests.get(endpointUrl).json()
        return flights

    if endpoint == "airlines":
        airlines = requests.get(endpointUrl).json()
        # airlines = open("airlines.json", "r")
        return airlines

    if endpoint == "countries":
        countries = requests.get(endpointUrl).json()
        # countries = open("countries.json", "r")
        return countries


def makeDict(airline):
    airline_dict = {}
    airline_dict['aName'] = airline["airline_name"]
    # country_name = ["country_name"]
    airline_dict['aAge'] = (float(airline["fleet_average_age"]))
    airline_dict['aSize'] = (int(airline["fleet_size"]))
    if airline["date_founded"] == None:
        airline_dict['aDate'] = 0
    else:
        airline_dict['aDate'] = (int(airline["date_founded"]))
    return airline_dict


def makeFlightDict(flight):
    flight_dict = {}
    flight_dict['fNum'] = flight["flight"]["number"]
    flight_dict['fStat'] = flight["flight_status"]
    flight_dict['fAName'] = flight["airline"]["name"]

    aSTime = flight["arrival"]["scheduled"]
    flight_dict['fASTime'] = aSTime[11:-9]

    flight_dict["aTZ"] = flight["arrival"]["timezone"]
    flight_dict["aAP"] = flight["arrival"]["airport"]

    dSTime = flight["departure"]["scheduled"]
    flight_dict['fDSTime'] = dSTime[11:-9]

    flight_dict["dTZ"] = flight["departure"]["timezone"]
    flight_dict["dAP"] = flight["departure"]["airport"]

    return flight_dict


def appendSort(sortedList, cnt1=None):
    limit = cnt1
    cnt = 0
    aAges = []
    aNames = []
    aSizes = []
    for airline in sortedList:
        if cnt == limit:
            break
        else:
            aAges.append((float(airline['aAge'])))
            aNames.append(airline['aName'])
            aSizes.append((int(airline['aSize'])))
            cnt = cnt + 1
    return aAges, aNames, aSizes


def appendFlight(list, filter):
    if filter == 'Arrival':
        fAirline = []
        fNum = []
        faPort = []
        faTime = []
        aTZ = []
        fStatus = []
        for flight in list:
            fAirline.append(flight['fAName'])
            fNum.append(flight["fNum"])
            faPort.append(flight['aAP'])
            faTime.append(flight['fASTime'])
            aTZ.append(flight['aTZ'])
            fStatus.append(flight['fStat'])

        return fAirline, fNum, faPort, faTime, aTZ, fStatus

    else:
        fAirline = []
        fNum = []
        daPort = []
        daTime = []
        dTZ = []
        fStatus = []

        for flight in list:
            fAirline.append(flight['fAName'])
            fNum.append(flight["fNum"])
            daPort.append(flight['dAP'])
            daTime.append(flight['fDSTime'])
            dTZ.append(flight['dTZ'])
            fStatus.append(flight['fStat'])

        return fAirline, fNum, daPort, daTime, dTZ, fStatus



@st.cache #changed from '..._data'
def load_data(flightList, filter):
    if filter == 'Arrival':
        fAirline, fNum, faPort, faTime, aTZ, fStatus = appendFlight(flightList, filter)
        return pd.DataFrame(
            {
                "Airline": fAirline,
                "Flight": fNum,
                "Coming From": faPort,
                "Time": faTime,
                "Time Zone": aTZ,
                "Status": fStatus

            })
    else:
        fAirline, fNum, daPort, daTime, dTZ, fStatus = appendFlight(flightList, filter)
        return pd.DataFrame(
            {
                "Airline": fAirline,
                "Flight": fNum,
                "Coming From": daPort,
                "Time": daTime,
                "Time Zone": dTZ,
                "Status": fStatus
            })


category = st.selectbox("What info are you looking for?",
                        options=["", "Airlines", "Airports", "Flights"])

if category == 'Airlines':
    endpoint = 'airlines'
    airline_list = requestData(endpoint)
    data = airline_list

    # type(airline_dict)
    # airline_dict = {}
    airline_dict_array = []
    cnt = 0

    for airline in data["data"]:
        airline_dict = makeDict(airline)
        airline_dict_array.append(airline_dict)
        cnt = cnt + 1
    # st.write(airline_dict_array)
    sortedAge = []
    sortedDate = []
    category2 = st.selectbox("Average Fleet Age or Fleet Size",
                             options=["", "Average Fleet Age", "Fleet Size"])
    if category2 == "Average Fleet Age":
        filter = st.sidebar.radio("How do you want to filter the chart?",
                                  ('Higest Ranked Airlines', 'Lowest Ranked Airlines', 'Custom Range'))
        if filter == "Higest Ranked Airlines":
            st.sidebar.write("")
            inputCnt = st.sidebar.number_input(f'How many airlines do you want to display?  \n(Max: {cnt})')
            if (inputCnt < 0 or inputCnt > cnt):
                st.sidebar.error('Value is out of bounds')
            else:
                sortedAge = sorted(airline_dict_array, key=lambda airline_dict: float(airline_dict['aAge']),
                                   reverse=True)
                aAges, aNames, aSizes = appendSort(sortedAge, inputCnt)
                df = pd.DataFrame(aAges, index=aNames)
                st.bar_chart(df)

        elif filter == "Lowest Ranked Airlines":
            st.sidebar.write("")
            inputCnt = st.sidebar.number_input(f'How many airlines do you want to display?  \n(Max: {cnt})')
            if (inputCnt < 0 or inputCnt > cnt):
                st.sidebar.error('Value is out of bounds')
            else:
                sortedAge = sorted(airline_dict_array, key=lambda airline_dict: float(airline_dict['aAge']))
                aAges, aNames, aSizes = appendSort(sortedAge, inputCnt)
                df = pd.DataFrame(aAges, index=aNames)
                st.bar_chart(df)

        elif filter == 'Custom Range':
            maxAge = max(airline_dict_array, key=lambda x: x['aAge'])
            minAge = min(airline_dict_array, key=lambda x: x['aAge'])
            st.sidebar.text("")
            range = st.sidebar.slider("Choose a range of average Fleet Ages",
                                      minAge['aAge'], maxAge['aAge'], ((maxAge['aAge'] / 4), ((maxAge['aAge'] * 0.75))))
            aAges = []
            aNames = []
            aSizes = []
            cnt = 0
            for airline in airline_dict_array:
                if ((airline['aAge'] >= range[0]) and (airline['aAge'] <= range[1])):
                    aAges.append((float(airline['aAge'])))
                    aNames.append(airline['aName'])
                    aSizes.append((int(airline['aSize'])))
                    cnt = cnt + 1
            df = pd.DataFrame(aAges, index=aNames)
            st.bar_chart(df)
            st.info(f'There are {cnt} airlines showing.')

    elif category2 == "Fleet Size":
        filter = st.sidebar.radio("How do you want to filter the chart?",
                                  ('Higest Ranked Airlines', 'Lowest Ranked Airlines', 'Custom Range'))
        if filter == "Higest Ranked Airlines":
            st.sidebar.write("")
            inputCnt = st.sidebar.number_input(f'How many airlines do you want to display?  \n(Max: {cnt})')
            if (inputCnt < 0 or inputCnt > cnt):
                st.sidebar.error('Value is out of bounds')
            else:
                sortedSize = sorted(airline_dict_array, key=lambda airline_dict: float(airline_dict['aSize']),
                                    reverse=True)
                aAges, aNames, aSizes = appendSort(sortedSize, inputCnt)
                df = pd.DataFrame(aSizes, index=aNames)
                st.bar_chart(df)
        elif filter == "Lowest Ranked Airlines":
            st.sidebar.write("")
            inputCnt = st.sidebar.number_input(f'How many airlines do you want to display?  \n(Max: {cnt})')
            if (inputCnt < 0 or inputCnt > cnt):
                st.sidebar.error('Value is out of bounds')
            else:
                sortedSize = sorted(airline_dict_array, key=lambda airline_dict: float(airline_dict['aSize']))
                aAges, aNames, aSizes = appendSort(sortedSize, inputCnt)
                df = pd.DataFrame(aSizes, index=aNames)
                st.bar_chart(df)
        elif filter == 'Custom Range':

            maxSize = max(airline_dict_array, key=lambda x: x['aSize'])
            minSize = min(airline_dict_array, key=lambda x: x['aSize'])
            st.sidebar.text("")
            range = st.sidebar.slider("Choose a range of Fleet Sizes",
                                      minSize['aSize'], maxSize['aSize'],
                                      (int((maxSize['aSize'] / 4)), (int(maxSize['aSize'] * 0.75))))
            aAges = []
            aNames = []
            aSizes = []
            cnt = 0
            for airline in airline_dict_array:
                if ((airline['aSize'] >= range[0]) and (airline['aSize'] <= range[1])):
                    aAges.append((float(airline['aAge'])))
                    aNames.append(airline['aName'])
                    aSizes.append((int(airline['aSize'])))
                    cnt = cnt + 1
            df = pd.DataFrame(aSizes, index=aNames)
            st.bar_chart(df)
            st.info(f'There are {cnt} airlines showing.')

if category == 'Airports':
    endpoint = 'airports'
    airport_list = requestData(endpoint)
    data = airport_list

    ctryJS = requestData('countries')  # to get info fr/ countries.json
    country_list = []
    none = []

    for airport in data["data"]:
        t = airport["country_name"]
        if t not in country_list:
            if (t == None):
                none.append(t)
            else:
                country_list.append(t)


    country_list.insert(0, " ")
    country_list.sort() #sort countries alphabet.

    country_list.insert(1, None)

    country_selected = st.selectbox("Select country to show airports:", options=country_list)
    airport_names = []
    airports = []
    country = ""
    cnt = 0

    currList = []
    # get info fr/ country.json, i.e. currency*
    for cn in ctryJS["data"]:
        if (cn["currency_name"] not in currList):
            currList.append(cn["currency_name"])

    for airport in data["data"]:
        if (country_selected == airport["country_name"]):

            if (airport["airport_name"] == "Municipal"):
                cnt += 1
                if (cnt > 1):
                    cnt = cnt
                else:
                    airports.append(airport["airport_name"])
            else:
                airports.append(airport["airport_name"])

    # sort list alphabetically
    airports.sort()
    airports.insert(0, "")

    if airports:
        if (country_selected == None):
            st.success('Showing airports with no country associated: ')
    else:
        st.warning('No airports found.')

    # st.text('').subheader(f'    Results:   ')
    ap = []
    cnt = 0

    # changing to selectbox instead of many buttons
    # for a in airports:
    a = st.selectbox("Airports: ", options=airports)

    haha = 0  # counter
    cntry_no_curr = " "
    latitude = " "
    longitude = " "
    lat = []
    lon = []

    with st.container():
        for p in data["data"]:  # implements map*
            if a == p["airport_name"]:
                latitude = p["latitude"]
                longitude = p["longitude"]
                lat.append(float(latitude))
                lon.append(float(longitude))
                df = pd.DataFrame({"latitude": lat, "longitude": lon})
                st.map(df)

                st.caption("Location of Selected Airport")
        st.write(f'---------------------------------------')

    with st.container():

        iso = False
        prefix = False
        cont = False
        lat_long = False
        lat = False
        extra = False

        isoBool = False
        prefBool = False
        contBool = False

        col1, col2 = st.columns(2)
        with col1:

            options = st.multiselect('Extra airport information:', options=['Continent', 'Country ISO',
                                                                            'Latitude & Longitude', 'Phone Prefix'])

            for ex in options:
                if ex == 'Country ISO':
                    iso = True
                if ex == 'Phone Prefix':
                    prefix = True

                if ex == 'Continent':
                    cont = True

                if ex == 'Latitude & Longitude':
                    lat_long = True

        with col2:
            for info in data["data"]:

                if (a == info["airport_name"]):

                    if (lat_long == True):
                        st.write(f'Airport Lattitude: {info["latitude"]}')
                        st.write(f'Airport Longitude: {info["longitude"]}')
                        lat = True

                    st.write(f'Time Zone: {info["timezone"]}')
                    st.write(f'City IATA Code: {info["city_iata_code"]}')

                    if (info["country_name"] == "United States"):
                        st.write(f'Currency: Dollar (USD)')
                    elif (info["country_name"] == "Russia"):
                        st.write(f'Currency: Ruble (RUB)')
                    elif (info["country_name"] == "French Polynesia"):
                        st.write(f'Currency: Franc (CFP)')

                    for c in ctryJS["data"]:
                        if (c["country_iso2"] == info["country_iso2"]):
                            if (iso == True):
                                st.write(f'Country ISO Code: {c["country_iso3"]}')

                            st.write(f'Currency: {c["currency_name"]} ({c["currency_code"]})')

                            if (prefix == True):
                                st.write(f'Phone Prefix: +{c["phone_prefix"]}')
                            if (cont == True):
                                st.write(f'Continent: {c["continent"]}')
                        else:
                            haha += 1
                            extra = True
                            isoBool = iso
                            prefBool = prefix
                            contBool = cont
                        cnt += 1

                    if (haha == cnt) and (extra and lat == True):
                        st.write(f'No further info available.')
                    if (haha == cnt and isoBool == True):
                        st.write(f'No extra info available.')
                    if (haha == cnt and prefBool == True):
                        st.write(f'No extra info available.')
                    if (haha == cnt and contBool == True):
                        st.write(f'No extra info available.')

                    st.write(f'---------------------------------------')


elif category == 'Flights':
    endpoint = 'flights'
    flights_list = requestData(endpoint)
    data = flights_list

    flight_dict_array = []

    for flight in data["data"]:
        flight_dict = makeFlightDict(flight)
        flight_dict_array.append(flight_dict)

    filter = st.radio("Arrival or Departure",
                      ("Arrival", "Departure"))
    if filter == "Arrival":
        # time = st.time_input('Pick a time',datetime.time(0,00))
        st.checkbox("Use container width", value=False, key="use_container_width")
        df = load_data(flight_dict_array, filter)
        st.dataframe(df, use_container_width=st.session_state.use_container_width)
    if filter == "Departure":
        st.checkbox("Use container width", value=False, key="use_container_width")
        df = load_data(flight_dict_array, filter)
        st.dataframe(df, use_container_width=st.session_state.use_container_width)

    # st.write(flight_dict_array)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        bg = st.button('Click for a plane')
        if bg:
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("https://images.flyingmag.com/flyingma/wp-content/uploads/2022/06/23090933/AdobeStock_249454423-scaled.jpeg");
                    background-attachment: fixed;
                    background-size: cover
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    with col2:
        bg = st.button('Click for more planes')
        if bg:
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("https://nodeassets.nbcnews.com/cdnassets/projects/2017/08/airplane-mode/lax-takeoff-02.jpg");
                    background-attachment: fixed;
                    background-size: cover
                }}
                </style>
                """,
                unsafe_allow_html=True
            )