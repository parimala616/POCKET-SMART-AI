from urllib.parse import quote_plus


BASES = {
    "amazon": "https://www.amazon.in/s?k={q}",

    "flipkart": "https://www.flipkart.com/search?q={q}",

    "ikea": "https://www.ikea.com/in/en/search/?q={q}",

    "myntra": "https://www.myntra.com/{q}",

    "meesho": "https://www.meesho.com/search?q={q}",

    "tanishq": "https://www.tanishq.co.in/search?q={q}",

    "caratlane": "https://www.caratlane.com/search?q={q}",

    "bluestone": "https://www.bluestone.com/search.html?query={q}",

    "swiggy": "https://www.swiggy.com/search?query={q}",

    "zomato": "https://www.zomato.com/search?q={q}",

    "bookmyshow": (
        "https://in.bookmyshow.com/explore/home/chennai"
    ),

    "booking": (
        "https://www.booking.com/search.html?ss={q}"
    ),

    "makemytrip": (
        "https://www.makemytrip.com/hotels/"
        "hotel-listing/?searchText={q}"
    ),

    "oyorooms": (
        "https://www.oyorooms.com/search/?location={q}"
    ),
}


def links(
    search_terms: str,
    platforms: list[str]
) -> dict[str, str]:

    query = quote_plus(search_terms)

    return {
        platform: BASES[platform].format(q=query)
        for platform in platforms
        if platform in BASES
    }