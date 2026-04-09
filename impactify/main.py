# main.py
from dotenv import load_dotenv
load_dotenv()  # This looks for the .env file and loads the keys
from ui.cli_app import ImpactifyCliApp


def main():
    app = ImpactifyCliApp()
    app.run()


if __name__ == "__main__":
    main()
