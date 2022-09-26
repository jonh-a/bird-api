from random import randrange
import urllib
from bs4 import BeautifulSoup
from .constants import WIKIPEDIA_BIRDS_LIST_URL
from .get_bird_deets import get_bird_deets


async def _get_list_of_birds(session):
    """
    Calls wikipedia API to get the contents of the 'List of birds by common name' article
    Returns full HTML
    """
    async with session.get(WIKIPEDIA_BIRDS_LIST_URL) as resp:
        if resp.status == 200:
            resp_j = await resp.json()
            full_text = resp_j["parse"]["text"]["*"]
            return full_text
        else:
            return None


def _parse_bird_list(unfiltered_bird_list):
    """
    Uses bs4 to parse the html returned from wikipedia's API
    Returns a list of all html anchor tags
    """
    soup = BeautifulSoup(unfiltered_bird_list, "html.parser")
    all_links = [link.get("href") for link in soup.find_all("a")]
    return all_links


def _random_number(max):
    return randrange(0, max)


async def select_bird(all_birds, session):
    """
    Takes a list of all html anchor tags, picks a random one,
    and checks that it is in fact a wikipedia article for a bird
    """
    invalid_article_content = [
        "#",
        "/wiki/wikipedia",
        "edit",
        "https://",
        "/w/",
        "list",
    ]
    invalid_bird = True
    bird_image = None
    while invalid_bird is True or bird_image is None:
        n = _random_number(len(all_birds))
        selected_bird_title = all_birds[n]
        invalid_bird = any(
            test in selected_bird_title.lower() for test in invalid_article_content
        )
        selected_bird = selected_bird_title.split("/wiki/")[-1]
        print(f"LOG: trying bird {selected_bird}...")
        bird_image = await get_bird_deets(selected_bird, session)
        print(f"LOG: image url is {bird_image}")
    print(f"LOG: decided on {selected_bird} - {bird_image}")
    return selected_bird, bird_image


async def get_random_bird(session):
    print("LOG: issuing bird request")
    unfiltered_bird_list = await _get_list_of_birds(session)
    if unfiltered_bird_list is None:
        return {"error": "Failed to parse birds."}
    all_birds = _parse_bird_list(unfiltered_bird_list)
    selected_bird, bird_image = await select_bird(all_birds, session)
    selected_bird_parsed = urllib.parse.unquote(selected_bird).replace("_", " ").lower()
    return {"name": selected_bird_parsed, "image": bird_image}
