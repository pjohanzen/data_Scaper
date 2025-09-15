import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin, urlparse
import time
import re

BASE_URL = "https://hiring.cafe/"

def setup_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "ashbyhq.com", "myworkdayjobs.com", "workday.com",
    "smartrecruiters.com", "bamboohr.com", "workable.com", "recruitee.com", "icims.com",
    "jobvite.com", "adp.com", "eightfold.ai", "oraclecloud.com", "successfactors.com",
    "ukg.com", "rippling-ats", "paylocity.com", "gusto.com", "careers"
]
JOB_PATH_HINTS = ["/job", "/jobs", "/career", "/careers", "/opening", "/openings", "/position", "/positions", "/vacanc", "/opportunit"]
EXCLUDE_SCHEMES = ("mailto:", "tel:", "javascript:", "#")

BANNED_TITLE_PHRASES = {
    "view all", "join our community", "learn more", "read more", "hiringcafe",
    "departments", "salary", "privacy", "terms", "about", "contact",
    "login", "sign in", "sign up", "home", "explore jobs", "all jobs", "show more"
}
ROLE_HINTS = [
    "engineer", "developer", "manager", "designer", "analyst", "scientist",
    "coordinator", "specialist", "director", "lead", "architect", "marketer",
    "writer", "editor", "sales", "support", "administrator", "operator",
    "technician", "consultant", "product", "project", "qa", "intern"
]

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def is_banned_title(text: str) -> bool:
    t = text.lower().strip()
    return any(b in t for b in BANNED_TITLE_PHRASES) or len(t) < 4

def looks_like_role(text: str) -> bool:
    t = text.lower().strip()
    if not (8 <= len(t) <= 100):
        return False
    if is_banned_title(t):
        return False
    if any(h in t for h in ROLE_HINTS):
        return True
    words = text.split()
    cap_words = sum(1 for w in words if w[:1].isupper())
    return cap_words >= max(2, len(words) // 2)

def href_score(href: str, anchor_text: str) -> int:
    if not href:
        return -999
    h = href.lower()
    if h.startswith(EXCLUDE_SCHEMES):
        return -999
    score = 0
    netloc = urlparse(href).netloc.lower().replace("www.", "")
    base = urlparse(BASE_URL).netloc.lower().replace("www.", "")
    if netloc and netloc != base:
        score += 3
    if any(dom in netloc for dom in ATS_DOMAINS):
        score += 5
    if any(hint in h for hint in JOB_PATH_HINTS):
        score += 3
    txt = normalize_space(anchor_text or "")
    if looks_like_role(txt):
        score += 3
    if is_banned_title(txt):
        score -= 5
    if any(dom in netloc for dom in ["reddit.com","twitter.com","x.com","facebook.com","instagram.com","youtube.com","t.me","discord.gg","medium.com"]):
        score -= 6
    return score

def biggest_salary(text: str) -> str:
    text = text.replace("\u00a0", " ")
    nums = []
    for m in re.finditer(r"\$?\s*([\d]{2,3}(?:,\d{3})+|\d{4,6})(?:\s*-\s*\$?\s*([\d]{2,3}(?:,\d{3})+|\d{4,6}))?", text):
        a = int(re.sub(r"[^\d]", "", m.group(1)))
        b = int(re.sub(r"[^\d]", "", m.group(2))) if m.group(2) else None
        nums.append(max(a,b) if b else a)
    for m in re.finditer(r"(\d{2,3})\s*[kK]", text):
        nums.append(int(m.group(1)) * 1000)
    if not nums:
        return ""
    val = max(nums)
    if val < 500:
        return ""
    return "${:,}".format(val)

def detect_workplace(text: str):
    t = text.lower()
    remote, wtype = "no", "in-office"
    if any(k in t for k in ["hybrid", "remote-friendly", "remote optional", "part remote", "flexible"]):
        remote, wtype = "yes", "hybrid"
    if any(k in t for k in ["remote", "work from home", "wfh", "anywhere"]):
        remote, wtype = "yes", "remote"
    return remote, wtype

def search_jobs_on_site(driver, job_title: str, location: str = ""):
    driver.get(BASE_URL)
    time.sleep(4)
    selectors = [
        "input[type='search']",
        "input[placeholder*='search' i]",
        "input[placeholder*='job' i]",
        "input[name*='search' i]",
        "input[id*='search' i]",
        ".search-input",
        "[data-testid*='search']"
    ]
    box = None
    for css in selectors:
        try:
            box = driver.find_element(By.CSS_SELECTOR, css)
            break
        except:
            continue
    if box:
        box.clear()
        box.send_keys(job_title)
        box.send_keys(Keys.ENTER)
        time.sleep(4)
    if location:
        for css in ["input[placeholder*='location' i]","input[name*='location' i]","[data-testid*='location']"]:
            try:
                loc = driver.find_element(By.CSS_SELECTOR, css)
                loc.clear()
                loc.send_keys(location)
                loc.send_keys(Keys.ENTER)
                time.sleep(2)
                break
            except:
                continue

def auto_scroll(driver, pause=1.5, max_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def best_title_from_card(card) -> str:
    for tag in ["h1","h2","h3","h4","h5","h6","strong"]:
        try:
            el = card.find_element(By.TAG_NAME, tag)
            t = normalize_space(el.text)
            if looks_like_role(t):
                return t
        except:
            pass
    try:
        lines = [normalize_space(x) for x in card.text.split("\n") if normalize_space(x)]
        for line in lines[:6]:
            if looks_like_role(line):
                return line
    except:
        pass
    return ""

def title_from_job_page(driver) -> str:
    for tag in ["h1","h2","h3"]:
        try:
            t = normalize_space(driver.find_element(By.TAG_NAME, tag).text)
            if looks_like_role(t):
                return t
        except:
            continue
    try:
        t = normalize_space(driver.title or "")
        for sep in [" - ", " | ", " – "]:
            if sep in t and len(t.split(sep)[0]) >= 8:
                return t.split(sep)[0].strip()
        return t
    except:
        return ""

def anchors_in_card(card):
    try:
        return card.find_elements(By.TAG_NAME, "a")
    except:
        return []

def choose_best_anchor(card):
    best = None
    best_s = -999
    for a in anchors_in_card(card):
        try:
            href = a.get_attribute("href") or ""
            txt  = normalize_space(a.text or a.get_attribute("aria-label") or a.get_attribute("title") or "")
            s = href_score(href, txt)
            if s > best_s:
                best, best_s = (a, href, txt), s
        except:
            continue
    return best

def collect_jobs_on_page(driver, max_jobs=50):
    jobs, seen = [], set()
    cards = driver.find_elements(By.CSS_SELECTOR, "div, li, article")

    for card in cards:
        if len(jobs) >= max_jobs:
            break
        try:
            card_text = normalize_space(card.text)
            if len(card_text) < 30:
                continue

            choice = choose_best_anchor(card)
            if not choice:
                continue
            a_el, href, a_text = choice
            if not href or any(href.lower().startswith(s) for s in EXCLUDE_SCHEMES):
                continue

            url = urljoin(BASE_URL, href)
            if url in seen:
                continue
            seen.add(url)

            title = best_title_from_card(card)
            if not title or is_banned_title(title):
                if looks_like_role(a_text):
                    title = a_text
                else:
                    for ln in card_text.split("\n"):
                        ln = normalize_space(ln)
                        if looks_like_role(ln):
                            title = ln
                            break
            if not title or is_banned_title(title):
                title = ""

            company = ""
            lines = [normalize_space(x) for x in card_text.split("\n") if normalize_space(x)]
            if lines:
                for ln in lines[:8]:
                    if ln != title and 2 < len(ln) < 60 and not re.search(r"\d", ln):
                        if not is_banned_title(ln):
                            company = ln
                            break

            salary = biggest_salary(card_text)
            remote, wtype = detect_workplace(card_text)

            full_text = ""
            try:
                driver.execute_script("window.open(arguments[0], '_blank');", url)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)
                full_text = normalize_space(driver.find_element(By.TAG_NAME, "body").text)
                page_title = title_from_job_page(driver)
                if page_title and not is_banned_title(page_title):
                    title = page_title
                if not salary:
                    salary = biggest_salary(full_text)
                if not company:
                    for ln in full_text.split("\n")[:30]:
                        ln = normalize_space(ln)
                        if 2 < len(ln) < 60 and not re.search(r"\d", ln) and not is_banned_title(ln):
                            company = ln
                            break
            except:
                pass
            finally:
                try:
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                except:
                    pass

            if not title or is_banned_title(title):
                continue

            jobs.append({
                "url": url,
                "job title": title,
                "company": company,
                "salary": salary,
                "remote": remote,
                "workplace_type": wtype
            })

        except:
            continue

    return jobs

def run(job_title: str, location: str, max_jobs: int, filename: str,
        scroll_pause=1.5, max_scrolls=10):
    driver = setup_driver()
    try:
        search_jobs_on_site(driver, job_title, location)
        auto_scroll(driver, pause=scroll_pause, max_scrolls=max_scrolls)
        data = collect_jobs_on_page(driver, max_jobs=max_jobs)
    finally:
        try:
            driver.quit()
        except:
            pass

    if not data:
        print("No jobs captured. Try different keywords or increase max_scrolls.")
        return

    df = pd.DataFrame(data, columns=["url", "job title", "company", "salary", "remote", "workplace_type"])
    df = df.drop_duplicates(subset=["url"])
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Saved {len(df)} rows to {filename}")

if __name__ == "__main__":
    print("HIRING.CAFE SCRAPER (URL/Title/Company/Salary/Remote/Workplace)")
    job_title = input("Enter job title/keywords: ").strip() or "python developer"
    location = input("Enter location (blank for any): ").strip()
    try:
        max_jobs = int(input("Max jobs (default 50): ").strip() or "50")
    except:
        max_jobs = 50
    filename = input("CSV filename (default jobs_results.csv): ").strip() or "jobs_results.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"

    run(job_title, location, max_jobs, filename, scroll_pause=1.5, max_scrolls=10)
