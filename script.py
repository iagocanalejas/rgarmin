import argparse
import logging
import os
from datetime import date

from rgarmin.client import GarminClient

# ruff: noqa
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main():
    g = GarminClient()
    # print(g.activity_types)
    # print(g.get_activities())
    # print(g.get_activity("18559183407"))  # bici
    # print(g.get_activity("18558812362"))  # pesas
    # print(g.get_activity("18546988821"))  # entreno mar
    # print(g.get_activity("18541384983"))  # regate
    # print(g.get_activity("18430213741"))  # ergometro
    # print(g.get_connections())
    # print(g.get_connection("Adrienone"))
    # print(g.get_connection_activities("Adrienone"))
    # print(g.get_activities_by_date(date(2025, 3, 23), date(2025, 3, 17)))
    print(
        g.get_connection_activities_by_date(
            "4fa4829e-1a24-4ead-be2b-2e79869d0444", date(2025, 3, 23), date(2025, 3, 17)
        )
    )


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main()
