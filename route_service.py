
import requests
import openrouteservice
import os
from dotenv import load_dotenv

load_dotenv()

# Keep your real ORS API key here
API_KEY = os.getenv("ORS_API_KEY")

client = openrouteservice.Client(key=API_KEY)


def get_coordinates(place):

    url = "https://nominatim.openstreetmap.org/search"

    parameters = {
        "q": place + ", India",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "RoadSafetyCollegeProject/1.0"
    }

    response = requests.get(
        url,
        params=parameters,
        headers=headers,
        timeout=10
    )

    result = response.json()

    if not result:
        return None

    latitude = float(result[0]["lat"])
    longitude = float(result[0]["lon"])

    # ORS needs longitude first, then latitude
    return [longitude, latitude]


def get_route(
    source,
    destination,
    source_coordinates=None,
    destination_coordinates=None
):

    # ==================================================
    # GET SOURCE COORDINATES
    # ==================================================

    if source_coordinates is None:

        source_coordinates = get_coordinates(
            source
        )


    # ==================================================
    # GET DESTINATION COORDINATES
    # ==================================================

    if destination_coordinates is None:

        destination_coordinates = get_coordinates(
            destination
        )


    # ==================================================
    # CHECK COORDINATES
    # ==================================================

    if source_coordinates is None:

        return {
            "error": "Source location not found"
        }

    if destination_coordinates is None:
        return {
            "error": "Destination location not found"
        }

    # Get the driving route from ORS
    route = client.directions(
        coordinates=[
            source_coordinates,
            destination_coordinates
        ],
        profile="driving-car",
        format="geojson",
        extra_info=[
            "surface",
            "waytype",
            "waycategory"
        ]
    )

    print(
        "Number of routes found:",
        len(route["features"])
    )

    route_info = route["features"][0]

    properties = route_info["properties"]
    extras = properties.get(
        "extras",
        {}
    )

    surface_info = extras.get(
        "surface",
        {}
    )

    surface_summary = surface_info.get(
        "summary",
        []
    )
    # Calculate percentage of known asphalt/paved surface

    asphalt_percentage = 0
    paved_percentage = 0
    concrete_percentage = 0

    for surface in surface_summary:

        value = surface.get("value")
        amount = surface.get("amount", 0)

        if value == 3:
            asphalt_percentage += amount

        elif value == 1:
            paved_percentage += amount

        elif value == 4:
            concrete_percentage += amount
    good_surface_percentage = (
        asphalt_percentage
        + paved_percentage
        + concrete_percentage
    )

    print("\n========== ROAD SURFACE ==========")

    print(
        "Asphalt:",
        round(asphalt_percentage, 2),
        "%"
    )

    print(
        "Paved:",
        round(paved_percentage, 2),
        "%"
    )

    print(  
        "Concrete:",
        round(concrete_percentage, 2),
        "%"
    )

    print(
        "Good surface:",
        round(good_surface_percentage, 2),
        "%"
    )

    print("==================================")

    # Get route points
    route_points = route_info["geometry"]["coordinates"]

    # ==================================================
    # EXTRACT ROAD INFORMATION
    # ==================================================

    major_roads = []
    state_roads = []
    other_roads = []

    roundabouts = 0
    service_roads = 0
    flyovers_underpasses = 0

    segments = properties.get("segments", [])

    for segment in segments:

        steps = segment.get("steps", [])

        for step in steps:

            road_name = step.get("name", "")

            instruction = step.get(
                "instruction",
                ""
            )

            # ------------------------------------------
            # Road names
            # ------------------------------------------

            if road_name and road_name != "-":

                if (
                    "NH" in road_name
                    or "National Highway" in road_name
                ):

                    if road_name not in major_roads:
                        major_roads.append(
                            road_name
                        )

                elif (
                    "SH" in road_name
                    or "State Highway" in road_name
                ):

                    if road_name not in state_roads:
                        state_roads.append(
                            road_name
                        )

                else:

                    if road_name not in other_roads:
                        other_roads.append(
                            road_name
                        )

            # ------------------------------------------
            # Roundabout
            # ------------------------------------------

            if "roundabout" in instruction.lower():

                roundabouts += 1

            # ------------------------------------------
            # Service road
            # ------------------------------------------

            if "service road" in road_name.lower():

                service_roads += 1

            # ------------------------------------------
            # Flyover / Underpass
            # ------------------------------------------

            road_text = (
                road_name + " " + instruction
            ).lower()

            if (
                "flyover" in road_text
                or "underpass" in road_text
                or "elevated road" in road_text
            ):

                flyovers_underpasses += 1

    # ==================================================
    # ROUTE DISTANCE AND DURATION
    # ==================================================

    distance_km = (
        properties["summary"]["distance"]
        / 1000
    )

    duration_minutes = (
        properties["summary"]["duration"]
        / 60
    )

    # ==================================================
    # PRINT ROAD INFORMATION
    # ==================================================

    print(
        "\n========== ROAD INFORMATION =========="
    )

    print(
        "Major Highways:",
        major_roads
    )

    print(
        "State Highways:",
        state_roads
    )

    print(
        "Other Roads:",
        other_roads
    )

    print(
        "Roundabouts:",
        roundabouts
    )

    print(
        "Service Roads:",
        service_roads
    )

    print(
        "Flyovers / Underpasses:",
        flyovers_underpasses
    )

    print(
        "======================================\n"
    )

    # ==================================================
    # RETURN RESULT
    # ==================================================

    return {

        "source": source,

        "destination": destination,

        "source_coordinates":
            source_coordinates,

        "destination_coordinates":
            destination_coordinates,

        "distance_km":
            round(distance_km, 2),

        "duration_minutes":
            round(duration_minutes, 2),

        "route_points":
                route_points,

        # NEW ROAD INFORMATION

        "major_roads":
            major_roads,

        "state_roads":
            state_roads,

        "other_roads":
            other_roads,

        "roundabouts":
            roundabouts,

        "service_roads":
            service_roads,

    "flyovers_underpasses":
        flyovers_underpasses,

    "asphalt_percentage":
        round(asphalt_percentage, 2),

    "paved_percentage":
        round(paved_percentage, 2),

    "concrete_percentage":
        round(concrete_percentage, 2),

    "good_surface_percentage":
        round(good_surface_percentage, 2)
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    result = get_route(
        "Vellore",
        "chennai"
    )

    print("\n========== FINAL RESULT ==========")

    print(
        "Distance:",
        result["distance_km"],
        "km"
    )

    print(
        "Duration:",
        result["duration_minutes"],
        "minutes"
    )

    print(
        "Major Roads:",
        result["major_roads"]
    )

    print(
        "State Roads:",
        result["state_roads"]
    )

    print(
        "Roundabouts:",
        result["roundabouts"]
    )

    print(
        "Service Roads:",
        result["service_roads"]
    )

    print(
        "Flyovers / Underpasses:",
        result["flyovers_underpasses"]
    )

    print(
        "================================="
    )