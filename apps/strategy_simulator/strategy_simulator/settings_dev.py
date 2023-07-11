from strategy_simulator.settings_base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# To loading Django modules in Jupter. Not recomended for production
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

NOTEBOOK_ARGUMENTS = [
    "--ip",
    os.environ.get("JUPYTER_HOST"),
    "--port",
    os.environ.get("JUPYTER_PORT"),
    "--allow-root",
    "--no-browser",
]