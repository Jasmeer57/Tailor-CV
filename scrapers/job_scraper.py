"""
Job Scraper Module
Scrapes job postings from various job boards (LinkedIn, Indeed, StepStone)
"""

import re
import time
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class JobScraper:
    """Scrapes job postings from various job sites"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def scrape_job(self, url: str) -> Optional[Dict]:
        """
        Main method to scrape job posting based on URL

        Args:
            url: Job posting URL

        Returns:
            Dictionary containing job information
        """
        domain = urlparse(url).netloc

        try:
            if 'linkedin.com' in domain:
                return self._scrape_linkedin(url)
            elif 'indeed.com' in domain or 'indeed.de' in domain:
                return self._scrape_indeed(url)
            elif 'stepstone' in domain:
                return self._scrape_stepstone(url)
            else:
                # Generic scraper for unknown sites
                return self._scrape_generic(url)
        except Exception as e:
            print(f"Error scraping job: {e}")
            return None

    def _scrape_linkedin(self, url: str) -> Optional[Dict]:
        """Scrape LinkedIn job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract job title
            title_elem = soup.find('h1', class_='top-card-layout__title') or soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Not found"

            # Extract company
            company_elem = soup.find('a', class_='topcard__org-name-link') or soup.find('span', class_='topcard__flavor')
            company = company_elem.text.strip() if company_elem else "Not found"

            # Extract location
            location_elem = soup.find('span', class_='topcard__flavor--bullet')
            location = location_elem.text.strip() if location_elem else "Not specified"

            # Extract job description
            desc_elem = soup.find('div', class_='description__text') or soup.find('div', class_='show-more-less-html__markup')
            description = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'source': 'LinkedIn'
            }
        except Exception as e:
            print(f"LinkedIn scraping error: {e}")
            return self._scrape_with_selenium(url)

    def _scrape_indeed(self, url: str) -> Optional[Dict]:
        """Scrape Indeed job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1', class_='jobsearch-JobInfoHeader-title')
            title = title_elem.text.strip() if title_elem else "Not found"

            # Extract company
            company_elem = soup.find('div', {'data-company-name': True})
            company = company_elem.text.strip() if company_elem else "Not found"

            # Extract location
            location_elem = soup.find('div', {'data-testid': 'job-location'})
            location = location_elem.text.strip() if location_elem else "Not specified"

            # Extract description
            desc_elem = soup.find('div', id='jobDescriptionText')
            description = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'source': 'Indeed'
            }
        except Exception as e:
            print(f"Indeed scraping error: {e}")
            return self._scrape_with_selenium(url)

    def _scrape_stepstone(self, url: str) -> Optional[Dict]:
        """Scrape StepStone job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1', {'data-at': 'header-job-title'})
            title = title_elem.text.strip() if title_elem else "Not found"

            # Extract company
            company_elem = soup.find('span', {'data-at': 'header-company-name'})
            company = company_elem.text.strip() if company_elem else "Not found"

            # Extract location
            location_elem = soup.find('span', {'data-at': 'job-location'})
            location = location_elem.text.strip() if location_elem else "Not specified"

            # Extract description
            desc_elem = soup.find('div', {'data-at': 'jobdescription-content'})
            description = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ""

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'source': 'StepStone'
            }
        except Exception as e:
            print(f"StepStone scraping error: {e}")
            return self._scrape_with_selenium(url)

    def _scrape_generic(self, url: str) -> Optional[Dict]:
        """Generic scraper for unknown job sites"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to find title (h1 is common)
            title = soup.find('h1')
            title = title.text.strip() if title else "Job Title"

            # Get all text content
            body_text = soup.get_text(separator='\n', strip=True)

            return {
                'title': title,
                'company': "Not specified",
                'location': "Not specified",
                'description': body_text[:2000],  # Limit to 2000 chars
                'url': url,
                'source': 'Generic'
            }
        except Exception as e:
            print(f"Generic scraping error: {e}")
            return None

    def _scrape_with_selenium(self, url: str) -> Optional[Dict]:
        """Fallback scraper using Selenium for JavaScript-heavy sites"""
        try:
            # Setup headless Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.get(url)
            time.sleep(3)  # Wait for page to load

            # Get page content
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract basic info
            title = soup.find('h1')
            title = title.text.strip() if title else "Job Title"

            body_text = soup.get_text(separator='\n', strip=True)

            driver.quit()

            return {
                'title': title,
                'company': "Not specified",
                'location': "Not specified",
                'description': body_text[:2000],
                'url': url,
                'source': 'Selenium'
            }
        except Exception as e:
            print(f"Selenium scraping error: {e}")
            return None


if __name__ == "__main__":
    # Test the scraper
    scraper = JobScraper()
    test_url = "https://www.linkedin.com/jobs/view/example"
    result = scraper.scrape_job(test_url)
    print(result)
