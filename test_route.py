import openrouteservice

# Paste your ORS API key between the quotes
API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjVmNWQzYzViNTdkZjQ1ZDc4NTMwOTRmMzJlMThmNmRiIiwiaCI6Im11cm11cjY0In0="

client = openrouteservice.Client(key=API_KEY)

# Coordinates are in this order:
# longitude, latitude

vellore = (79.1325, 12.9165)
chennai = (80.2707, 13.0827)

route = client.directions(
    coordinates=[vellore, chennai],
    profile="driving-car"
)

route_info = route["routes"][0]

distance_km = route_info["summary"]["distance"] / 1000
duration_minutes = route_info["summary"]["duration"] / 60

print("Route found successfully! 🛣️")
print("Distance:", round(distance_km, 2), "km")
print("Estimated duration:", round(duration_minutes, 2), "minutes")