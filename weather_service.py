import requests


# =====================================================
# GET WEATHER FOR ONE LOCATION
# =====================================================

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            url,
            params=parameters,
            timeout=10
        )

        # If Open-Meteo temporarily rate-limits us
        if response.status_code == 429:

            print("Open-Meteo rate limit reached. Using fallback weather.")

            return {
                "temperature": 25,
                "weather": "clear"
            }

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            data = data[0]

        temperature = data["current"]["temperature_2m"]
        weather_code = data["current"]["weather_code"]

        if weather_code in [0, 1, 2, 3]:
            weather = "clear"

        elif weather_code in [45, 48]:
            weather = "fog"

        elif weather_code in [
            51, 53, 55,
            56, 57,
            61, 63, 65,
            66, 67,
            80, 81, 82
        ]:
            weather = "rain"

        elif weather_code in [
            71, 73, 75,
            77,
            85, 86
        ]:
            weather = "snow"

        elif weather_code in [95, 96, 99]:
            weather = "storm"

        else:
            weather = "clear"

        return {
            "temperature": temperature,
            "weather": weather
        }

    except Exception as e:

        print("Weather API error:", e)

        # Keep route prediction working even if
        # the weather service is temporarily unavailable
        return {
            "temperature": 25,
            "weather": "clear"
        }
# =====================================================
# GET WEATHER FOR ROUTE POINTS
# =====================================================
# =====================================================
# GET WEATHER FOR ROUTE POINTS
# =====================================================

def get_route_weather(route_points):

    if not route_points:
        return []

    number_of_points = len(route_points)

    # -------------------------------------------------
    # SAMPLE ONLY 5 POINTS FROM THE ROUTE
    # -------------------------------------------------

    sample_indexes = [
        0,
        number_of_points // 4,
        number_of_points // 2,
        (3 * number_of_points) // 4,
        number_of_points - 1
    ]

    # Remove duplicate indexes
    sample_indexes = list(dict.fromkeys(sample_indexes))

    selected_points = [
        route_points[index]
        for index in sample_indexes
    ]

    # ORS coordinates:
    # [longitude, latitude]

    longitudes = [
        point[0]
        for point in selected_points
    ]

    latitudes = [
        point[1]
        for point in selected_points
    ]

    print("Checking weather for", len(selected_points), "route points")

    # -------------------------------------------------
    # ONE OPEN-METEO REQUEST FOR ALL POINTS
    # -------------------------------------------------

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": ",".join(map(str, latitudes)),
        "longitude": ",".join(map(str, longitudes)),
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            url,
            params=parameters,
            timeout=10
        )

        # Rate limit fallback
        if response.status_code == 429:

            print(
                "Open-Meteo rate limit reached. "
                "Using fallback weather."
            )

            return [
                {
                    "latitude": latitudes[i],
                    "longitude": longitudes[i],
                    "temperature": 25,
                    "weather": "clear"
                }
                for i in range(len(selected_points))
            ]

        response.raise_for_status()

        data = response.json()

        # Open-Meteo returns a list when
        # multiple locations are requested.
        if not isinstance(data, list):
            data = [data]

        weather_results = []

        for i, weather_data in enumerate(data):

            temperature = weather_data["current"]["temperature_2m"]

            weather_code = weather_data["current"]["weather_code"]

            # -------------------------------------------------
            # CONVERT WEATHER CODE
            # -------------------------------------------------

            if weather_code in [0, 1, 2, 3]:

                weather = "clear"

            elif weather_code in [45, 48]:

                weather = "fog"

            elif weather_code in [
                51, 53, 55,
                56, 57,
                61, 63, 65,
                66, 67,
                80, 81, 82
            ]:

                weather = "rain"

            elif weather_code in [
                71, 73, 75,
                77,
                85, 86
            ]:

                weather = "snow"

            elif weather_code in [95, 96, 99]:

                weather = "storm"

            else:

                weather = "clear"

            weather_results.append({

                "latitude": latitudes[i],

                "longitude": longitudes[i],

                "temperature": temperature,

                "weather": weather

            })

        return weather_results

    except Exception as e:

        print("Weather API error:", e)

        # Keep prediction working even if
        # weather service fails.

        return [
            {
                "latitude": latitudes[i],
                "longitude": longitudes[i],
                "temperature": 25,
                "weather": "clear"
            }
            for i in range(len(selected_points))
        ]
# ===================
# GET OVERALL ROUTE WEATHER
# =====================================================

def get_overall_route_weather(route_points):

    weather_results = get_route_weather(

        route_points

    )


    if not weather_results:

        return {

            "overall_weather":
                "clear",

            "average_temperature":
                0

        }


    # -----------------------------------------
    # TEMPERATURE
    # -----------------------------------------

    temperatures = [

        item["temperature"]

        for item in weather_results

    ]


    average_temperature = round(

        sum(temperatures)
        /
        len(temperatures),

        2

    )


    # -----------------------------------------
    # WEATHER
    # -----------------------------------------

    weather_list = [

        item["weather"]

        for item in weather_results

    ]


    # Give priority to dangerous weather

    if "storm" in weather_list:

        overall_weather = "storm"

    elif "snow" in weather_list:

        overall_weather = "snow"

    elif "rain" in weather_list:

        overall_weather = "rain"

    elif "fog" in weather_list:

        overall_weather = "fog"

    else:

        overall_weather = "clear"


    return {

        "overall_weather":
            overall_weather,

        "average_temperature":
            average_temperature

    }