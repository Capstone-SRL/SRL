mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"yixliu1@student.unimelb.edu.au\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
