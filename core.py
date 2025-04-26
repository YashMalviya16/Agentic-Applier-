import os
import time
import random
import pdfplumber
import spacy
import streamlit as st
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import json
from datetime import datetime
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# Load environment variables
load_dotenv()

# Constants
MAX_APPLICATIONS_PER_DAY = 10
MIN_DELAY = 2
MAX_DELAY = 5
RESUME_PATH = "Yash Malviya 2025 Apr Resume.pdf"

class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.skills = [
            "Python", "PyTorch", "AWS", "GANs", "Diffusion Models",
            "MLOps", "Kubernetes", "Docker", "CI/CD", "Snowflake"
        ]
        self.certifications = ["NVIDIA RAG", "AWS ML"]
        self.achievements = [
            "25K revenue boost", "99.89% error reduction",
            "10M+ synthetic records"
        ]

    def parse_resume(self):
        try:
            with pdfplumber.open(RESUME_PATH) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages])
            
            doc = self.nlp(text)
            
            # Extract entities and keywords
            extracted_skills = []
            for skill in self.skills:
                if skill.lower() in text.lower():
                    extracted_skills.append(skill)
            
            extracted_certs = []
            for cert in self.certifications:
                if cert.lower() in text.lower():
                    extracted_certs.append(cert)
            
            extracted_achievements = []
            for achievement in self.achievements:
                if achievement.lower() in text.lower():
                    extracted_achievements.append(achievement)
            
            return {
                "skills": extracted_skills,
                "certifications": extracted_certs,
                "achievements": extracted_achievements,
                "raw_text": text
            }
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            return None

class LinkedInBot:
    def __init__(self):
        self.driver = None
        self.applications_today = 0
        self.applied_jobs = []

    def setup_driver(self):
        try:
            chrome_options = uc.ChromeOptions()
            # chrome_options.add_argument("--headless")  # Enable if you want headless
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            # chrome_options.add_argument("--user-data-dir=C:/temp/chrome-profile")
            self.driver = uc.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            st.error(f"Error setting up undetected Chrome driver: {str(e)}")
            return False

    def login(self, email, password):
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            
            self.driver.find_element(By.ID, "username").send_keys(email)
            self.driver.find_element(By.ID, "password").send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, ".btn__primary--large").click()
            
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            return True
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False

    def calculate_fit_score(self, job_description, resume_data):
        score = 0
        total_keywords = len(resume_data["skills"]) + len(resume_data["certifications"]) + len(resume_data["achievements"])
        
        for skill in resume_data["skills"]:
            if skill.lower() in job_description.lower():
                score += 1
        
        for cert in resume_data["certifications"]:
            if cert.lower() in job_description.lower():
                score += 1
        
        for achievement in resume_data["achievements"]:
            if achievement.lower() in job_description.lower():
                score += 1
        
        return (score / total_keywords) * 100 if total_keywords > 0 else 0

    def apply_to_jobs(self, keywords, location, resume_data):
        if self.applications_today >= MAX_APPLICATIONS_PER_DAY:
            st.warning("Daily application limit reached. Please try again tomorrow.")
            return
        try:
            page = 1
            while self.applications_today < MAX_APPLICATIONS_PER_DAY:
                st.info(f"Navigating to LinkedIn Jobs page {page}...")
                # Add f_TPR=r86400 for jobs posted in last 24 hours
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true&f_TPR=r86400&start={(page-1)*25}"
                self.driver.get(search_url)
                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                try:
                    st.info("Waiting for Easy Apply job listings to load (scrolling page)...")
                    for _ in range(5):
                        self.driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)
                    st.info("Trying multiple selectors for job cards...")
                    job_list_selectors = [
                        ".jobs-search-results__list-item",
                        ".job-card-container",
                        ".base-card"
                    ]
                    jobs = []
                    for selector in job_list_selectors:
                        jobs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if jobs:
                            st.info(f"Found {len(jobs)} jobs with selector {selector}")
                            break
                    if not jobs:
                        st.error("No job cards found with any known selector. Printing page source for debugging.")
                        st.text(self.driver.page_source[:2000])
                        break
                except Exception as e:
                    st.error(f"Error waiting for job listings: {repr(e)}")
                    break

                for idx, job in enumerate(jobs):
                    if self.applications_today >= MAX_APPLICATIONS_PER_DAY:
                        break
                    start_time = time.time()
                    try:
                        st.info(f"Processing job card {idx} on page {page}...")
                        self.driver.execute_script("arguments[0].scrollIntoView();", job)
                        time.sleep(1)
                        try:
                            job.click()
                            st.info(f"Clicked job card {idx}.")
                        except ElementClickInterceptedException:
                            st.warning(f"Job card {idx} not clickable, retrying after scroll...")
                            self.driver.execute_script("window.scrollBy(0, 200);")
                            time.sleep(1)
                            job.click()
                        except StaleElementReferenceException:
                            st.warning(f"Job card {idx} became stale, skipping...")
                            continue

                        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                        try:
                            st.info(f"Waiting for job description for card {idx}...")
                            WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-description__content"))
                            )
                            st.info(f"Job description loaded for card {idx}.")
                        except Exception as e:
                            st.warning(f"Error waiting for job description for card {idx}: {repr(e)}")
                            continue

                        easy_apply_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.jobs-apply-button")
                        if not easy_apply_buttons:
                            st.info(f"No Easy Apply button found for job card {idx}. Skipping...")
                            continue

                        try:
                            job_description = self.driver.find_element(By.CSS_SELECTOR, ".jobs-description__content").text
                            st.info(f"Fetched job description for card {idx}.")
                        except Exception as e:
                            st.warning(f"Error fetching job description for card {idx}: {repr(e)}")
                            continue

                        fit_score = self.calculate_fit_score(job_description, resume_data)
                        st.info(f"Fit score for card {idx}: {fit_score:.2f}%")

                        if fit_score >= 0:
                            st.info(f"Attempting Easy Apply for card {idx}...")
                            if self._submit_application():
                                self.applications_today += 1
                                try:
                                    job_title = job.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                                    company_name = job.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                                except Exception as e:
                                    job_title = "Unknown"
                                    company_name = "Unknown"
                                    st.warning(f"Error fetching job/company name for card {idx}: {repr(e)}")
                                self.applied_jobs.append({
                                    "title": job_title,
                                    "company": company_name,
                                    "fit_score": fit_score,
                                    "applied_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.success(f"✅ Successfully applied to {job_title} at {company_name}")
                                self._save_application_history()
                            else:
                                st.warning(f"Failed to submit application for card {idx}. Moving to next job...")
                        else:
                            st.info(f"Fit score {fit_score:.2f}% is below threshold for card {idx}. Moving to next job...")

                        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                        # Watchdog: skip job if it takes more than 10 seconds
                        if time.time() - start_time > 10:
                            st.warning(f"Job card {idx} took too long (>10s), skipping to next job...")
                            continue
                    except Exception as e:
                        st.warning(f"Error processing job {idx}: {repr(e)}")
                        continue

                # Check for next page: if less than 25 jobs, it's the last page
                if len(jobs) < 25:
                    break
                page += 1

            st.success("Finished processing all job cards on all pages.")
        except Exception as e:
            st.error(f"Error during job search: {repr(e)}")
            st.error("Please check your internet connection and try again.")

    def close_application_modal(self):
        try:
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
            if close_buttons:
                close_buttons[0].click()
                time.sleep(1)
                return True
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
            return True
        except Exception as e:
            st.warning(f"Could not close application modal: {repr(e)}")
            return False

    def _submit_application(self):
        try:
            st.info("Waiting for Easy Apply button...")
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-apply-button"))
            )
            easy_apply_button.click()
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

            while True:
                # Fill text inputs
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                for input_field in text_inputs:
                    try:
                        if not input_field.get_attribute("value"):
                            input_field.clear()
                            input_field.send_keys("5")
                    except Exception:
                        continue

                # Fill dropdowns
                selects = self.driver.find_elements(By.TAG_NAME, "select")
                for select_elem in selects:
                    try:
                        select = Select(select_elem)
                        select.select_by_index(1)
                    except Exception:
                        continue

                # Click Next or Submit
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Continue to next step'], button[aria-label='Next']")
                if next_buttons:
                    next_buttons[0].click()
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                    continue

                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Submit application'], button[aria-label='Review your application'], button[aria-label='Review']")
                if submit_buttons:
                    # Scroll modal to bottom before clicking submit
                    try:
                        modal = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-modal__content")
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                        time.sleep(1)
                    except Exception:
                        pass
                    submit_buttons[0].click()
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                    st.success("Application submitted successfully!")
                    # After submit, look for Done button
                    try:
                        done_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Done']"))
                        )
                        done_button.click()
                        time.sleep(1)
                    except Exception:
                        pass
                    return True

                # If neither Next nor Submit is found, break
                break

            st.warning("Could not find a way to submit the application. Closing modal.")
            return False
        except Exception as e:
            st.warning(f"Error submitting application: {str(e)}")
            return False
        finally:
            self.close_application_modal()

    def _save_application_history(self):
        try:
            with open("application_history.json", "w") as f:
                json.dump(self.applied_jobs, f, indent=4)
        except Exception as e:
            st.warning(f"Error saving application history: {str(e)}")

    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    st.set_page_config(page_title="LinkedIn Auto-Applicator", layout="wide")
    st.title("🔍 LinkedIn Auto-Applicator")
    
    # Initialize session state
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    if "bot" not in st.session_state:
        st.session_state.bot = None
    
    # Parse Resume
    st.header("1. Resume Analysis")
    if st.session_state.resume_data is None:
        parser = ResumeParser()
        st.session_state.resume_data = parser.parse_resume()
        
        if st.session_state.resume_data:
            st.success("✅ Resume parsed successfully!")
            st.write("Detected Skills:", ", ".join(st.session_state.resume_data["skills"]))
            st.write("Detected Certifications:", ", ".join(st.session_state.resume_data["certifications"]))
            st.write("Detected Achievements:", ", ".join(st.session_state.resume_data["achievements"]))
    
    # LinkedIn Credentials
    st.header("2. LinkedIn Credentials")
    email = st.text_input("LinkedIn Email", value=os.getenv("LINKEDIN_EMAIL", ""))
    password = st.text_input("LinkedIn Password", type="password", value=os.getenv("LINKEDIN_PASSWORD", ""))
    
    # Job Search Parameters
    st.header("3. Job Search Parameters")
    keywords = st.text_input("Job Keywords", value="Machine Learning Engineer, Data Scientist, MLOps")
    location = st.text_input("Location", value="Boston, MA")
    
    # Start Automation
    if st.button("Start Applying"):
        if not st.session_state.resume_data:
            st.error("Error parsing resume. Please check if the resume file exists.")
            return
        
        if not email or not password:
            st.error("Please enter your LinkedIn credentials!")
            return
        
        if not st.session_state.bot:
            st.session_state.bot = LinkedInBot()
            if not st.session_state.bot.setup_driver():
                st.error("Failed to initialize Chrome driver. Please check your Chrome installation.")
                return
        
        with st.spinner("Logging in to LinkedIn..."):
            if st.session_state.bot.login(email, password):
                st.success("✅ Successfully logged in!")
                
                with st.spinner("Searching and applying to jobs..."):
                    st.session_state.bot.apply_to_jobs(keywords, location, st.session_state.resume_data)
                
                # Display application history
                if st.session_state.bot.applied_jobs:
                    st.header("Application History")
                    for job in st.session_state.bot.applied_jobs:
                        st.write(f"📝 {job['title']} at {job['company']}")
                        st.write(f"Fit Score: {job['fit_score']:.2f}%")
                        st.write(f"Applied at: {job['applied_at']}")
                        st.write("---")
            else:
                st.error("❌ Login failed. Please check your credentials.")

if __name__ == "__main__":
    main() 