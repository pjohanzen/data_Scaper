#Data Scraper

````markdown
# HiringCafe Job Scraper

This project is a **web scraper** built with Python and Selenium that extracts job listings from [HiringCafe](https://hiring.cafe).  
It collects job details such as:

- Job URL  
- Job Title  
- Company  
- Salary  
- Remote status  
- Workplace type (remote, hybrid, in-office)

The results are saved to a CSV file.

---

## Features
- Uses **Selenium** to automate Chrome browser.
- Automatically scrolls the page to load more jobs.
- Clicks job postings to capture full job details.
- Cleans and filters job titles to avoid junk values like "View all".
- Outputs structured CSV data ready for analysis.

---

## Requirements

You need Python **3.8+** installed.

### Install Dependencies
Create a virtual environment (recommended) and install the required packages:

```bash
pip install pandas selenium
````

For Selenium to work, you also need **Google Chrome** and a **matching ChromeDriver** installed.
You can manage this with `webdriver-manager`:

```bash
pip install webdriver-manager
```

---

## Usage

Run the script in your terminal:

```bash
python scraper.py
```

You’ll be prompted for:

1. Job title or keywords
2. Location (optional)
3. Max number of jobs to scrape
4. Output CSV filename

Example:

```text
HIRING.CAFE SCRAPER (URL/Title/Company/Salary/Remote/Workplace)
Enter job title/keywords: marketing director
Enter location (blank for any): New York
Max jobs (default 50): 100
CSV filename (default jobs_results.csv): jobs.csv
```

The scraper will run, scroll through job listings, open job detail pages, and save results to `jobs.csv`.

---

## Output

The CSV file will contain the following columns:

* **url**: Direct link to the job posting
* **job title**: Title of the job (e.g., “Marketing Director”)
* **company**: Company offering the job
* **salary**: Extracted salary range if available
* **remote**: `yes` or `no`
* **workplace\_type**: `remote`, `hybrid`, or `in-office`

---

## Example Row

```csv
url,job title,company,salary,remote,workplace_type
https://hiring.cafe/jobs/12345,Senior Marketing Director,Viatris,"$151,000-$314,000",yes,remote
```

---

## Notes

* The scraper uses **heuristics** to detect job titles, salaries, and company names.
* If some jobs aren’t captured, try:

  * Increasing the scroll limit (`max_scrolls` in code).
  * Using different keywords.
  * Running the script with more max jobs.

---
