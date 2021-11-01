mkdir -p ~/.streamlit/
echo "\
[theme]\n\
primaryColor=\"#f9d793\"\n\
backgroundColor=\"#282a36\"\n\
secondaryBackgroundColor=\"#44475a\"\n\
textColor=\"#f8f8f2\"\n\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml