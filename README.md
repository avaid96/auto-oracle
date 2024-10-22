# Auto Oracle

Auto Oracle is a Python application designed to process a questionnaire document and query a knowledge base to generate answers. The application outputs the results in a CSV file, making it easy to review and analyze the responses.

## Features

- Parses a questionnaire document in `.docx` format to extract questions.
- Queries a specified knowledge base API to retrieve answers for each question.
- Outputs the questions and their corresponding answers to a CSV file.
- Automatically opens the generated CSV file after processing.


## Requirements

- Python 3.x
- Required libraries listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd auto-oracle
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application from the command line with the following syntax:

```python3 auto_oracle.py --questionnaire path/to/questionnaire.docx --chatbot_link <knowledge_base_api_link>```


Replace `path/to/questionnaire.docx` with the path to your questionnaire document and `<knowledge_base_api_link>` with the link to your chatbot  API. You can use `https://aihub.instabase.com/hub/apps/187900cc-8937-4fd5-9209-528879f51aa0` (replace with latest version by visiting link) to query the AI Hub docs chatbot.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## Environment Variables

Before running the application, you need to specify the following environment variables in a `.env` file:

```
API_KEY = "<your_api_key>"
IB-CONTEXT = "<your_ib_context>"
```

Replace `<your_api_key>` with your actual AI Hub API key and `<your_ib_context>` with the appropriate context value.

## Debugging

#### 1. **SSL Certificate Verification Error**

**Error:**
```
SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

**Solution:**
- Install or update `certifi` to provide the CA bundle:
  ```bash
  pip install certifi
  export SSL_CERT_FILE=$(python -m certifi)
  ```
- (macOS) Run the `Install Certificates.command`:
  ```bash
  open /Applications/Python\ 3.11/Install\ Certificates.command
  ```

#### 2. **Incorrect Python Version**

**Error:**
Mismatched Python versions during execution.

**Solution:**
- Ensure the correct Python version (e.g., `3.11.x`) is used:
  ```bash
  python3 --version
  ```
- Activate your virtual environment:
  ```bash
  source venv/bin/activate
  ```

#### 3. **Missing Environment Variables (.env)**

**Error:**
Missing or invalid environment variables causing failures.

**Solution:**
- Ensure a `.env` file exists with the necessary variables.
- Load environment variables using `python-dotenv`:
  ```bash
  pip install python-dotenv
  ```

#### 4. **AI Hub API Connection Issues**

**Error:**
Connection to AI Hub API fails.

**Solution:**
- Verify the chatbot link and ensure the API is accessible.
- Check for SSL certificate issues and resolve them using `certifi` or other debugging steps listed above.

---

These steps should help streamline debugging common issues for your project!