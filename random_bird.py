from random import randrange
import datetime
import urllib
from bs4 import BeautifulSoup
from constants import WIKIPEDIA_BIRDS_LIST_URL, WIKIPEDIA_BIRD_URL, WIKIPEDIA_IMAGE_BASE_URL


def _should_refresh_cache(app):
    """
    don't pull list of birds from cache if it was last updated over an hour ago
    """
    if len(app.config["birds"]) < 10:
        return True

    time_diff = datetime.datetime.now() - app.config["last_refreshed"]
    if time_diff.total_seconds() >= 3600:
        return True
    
    return False


async def _get_list_of_birds(session):
    """
    calls wikipedia API to get the contents of the 'List of birds by common name' article
    returns full HTML
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
    uses bs4 to parse the html returned from wikipedia's API
    returns a list of all html anchor tags
    """
    soup = BeautifulSoup(unfiltered_bird_list, "html.parser")
    all_links = [link.get("href") for link in soup.find_all("a")]
    return all_links


def _random_number(max):
    return randrange(0, max)


async def _select_bird(all_birds, session):
    """
    takes a list of all html anchor tags, picks a random one,
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
        print(f" + trying bird {selected_bird}...")
        bird_image = await _get_bird_deets(selected_bird, session)
        print(f" + image url is {bird_image}")
    print(f" + decided on {selected_bird} - {bird_image}")
    return selected_bird, bird_image



async def _get_bird_deets(bird, session):
    """
    pulls an image from the wikipedia page

    first, gets the entrity of the wikipedia article
    and filters out anchor tags with href's ending in .jpg
    if no jpgs, then return None
    otherwise, open url of first jpg and grab the img src
    return img src of first jpg
    """

    async with await session.get(
        WIKIPEDIA_BIRD_URL.format(bird=bird, data="text")
    ) as text_resp:
        if text_resp.status == 200:
            text_resp_j = await text_resp.json()
            text_resp_j = text_resp_j["parse"]["text"]["*"]
            soup = BeautifulSoup(text_resp_j, "html.parser")
            all_links = [link.get("href") for link in soup.find_all("a")]
            all_img_hrefs = []
            for link in all_links:
                if str(link).endswith(".jpg"):
                    all_img_hrefs.append(link)
            if len(all_img_hrefs) == 0:
                return None

    async with await session.get(
        WIKIPEDIA_IMAGE_BASE_URL.format(link=all_img_hrefs[0])
    ) as img_resp:
        if img_resp.status == 200:
            img_resp = await img_resp.text()
            soup = BeautifulSoup(img_resp, "html.parser")
            all_imgs = [img.get("src") for img in soup.find_all("img")]

            img = 0
            invalid_img = True
            while img < len(all_imgs) and invalid_img is True:
                if "svg" in all_imgs[img] or "status" in all_imgs[img] or "wikipedia.png" in all_imgs[img]:
                    img += 1
                else:
                    invalid_img = False
                    img_url = "https://" + all_imgs[img].split("//")[1]

        return img_url


async def get_random_bird(app, session):
    """
    main function
    """
    try:
        print("LOG: issuing bird request")

        if _should_refresh_cache(app) is True:
            print(" + fetching list of birds...")
            unfiltered_bird_list = await _get_list_of_birds(session)
            if unfiltered_bird_list is None:
                return {"error": "Failed to parse birds."}

            all_birds = _parse_bird_list(unfiltered_bird_list)
            app.config["birds"] = all_birds
            app.config["last_refreshed"] = datetime.datetime.now()
        
        else:
            print(" + pulling birds list from cache...")
            all_birds = app.config["birds"]

        selected_bird, bird_image = await _select_bird(all_birds, session)
        selected_bird_parsed = urllib.parse.unquote(selected_bird).replace("_", " ").lower()
        return {"name": selected_bird_parsed, "image": bird_image}
    except Exception as e:
        print(e)
        return {"error": "An unexpected error occurred."}