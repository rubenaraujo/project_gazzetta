import requests
from bs4 import BeautifulSoup
import os
import time
from email.utils import parsedate_to_datetime


BASE_URL = "https://capasjornais.pt/"
PROXY_PREFIX = "https://corsproxy.ruben-araujo.workers.dev/corsproxy/?apiurl="

def proxied_url(url):
    return f"{PROXY_PREFIX}{url}"

CATEGORIES = {
    "JornaisNacionais": "https://capasjornais.pt/capas/JornaisNacionais.html",
    "Revistas": "https://capasjornais.pt/capas/Revistas.html",
    "JornaisDesportivos": "https://capasjornais.pt/capas/JornaisDesportivos.html",
    "RevistasTecnologia": "https://capasjornais.pt/capas/RevistasTecnologia.html",
    "RevistasCarros": "https://capasjornais.pt/capas/RevistasCarros.html",
    "RevistasModa": "https://capasjornais.pt/capas/RevistasModa.html",
}

def get_full_image(url):
    """Goes to the individual cover page and returns the link to the high-res image"""
    resp = requests.get(proxied_url(url))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    img = soup.find("img", class_="img-fluid")
    if img and img.get("src"):
        img_url = img["src"]
        if not img_url.startswith("http"):
            img_url = BASE_URL.rstrip("/") + "/" + img_url.lstrip("/")
        return img_url
    return None

def fetch_covers(category, url):
    resp = requests.get(proxied_url(url))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    covers = []
    blocks = soup.find_all("div", class_="col-xs-6")  # each cover in a block

    for block in blocks:
        img = block.find("img", class_="img-thumbnail")
        h2 = block.find("h2")
        date_div = block.find("div", class_="tinydate")
        a_tag = block.find("a", href=True)

        if not img or not h2 or not date_div or not a_tag:
            continue

        name = h2.text.strip()
        date = date_div.text.strip().replace(" ", "_")

        # Thumbnail URL
        thumb_url = img["src"]
        if not thumb_url.startswith("http"):
            thumb_url = BASE_URL.rstrip("/") + "/" + thumb_url.lstrip("/")

        # Individual cover page
        detail_url = a_tag["href"]
        if not detail_url.startswith("http"):
            detail_url = BASE_URL.rstrip("/") + "/" + detail_url.lstrip("/")

        # Fetch the high-resolution image
        full_img_url = get_full_image(detail_url)

        covers.append({
            "name": name,
            "date": date,
            "thumb_url": thumb_url,
            "image_url": full_img_url
        })
    return covers

def download_images(covers, category, base_dir="images"):

    # folders: one for covers and another for thumbnails
    full_dir = os.path.join(base_dir, "covers", category)
    thumb_dir = os.path.join(base_dir, "thumbnails", category)
    os.makedirs(full_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    def should_download(remote_url, local_path):
        if not os.path.exists(local_path):
            return True  # File does not exist, download
        try:
            head = requests.head(proxied_url(remote_url), timeout=10)
            if head.status_code != 200:
                return False  # Can't check, skip
            last_mod = head.headers.get("Last-Modified")
            if last_mod:
                remote_time = parsedate_to_datetime(last_mod).timestamp()
                local_time = os.path.getmtime(local_path)
                return remote_time > local_time
            else:
                # No Last-Modified header, skip if file exists
                return False
        except Exception as e:
            print(f"    ! Error checking remote file {remote_url}: {e}")
            return False

    # Track filenames for current run
    current_full_filenames = set()
    current_thumb_filenames = set()

    for cover in covers:
        safe_name = cover['name'].replace(" ", "_")
        fname = f"{safe_name}_{cover['date']}.jpg"

        # Full cover
        if cover['image_url']:
            full_path = os.path.join(full_dir, fname)
            current_full_filenames.add(fname)
            if should_download(cover['image_url'], full_path):
                try:
                    r = requests.get(proxied_url(cover['image_url']))
                    r.raise_for_status()
                    with open(full_path, "wb") as f:
                        f.write(r.content)
                    print(f"  • [FULL] {full_path} (downloaded)")
                except Exception as e:
                    print(f"  ! Error downloading {cover['image_url']}: {e}")
            else:
                print(f"  • [FULL] {full_path} (skipped)")

        # Thumbnail
        if cover['thumb_url']:
            thumb_path = os.path.join(thumb_dir, fname)
            current_thumb_filenames.add(fname)
            if should_download(cover['thumb_url'], thumb_path):
                try:
                    r = requests.get(proxied_url(cover['thumb_url']))
                    r.raise_for_status()
                    with open(thumb_path, "wb") as f:
                        f.write(r.content)
                    print(f"  • [THUMB] {thumb_path} (downloaded)")
                except Exception as e:
                    print(f"  ! Error downloading {cover['thumb_url']}: {e}")
            else:
                print(f"  • [THUMB] {thumb_path} (skipped)")

    # Delete outdated images (covers)
    for fname in os.listdir(full_dir):
        if fname.endswith('.jpg') and fname not in current_full_filenames:
            try:
                os.remove(os.path.join(full_dir, fname))
                print(f"  - [FULL] {os.path.join(full_dir, fname)} (deleted outdated)")
            except Exception as e:
                print(f"  ! Error deleting {os.path.join(full_dir, fname)}: {e}")

    # Delete outdated images (thumbnails)
    for fname in os.listdir(thumb_dir):
        if fname.endswith('.jpg') and fname not in current_thumb_filenames:
            try:
                os.remove(os.path.join(thumb_dir, fname))
                print(f"  - [THUMB] {os.path.join(thumb_dir, fname)} (deleted outdated)")
            except Exception as e:
                print(f"  ! Error deleting {os.path.join(thumb_dir, fname)}: {e}")

def main():
    print("Collecting covers and thumbnails...\n")
    for category, url in CATEGORIES.items():
        print(f"Category: {category}")
        covers = fetch_covers(category, url)
        if not covers:
            print("  No covers found.")
            continue
        print(f"  {len(covers)} covers found.")
        download_images(covers, category)
        print("")

if __name__ == "__main__":
    main()
