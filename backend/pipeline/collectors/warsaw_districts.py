"""Geographic anchors for Warsaw's 18 districts.

Approximate centroids (WGS84) used to bias/restrict Google Places searches so
coverage spans the whole city rather than clustering in the centre. Coordinates
are good enough to anchor a ~3 km search radius per district.
"""

from typing import NamedTuple


class DistrictCentroid(NamedTuple):
    """A district name paired with its approximate centre coordinates."""

    name: str
    latitude: float
    longitude: float


WARSAW_DISTRICT_CENTROIDS: tuple[DistrictCentroid, ...] = (
    DistrictCentroid("Bemowo", 52.2545, 20.9110),
    DistrictCentroid("Białołęka", 52.3210, 20.9960),
    DistrictCentroid("Bielany", 52.2900, 20.9340),
    DistrictCentroid("Mokotów", 52.1900, 21.0360),
    DistrictCentroid("Ochota", 52.2150, 20.9740),
    DistrictCentroid("Praga-Południe", 52.2440, 21.0700),
    DistrictCentroid("Praga-Północ", 52.2560, 21.0360),
    DistrictCentroid("Rembertów", 52.2620, 21.1600),
    DistrictCentroid("Śródmieście", 52.2300, 21.0120),
    DistrictCentroid("Targówek", 52.2900, 21.0550),
    DistrictCentroid("Ursus", 52.1950, 20.8830),
    DistrictCentroid("Ursynów", 52.1490, 21.0490),
    DistrictCentroid("Wawer", 52.1960, 21.1700),
    DistrictCentroid("Wesoła", 52.2490, 21.2300),
    DistrictCentroid("Wilanów", 52.1650, 21.0900),
    DistrictCentroid("Włochy", 52.1880, 20.9390),
    DistrictCentroid("Wola", 52.2360, 20.9580),
    DistrictCentroid("Żoliborz", 52.2700, 20.9810),
)

# Search terms (Polish + English) covering the main salon categories. Combined
# with each district centroid, these queries fan out across the city.
SEARCH_QUERIES: tuple[str, ...] = (
    "fryzjer",
    "salon fryzjerski",
    "barber shop",
    "salon kosmetyczny",
    "salon urody",
    "paznokcie manicure",
)
