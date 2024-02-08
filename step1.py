# from https://stackoverflow.com/a/72241008/1623645

import time

import selenium.webdriver
from bs4 import BeautifulSoup

driver = selenium.webdriver.Chrome()

output = open("numba-dependents.txt", "w")

repo = "numba/numba"
url = 'https://github.com/{}/network/dependents?dependents_after=MjgxMjEwMDkxMzU'.format(repo)
nextExists = True
total = 0
while nextExists:
    print(f"{time.strftime('%H:%M:%S')}: get {url}")
    driver.get(url)
    while (
        "exceeded a secondary rate limit" in driver.page_source
        or "dependents are currently unavailable" in driver.page_source
    ):
        print(f"{time.strftime('%H:%M:%S')}: wait 1 minute...")
        time.sleep(60)
        driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    batch = [
        "{}/{}".format(
            t.find('a', {"data-repository-hovercards-enabled":""}).text,
            t.find('a', {"data-hovercard-type":"repository"}).text
        )
        for t in soup.findAll("div", {"class": "Box-row"})
    ]
    total += len(batch)
    print(f"{time.strftime('%H:%M:%S')}: found {len(batch)} (running total: {total})")
    output.write("\n".join(batch))
    output.write("\n")
    output.flush()
    nextExists = False
    for u in soup.find("div", {"class":"paginate-container"}).findAll('a'):
        if u.text == "Next":
            nextExists = True
            url = u["href"]
    time.sleep(1)

print("{time.strftime('%H:%M:%S')}: DONE")
