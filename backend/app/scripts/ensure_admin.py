import logging

from app.core.admin import create_default_admin_if_missing


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    create_default_admin_if_missing()


if __name__ == "__main__":
    main()
