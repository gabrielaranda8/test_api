import os

# -----------> API Settings <-----------
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))

api_name = os.environ.get("APP_NAME", "api_challenge")
app_domain = os.environ.get("APP_DOMAIN", "api-challenge")

# -----------> DB Settings <-----------

# -----------> Collection names <-----------