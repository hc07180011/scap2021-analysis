# 2021 Fugle <> SCAP Data Analysis

## Streamlit 

1. Configuration:
    + you should create a new file named `.streamlit/secrets.toml`
    + set `public_gsheets_url = "URL"` (now using `public_data` in our shared folder under `Projects/問卷資料/data`)
    + set the constant variable `DEPLOY_TO_HEROKU = False` in `app.py`
2. Run:
    ```sh
    pip install -r requirements.txt
    streamlit run app.py
    ```
