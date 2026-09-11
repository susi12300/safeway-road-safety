import openrouteservice

# Use your ORS API key
API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjVmNWQzYzViNTdkZjQ1ZDc4NTMwOTRmMzJlMThmNmRiIiwiaCI6Im11cm11cjY0In0="

client = openrouteservice.Client(key=API_KEY)


def get_coordinates(place):

    result = client.pelias_search(
        text=place + ", Tamil Nadu, India"
    )

    coordinates = result["features"][0]["geometry"]["coordinates"]

    return coordinates


source = "Vellore"
destination = "Chennai"

source_coordinates = get_coordinates(source)
destination_coordinates = get_coordinates(destination)

print("Source:", source)
print("Coordinates:", source_coordinates)

print("\nDestination:", destination)
print("Coordinates:", destination_coordinates)