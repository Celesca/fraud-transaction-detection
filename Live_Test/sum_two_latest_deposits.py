#!/usr/bin/env python3
"""
sum_two_latest_deposits.py

Find users who registered on 2023-10-01 and 2023-10-02 and compute the sum
of their two latest deposit transactions (from data2.csv).

Outputs: uid, amount

Usage:
    python sum_two_latest_deposits.py \
        --df data.csv --df2 data2.csv \
        [--out output.csv]

If --out is provided, writes CSV with columns: uid, amount
Otherwise prints the result to stdout.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


def compute_sum_two_latest_deposits(df: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    # Ensure dt columns are datetimes
    df = df.copy()
    df2 = df2.copy()
    df['dt'] = pd.to_datetime(df['dt'], errors='coerce')
    df2['dt'] = pd.to_datetime(df2['dt'], errors='coerce')

    # registration dates (dates only)
    target_dates = {pd.Timestamp('2023-10-01').date(), pd.Timestamp('2023-10-02').date()}

    # users who registered on those dates
    registered = df[(df['account_action'] == 'register') & df['dt'].notna()]
    registered = registered[registered['dt'].dt.date.isin(target_dates)]
    registered_uids = registered['uid'].unique()

    if len(registered_uids) == 0:
        return pd.DataFrame(columns=['uid', 'amount'])

    # deposits by those users
    deposits = df2[(df2['uid'].isin(registered_uids)) & (df2['transaction'] == 'deposit')].copy()

    if deposits.empty:
        return pd.DataFrame(columns=['uid', 'amount'])

    # sort by uid and datetime descending to pick latest deposits
    deposits.sort_values(['uid', 'dt'], ascending=[True, False], inplace=True)

    # take up to 2 latest deposits per uid
    top2 = deposits.groupby('uid', as_index=False).head(2)

    # sum amounts per uid
    sums = top2.groupby('uid', as_index=False)['amount'].sum()
    sums = sums.rename(columns={'amount': 'amount'})

    # Optionally, ensure amounts are numeric
    sums['amount'] = pd.to_numeric(sums['amount'], errors='coerce').fillna(0)

    return sums


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sum two latest deposits for users who registered on 2023-10-01/02')
    parser.add_argument('--df', default='data.csv', help='Path to registrations file (data.csv)')
    parser.add_argument('--df2', default='data2.csv', help='Path to transactions file (data2.csv)')
    parser.add_argument('--out', help='Optional output CSV path')
    args = parser.parse_args(argv)

    df_path = Path(args.df)
    df2_path = Path(args.df2)

    if not df_path.exists():
        print(f"Registration file not found: {df_path}", file=sys.stderr)
        sys.exit(2)
    if not df2_path.exists():
        print(f"Transactions file not found: {df2_path}", file=sys.stderr)
        sys.exit(2)

    df = pd.read_csv(df_path)
    df2 = pd.read_csv(df2_path)

    result = compute_sum_two_latest_deposits(df, df2)

    if result.empty:
        print("No matching deposits found for users who registered on 2023-10-01 or 2023-10-02.")
    else:
        # Sort by uid for stable output
        result = result.sort_values('uid').reset_index(drop=True)
        if args.out:
            result.to_csv(args.out, index=False)
            print(f"Wrote results to {args.out}")
        else:
            # print as table
            print(result.to_string(index=False))


if __name__ == '__main__':
    main()
