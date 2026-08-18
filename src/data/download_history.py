from datetime import datetime, timezone

from src.config.loader import load_settings
from src.data.downloader import HistoricalDataDownloader
from src.data.exchange import ExchangeClient


def main():

    settings = load_settings()

    exchange = ExchangeClient(
        settings["market"]["exchange"]
    )

    try:

        downloader = HistoricalDataDownloader(
            exchange=exchange,
            output_directory=settings["data"]["raw_path"],
            batch_size=settings["data"]["download"]["batch_size"],
            request_delay=settings["data"]["download"][
                "request_delay_seconds"
            ],
        )

        dataframe = downloader.download(
            symbol=settings["market"]["symbol"],
            timeframe="1m",

            # Пока скачиваем только небольшой участок
            # для проверки всей системы.
            start=datetime(
                2026,
                8,
                17,
                tzinfo=timezone.utc,
            ),

            end=datetime(
                2026,
                8,
                18,
                tzinfo=timezone.utc,
            ),
        )

        print()
        print("=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)
        print(f"Rows: {len(dataframe)}")
        print(
            f"First: {dataframe['timestamp'].iloc[0]}"
        )
        print(
            f"Last: {dataframe['timestamp'].iloc[-1]}"
        )
        print("=" * 60)

    finally:
        exchange.close()


if __name__ == "__main__":
    main()