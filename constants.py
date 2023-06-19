WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_BIRD_LIST_PAGE_ID = "20184453"
WIKIPEDIA_SEARCH_URL = f"{WIKIPEDIA_BASE_URL}?action=query&list=search&format=json&origin=*&srsearch=list%20of%20birds%20by%20common%20name"
WIKIPEDIA_BIRDS_LIST_URL = f"{WIKIPEDIA_BASE_URL}?action=parse&format=json&origin=*&pageid={WIKIPEDIA_BIRD_LIST_PAGE_ID}&prop=text"
WIKIPEDIA_BIRD_URL = (
    WIKIPEDIA_BASE_URL + "?action=parse&format=json&origin=*&page={bird}&prop={data}"
)
WIKIPEDIA_IMAGE_BASE_URL = "https://en.wikipedia.org{link}"
