import os
import seaborn as sns

def main():
    os.makedirs("data", exist_ok=True)
    df = sns.load_dataset("titanic")
    df.to_csv("data/titanic.csv", index=False)
    print(f"✅ Saved {len(df)} rows to data/titanic.csv")
    print(f"   Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
