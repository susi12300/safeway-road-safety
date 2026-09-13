import requests
import time
from datetime import datetime, timezone


# ============================================================
# WEATHER CACHE
# ============================================================

# Weather data is cached for 5 minutes.
# This reduces repeated Open-Meteo requests when multiple
# users request the same/similar route.
CACHE_DURATION = 300

_weather_cache = {}


# ============================================================
# WEATHER CODE CONVERSION
# ============================================================

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


# ============================================================
# SINGLE LOCATION WEATHER
# ============================================================

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    headers = {
        "User-Agent": "SafeWay-Road-Safety-Project/1.0"
    }

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                "Single-location weather attempt",
                attempt,
                "of",
                max_attempts
            )

            response = requests.get(
                url,
                params=parameters,
                headers=headers,
                timeout=10
            )

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if response.status_code == 429:

                print(
                    "Open-Meteo returned 429."
                )

                if attempt < max_attempts:

                    retry_after = response.headers.get(
                        "Retry-After"
                    )

                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except ValueError:
                            wait_time = attempt * 2
                    else:
                        wait_time = attempt * 2

                    wait_time = min(wait_time, 10)

                    print(
                        "Waiting",
                        wait_time,
                        "seconds before retry..."
                    )

                    time.sleep(wait_time)

                    continue

                raise RuntimeError(
                    "Live weather service is temporarily "
                    "rate limited. Please try again later."
                )

            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                data = data[0]

            if "current" not in data:

                raise RuntimeError(
                    "Weather service returned invalid data."
                )

            temperature = data["current"]["temperature_2m"]

            weather_code = data["current"]["weather_code"]

            weather = weather_code_to_text(
                weather_code
            )

            return {
                "temperature": temperature,
                "weather": weather
            }

        except RuntimeError:
            raise

        except Exception as e:

            print(
                "Weather API error:",
                repr(e)
            )

            if attempt < max_attempts:

                wait_time = attempt * 2

                print(
                    "Retrying in",
                    wait_time,
                    "seconds..."
                )

                time.sleep(wait_time)

            else:

                raise RuntimeError(
                    "Unable to obtain live weather data."
                )


# ============================================================
# ROUTE WEATHER
# ============================================================

def get_route_weather(route_points):

    if not route_points:

        raise RuntimeError(
            "No route points available for weather checking."
        )


    # --------------------------------------------------------
    # SELECT 5 REPRESENTATIVE POINTS
    # --------------------------------------------------------

    number_of_points = len(route_points)

    sample_indexes = [
        0,
        number_of_points // 4,
        number_of_points // 2,
        (3 * number_of_points) // 4,
        number_of_points - 1
    ]

    sample_indexes = list(
        dict.fromkeys(sample_indexes)
    )

    selected_points = [
        route_points[index]
        for index in sample_indexes
    ]


    longitudes = [
        point[0]
        for point in selected_points
    ]

    latitudes = [
        point[1]
        for point in selected_points
    ]


    print(
        "Checking live weather for",
        len(selected_points),
        "route points"
    )


    # --------------------------------------------------------
    # CACHE KEY
    # --------------------------------------------------------
    #
    # Round coordinates slightly so tiny coordinate
    # differences don't create unnecessary cache entries.
    #

    cache_key = tuple(
        (
            round(latitudes[i], 3),
            round(longitudes[i], 3)
        )
        for i in range(len(selected_points))
    )


    # --------------------------------------------------------
    # CHECK CACHE
    # --------------------------------------------------------

    current_time = time.time()

    cached_weather = _weather_cache.get(cache_key)

    if cached_weather:

        cached_time, cached_data = cached_weather

        cache_age = current_time - cached_time

        if cache_age < CACHE_DURATION:

            print(
                "Using cached weather data."
            )

            print(
                "Cache age:",
                round(cache_age, 1),
                "seconds"
            )

            return cached_data

        else:

            print(
                "Cached weather expired."
            )

            del _weather_cache[cache_key]


    # --------------------------------------------------------
    # OPEN-METEO REQUEST
    # --------------------------------------------------------

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": ",".join(
            map(str, latitudes)
        ),

        "longitude": ",".join(
            map(str, longitudes)
        ),

        "current": "temperature_2m,weather_code",

        "timezone": "auto"
    }


    headers = {
        "User-Agent": "SafeWay-Road-Safety-Project/1.0"
    }


    # --------------------------------------------------------
    # RETRY SETTINGS
    # --------------------------------------------------------

    max_attempts = 3


    for attempt in range(1, max_attempts + 1):

        try:

            print(
                "Weather API attempt",
                attempt,
                "of",
                max_attempts
            )


            response = requests.get(
                url,
                params=parameters,
                headers=headers,
                timeout=10
            )


            # =================================================
            # 429 RATE LIMIT
            # =================================================

            if response.status_code == 429:

                print(
                    "Open-Meteo returned 429."
                )


                if attempt < max_attempts:

                    # Open-Meteo/server may tell us how long
                    # to wait using Retry-After.
                    retry_after = response.headers.get(
                        "Retry-After"
                    )


                    if retry_after:

                        try:

                            wait_time = int(
                                retry_after
                            )

                        except ValueError:

                            wait_time = attempt * 2

                    else:

                        # Controlled exponential backoff:
                        #
                        # attempt 1 -> 2 seconds
                        # attempt 2 -> 4 seconds
                        #
                        wait_time = attempt * 2


                    # Don't wait an unreasonable amount
                    # during an app request.
                    wait_time = min(
                        wait_time,
                        10
                    )


                    print(
                        "Waiting",
                        wait_time,
                        "seconds before retry..."
                    )


                    time.sleep(
                        wait_time
                    )


                    continue


                # All attempts failed.
                raise RuntimeError(
                    "Live weather service is temporarily "
                    "rate limited. Please try again later."
                )


            # =================================================
            # OTHER HTTP ERRORS
            # =================================================

            response.raise_for_status()


            # =================================================
            # READ RESPONSE
            # =================================================

            data = response.json()


            if not isinstance(data, list):

                data = [data]


            # We requested one weather result for each
            # selected route point.
            if len(data) != len(selected_points):

                raise RuntimeError(
                    "Weather service returned incomplete "
                    "route weather data."
                )


            # =================================================
            # PROCESS WEATHER
            # =================================================

            weather_results = []


            for i, weather_data in enumerate(data):

                if "current" not in weather_data:

                    raise RuntimeError(
                        "Weather service returned invalid "
                        "data for a route point."
                    )


                temperature = weather_data[
                    "current"
                ][
                    "temperature_2m"
                ]


                weather_code = weather_data[
                    "current"
                ][
                    "weather_code"
                ]


                weather = weather_code_to_text(
                    weather_code
                )


                weather_results.append({

                    "latitude": latitudes[i],

                    "longitude": longitudes[i],

                    "temperature": temperature,

                    "weather": weather

                })


            # =================================================
            # SAVE TO CACHE
            # =================================================

            _weather_cache[cache_key] = (
                time.time(),
                weather_results
            )


            print(
                "Live weather received successfully."
            )


            print(
                "Weather data cached for",
                CACHE_DURATION,
                "seconds."
            )


            return weather_results


        except RuntimeError:
            raise


        except Exception as e:

            print(
                "Weather API error:",
                repr(e)
            )


            if attempt < max_attempts:

                wait_time = attempt * 2


                print(
                    "Retrying in",
                    wait_time,
                    "seconds..."
                )


                time.sleep(
                    wait_time
                )


                continue


            raise RuntimeError(
                "Unable to obtain live weather data."
            )


# ============================================================
# OVERALL ROUTE WEATHER
# ============================================================

def get_overall_route_weather(route_points):

    weather_results = get_route_weather(
        route_points
    )


    if not weather_results:

        raise RuntimeError(
            "Live weather data is unavailable."
        )


    # --------------------------------------------------------
    # AVERAGE TEMPERATURE
    # --------------------------------------------------------

    temperatures = [
        item["temperature"]
        for item in weather_results
    ]


    average_temperature = round(
        sum(temperatures) /
        len(temperatures),
        2
    )


    # --------------------------------------------------------
    # OVERALL WEATHER
    # --------------------------------------------------------

    weather_list = [
        item["weather"]
        for item in weather_results
    ]


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


    print(
        "Overall route weather:",
        overall_weather
    )


    print(
        "Average temperature:",
        average_temperature
    )


    return {

        "overall_weather": overall_weather,

        "average_temperature": average_temperature

    }