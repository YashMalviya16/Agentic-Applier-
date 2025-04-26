# LinkedIn Auto-Applicator

An automated tool for applying to LinkedIn jobs based on your resume and preferences.

## Features

- Resume parsing and keyword extraction
- LinkedIn job scraping with fit score calculation
- Automated application for "Easy Apply" jobs
- Streamlit dashboard for monitoring applications

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Set up environment variables:
Create a `.env` file with your LinkedIn credentials:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

3. Run the application:
```bash
streamlit run core.py
```

## Usage

1. Upload your resume (PDF format)
2. Enter your LinkedIn credentials
3. Set your preferred job location
4. Click "Start Applying" to begin the automation

## Ethical Considerations

- Use this tool responsibly and in accordance with LinkedIn's Terms of Service
- Limit applications to avoid account flags
- Respect rate limits and add appropriate delays between actions

## Disclaimer

This tool is for educational purposes only. Use at your own risk and in accordance with LinkedIn's terms of service. 