from bs4 import BeautifulSoup
from .constants import WIKIPEDIA_BIRD_URL, WIKIPEDIA_IMAGE_BASE_URL


async def get_bird_deets(bird, session):
    """
    Pulls an image from the wikipedia page

    First, gets the entrity of the wikipedia article
    and filters out anchor tags with href's ending in .jpg
    If no jpgs, then return None
    Otherwise, open url of first jpg and grab the img src
    Return img src of first jpg
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

        print(WIKIPEDIA_IMAGE_BASE_URL.format(link=all_img_hrefs[0]))

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
                        img_url = "https://" + all_imgs[img].split('//')[1]

            return img_url
