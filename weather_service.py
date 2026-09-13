import requests
import time


def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=parameters, timeout=5)

        if response.status_code == 429:
            print("Open-Meteo rate limit reached.")
            return None

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
            51, 53, 55, 56, 57,
            61, 63, 65, 66, 67,
            80, 81, 82
        ]:
            weather = "rain"

        elif weather_code in [71, 73, 75, 77, 85, 86]:
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
        return None


def get_route_weather(route_points):

    if not route_points:
        raise RuntimeError("No route points available for weather checking.")

    number_of_points = len(route_points)

    sample_indexes = [
        0,
        number_of_points // 4,
        number_of_points // 2,
        (3 * number_of_points) // 4,
        number_of_points - 1
    ]

    sample_indexes = list(dict.fromkeys(sample_indexes))

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

    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        "latitude": ",".join(map(str, latitudes)),
        "longitude": ",".join(map(str, longitudes)),
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

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
                timeout=5
            )

            # Too many requests
            if response.status_code == 429:

                print(
                    "Open-Meteo returned 429."
                    " Waiting before retry..."
                )

                if attempt < max_attempts:
                    time.sleep(attempt)

                    continue

                raise RuntimeError(
                    "Live weather service is temporarily "
                    "rate limited. Please try again."
                )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                data = [data]

            # Make sure we received weather for
            # every requested route point.
            if len(data) != len(selected_points):

                raise RuntimeError(
                    "Weather service returned incomplete "
                    "route weather data."
                )

            weather_results = []

            for i, weather_data in enumerate(data):

                temperature = weather_data[
                    "current"
                ]["temperature_2m"]

                weather_code = weather_data[
                    "current"
                ]["weather_code"]

                if weather_code in [0, 1, 2, 3]:
                    weather = "clear"

                elif weather_code in [45, 48]:
                    weather = "fog"

                elif weather_code in [
                    51, 53, 55, 56, 57,
                    61, 63, 65, 66, 67,
                    80, 81, 82
                ]:
                    weather = "rain"

                elif weather_code in [
                    71, 73, 75, 77, 85, 86
                ]:
                    weather = "snow"

                elif weather_code in [
                    95, 96, 99
                ]:
                    weather = "storm"

                else:
                    weather = "clear"

                weather_results.append({
                    "latitude": latitudes[i],
                    "longitude": longitudes[i],
                    "temperature": temperature,
                    "weather": weather
                })

            print(
                "Live weather received successfully."
            )

            return weather_results

        except RuntimeError:
            raise

        except Exception as e:

            print(
                "Weather API error:",
                e
            )

            if attempt < max_attempts:

                print(
                    "Retrying weather request..."
                )

                time.sleep(attempt)

                continue

            raise RuntimeError(
                "Unable to obtain live weather data."
            )


def get_overall_route_weather(route_points):

    weather_results = get_route_weather(
        route_points
    )

    if not weather_results:

        raise RuntimeError(
            "Live weather data is unavailable."
        )

    temperatures = [
        item["temperature"]
        for item in weather_results
    ]

    average_temperature = round(
        sum(temperatures) /
        len(temperatures),
        2
    )

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