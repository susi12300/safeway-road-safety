import requests
import time


# =====================================================
# SETTINGS
# =====================================================

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

CACHE_DURATION = 300

_weather_cache = {}


# =====================================================
# CONVERT WEATHER CODE
# =====================================================

def weather_code_to_text(weather_code):

    if weather_code in [0, 1, 2, 3]:
        return "clear"

    elif weather_code in [45, 48]:
        return "fog"

    elif weather_code in [
        51, 53, 55,
        56, 57,
        61, 63, 65,
        66, 67,
        80, 81, 82
    ]:
        return "rain"

    elif weather_code in [
        71, 73, 75,
        77, 85, 86
    ]:
        return "snow"

    elif weather_code in [
        95, 96, 99
    ]:
        return "storm"

    else:
        return "clear"


# =====================================================
# CACHE KEY
# =====================================================

def create_cache_key(points):

    return tuple(
        (
            round(point[1], 3),
            round(point[0], 3)
        )
        for point in points
    )


# =====================================================
# GET WEATHER FOR ROUTE
# =====================================================

def get_route_weather(route_points):

    if not route_points:
        return []


    number_of_points = len(route_points)


    # -------------------------------------------------
    # ONLY 3 POINTS
    #
    # SOURCE
    # MIDPOINT
    # DESTINATION
    # -------------------------------------------------

    sample_indexes = [
        0,
        number_of_points // 2,
        number_of_points - 1
    ]


    # Remove duplicates for very short routes

    sample_indexes = list(
        dict.fromkeys(sample_indexes)
    )


    selected_points = [
        route_points[index]
        for index in sample_indexes
    ]


    # -------------------------------------------------
    # CHECK CACHE
    # -------------------------------------------------

    cache_key = create_cache_key(
        selected_points
    )


    current_time = time.time()


    if cache_key in _weather_cache:

        cached = _weather_cache[cache_key]


        if (
            current_time - cached["time"]
            < CACHE_DURATION
        ):

            print(
                "Using cached weather data."
            )

            return cached["weather"]


    # -------------------------------------------------
    # CREATE ONE REQUEST FOR ALL 3 POINTS
    # -------------------------------------------------

    latitudes = ",".join(
        str(point[1])
        for point in selected_points
    )


    longitudes = ",".join(
        str(point[0])
        for point in selected_points
    )


    parameters = {

        "latitude": latitudes,

        "longitude": longitudes,

        "current":
            "temperature_2m,weather_code",

        "timezone":
            "auto"
    }


    headers = {

        "User-Agent":
            "SafeWay-Road-Safety-Project/1.0"
    }


    # -------------------------------------------------
    # REQUEST
    # -------------------------------------------------

    for attempt in range(1, 4):

        try:

            print(
                f"Weather API attempt {attempt} of 3"
            )


            response = requests.get(

                WEATHER_URL,

                params=parameters,

                headers=headers,

                timeout=10
            )


            # -------------------------------------------------
            # RATE LIMIT
            # -------------------------------------------------

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After"
                )


                if retry_after:

                    try:
                        wait_time = min(
                            int(retry_after),
                            10
                        )

                    except ValueError:

                        wait_time = 2

                else:

                    wait_time = 2 * attempt


                print(
                    "Open-Meteo returned 429."
                )


                if attempt < 3:

                    print(
                        f"Waiting {wait_time} seconds..."
                    )

                    time.sleep(
                        wait_time
                    )

                    continue


                # Don't keep hitting the API
                break


            # -------------------------------------------------
            # OTHER HTTP ERRORS
            # -------------------------------------------------

            response.raise_for_status()


            data = response.json()


            # -------------------------------------------------
            # MULTIPLE LOCATIONS RETURN LIST
            # -------------------------------------------------

            if not isinstance(data, list):

                data = [data]


            if len(data) != len(selected_points):

                raise RuntimeError(
                    "Weather API returned an unexpected "
                    "number of locations."
                )


            weather_results = []


            # -------------------------------------------------
            # PROCESS WEATHER
            # -------------------------------------------------

            for point, weather_data in zip(
                selected_points,
                data
            ):

                temperature = (
                    weather_data["current"]
                    ["temperature_2m"]
                )


                weather_code = (
                    weather_data["current"]
                    ["weather_code"]
                )


                weather = weather_code_to_text(
                    weather_code
                )


                weather_results.append({

                    "latitude":
                        point[1],

                    "longitude":
                        point[0],

                    "temperature":
                        temperature,

                    "weather":
                        weather

                })


            # -------------------------------------------------
            # SAVE SUCCESSFUL RESULT
            # -------------------------------------------------

            _weather_cache[cache_key] = {

                "time":
                    time.time(),

                "weather":
                    weather_results
            }


            print(
                "Weather data received successfully."
            )


            return weather_results


        except requests.exceptions.RequestException as e:

            print(
                "Weather request error:",
                repr(e)
            )


            if attempt < 3:

                wait_time = 2 * attempt

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

            else:

                break


        except Exception as e:

            print(
                "Weather processing error:",
                repr(e)
            )

            break


    # -------------------------------------------------
    # USE OLD SUCCESSFUL CACHE IF AVAILABLE
    # -------------------------------------------------

    if cache_key in _weather_cache:

        print(
            "Using previously successful "
            "weather data."
        )

        return _weather_cache[cache_key]["weather"]


    # -------------------------------------------------
    # NO WEATHER AVAILABLE
    # -------------------------------------------------

    print(
        "Live weather could not be obtained."
    )

    raise RuntimeError(
        "Live weather service is temporarily unavailable. "
        "Please try again later."
    )


# =====================================================
# GET OVERALL ROUTE WEATHER
# =====================================================

def get_overall_route_weather(route_points):

    weather_results = get_route_weather(
        route_points
    )


    if not weather_results:

        raise RuntimeError(
            "No weather data available."
        )


    # -------------------------------------------------
    # AVERAGE TEMPERATURE
    # -------------------------------------------------

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


    # -------------------------------------------------
    # WEATHER
    # -------------------------------------------------

    weather_list = [

        item["weather"]

        for item in weather_results

    ]


    # Dangerous weather gets priority

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