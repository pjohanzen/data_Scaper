

````markdown
# HiringCafe Job Scraper (v0)

This project is a **web scraper** built with Python and Selenium that extracts job listings from [HiringCafe](https://hiring.cafe).  
It collects job details such as:

- Job URL  
- Job Title  
- Company  
- Salary  
- Remote status  
- Workplace type (remote, hybrid, in-office)

The results are saved into a CSV file for further use.

⚠️ **Note:** This is **version 0 (v0)** of the scraper.  
It is still experimental and may have **minor bugs** (e.g., missed job titles or mismatched companies), but these are fixable in later stages with improved parsing rules and error handling.

---

## Features
- Automates Chrome browser with **Selenium**.  
- Scrolls the job listings page to load more results automatically.  
- Opens each job posting to capture **full job details** (titles, salaries, companies).  
- Filters out junk titles like *"View all"* or *"Join our community"*.  
- Outputs clean, structured CSV data ready for analysis.  

---

## Requirements

You’ll need:

- Python **3.8+**
- Google Chrome installed

### Install Dependencies

It’s recommended to use a **virtual environment**:

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate   # On Mac/Linux
````

Then install the required packages:

```bash
pip install pandas selenium webdriver-manager
```

⚠️ If you see errors related to **numpy/pandas**, fix them with:

```bash
pip install --upgrade pip setuptools wheel
pip install --force-reinstall numpy pandas
```

---

## Usage

Run the script from your terminal:

```bash
python scraper.py
```

You’ll be prompted for:

1. **Job title or keywords**
2. **Location** (leave blank for any)
3. **Max number of jobs** to scrape
4. **Output CSV filename**

Example:

```text
HIRING.CAFE SCRAPER (URL/Title/Company/Salary/Remote/Workplace)
Enter job title/keywords: marketing director
Enter location (blank for any): New York
Max jobs (default 50): 100
CSV filename (default jobs_results.csv): jobs.csv
```

The scraper will:

1. Scroll through job listings
2. Open job detail pages
3. Extract the information
4. Save results to your chosen CSV file

---

## Output Format

The CSV file will contain these columns:

| Column           | Description                                   |
| ---------------- | --------------------------------------------- |
| `url`            | Direct link to the job posting                |
| `job title`      | Title of the job (e.g., “Marketing Director”) |
| `company`        | Company offering the job                      |
| `salary`         | Extracted salary (if available)               |
| `remote`         | `yes` or `no`                                 |
| `workplace_type` | `remote`, `hybrid`, or `in-office`            |

---

## Example Row

```csv
url,job title,company,salary,remote,workplace_type
https://hiring.cafe/jobs/12345,Senior Marketing Director,Viatris,"$151,000-$314,000",yes,remote
```

---

## Notes

* This scraper is **v0**: it works, but may skip or mislabel some jobs.
* Improvements (planned for future versions):

  * More robust job title extraction.
  * Better company parsing.
  * Handling of edge cases for salaries.
* If some jobs aren’t being captured, try:

  * Increasing the scroll limit (`max_scrolls` in the code).
  * Using different keywords.
  * Running the script with a higher max jobs setting.

---
