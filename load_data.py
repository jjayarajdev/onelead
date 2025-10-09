"""Main script to load data into OneLead database."""

from src.etl.loader import DataLoader

if __name__ == "__main__":
    print("=" * 60)
    print("OneLead Data Loader")
    print("=" * 60)
    print()

    loader = DataLoader()
    loader.load_all()

    print()
    print("=" * 60)
    print("Data loading complete!")
    print("=" * 60)
