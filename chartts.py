import time
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import requests

START_BLOCK = 25571124
END_BLOCK = 25931124
BLOCK_TIME = 6
API_URL = "https://lcd.terra-classic.hexxagon.io/cosmos/bank/v1beta1/supply/by_denom?denom=uluna"
OUTPUT_FILE = "lunc_supply.csv"


total_seconds = (END_BLOCK - START_BLOCK) * BLOCK_TIME
num_days = total_seconds / 86400
blocks_per_day = int((86400 / BLOCK_TIME))

print(
    f"Collecting approximately {int(num_days)} days of data (~{blocks_per_day} blocks per day)."
)

data = []
current_block = START_BLOCK
current_date = datetime(2025, 10, 17)

while current_block <= END_BLOCK:
    url = f"{API_URL}&height={current_block}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        result = r.json()

        amount_uluna = float(result["amount"]["amount"])
        amount_lunc = amount_uluna / 1_000_000

        data.append(
            {
                "date": current_date.strftime("%Y-%m-%d"),
                "block": current_block,
                "supply_LUNC": amount_lunc,
            }
        )

        print(
            f"{current_date.strftime('%Y-%m-%d')} | Block {current_block} | {amount_lunc:,.0f} LUNC"
        )

    except Exception as e:
        print(f"Error at block {current_block}: {e}")

    current_block += blocks_per_day
    current_date += timedelta(days=1)
    time.sleep(0.5)


df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved {len(df)} records to {OUTPUT_FILE}")


plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["supply_LUNC"], marker="o", linestyle="-", linewidth=2)
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Total Supply (LUNC)")
plt.title("LUNC Total Supply Over Time (17 Oct 2025 – Present)")


plt.ylim(df["supply_LUNC"].min() * 0.999, df["supply_LUNC"].max() * 1.001)

plt.tight_layout()
plt.show()
