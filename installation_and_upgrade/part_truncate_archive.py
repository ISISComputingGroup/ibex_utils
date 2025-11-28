import argparse
import time
from contextlib import closing

import mysql.connector

"""
This script will delete rows from the mysql archive `sample` table
that are more than `history` days old in batches of `limit` to improve performance.

This could be done after a database backup and be used instead of truncating
the entire database. It will not reduce the size of the database file on disk, but the
deleted rows will be re-used by the database and so the file should not grow.

A typical usage would be if the instrument already has information in mysql it would like
to keep a bit longer, or is running. The backup is safe to do on a running as it uses
`single transaction` mode, but if the backup takes 2 hours you'll have two hours of missed
data after a truncate. Hence this script to leave some old data in mysql.  
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Set query options")
    parser.add_argument(
        "--host", dest="host", action="store", help="Host (default: localhost)", default="127.0.0.1"
    )
    parser.add_argument(
        "--limit",
        dest="limit",
        action="store",
        type=int,
        help="Rows to delete each query (default: 1000)",
        default=1000,
    )
    parser.add_argument(
        "--sleep",
        dest="sleep",
        action="store",
        type=float,
        help="Seconds to sleep between queries (default: 0.5)",
        default=0.5,
    )
    parser.add_argument(
        "--history",
        dest="history",
        action="store",
        type=int,
        help="How many days to keep (default: 7)",
        default=7,
    )
    parser.add_argument(
        "--password", dest="password", action="store", help="mysql root password", default=""
    )
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="dry run")

    args = parser.parse_args()

    # ignore pyright checking as oracle bug in type signature of close() method
    with closing(
        mysql.connector.connect(
            user="root", password=args.password, host=args.host, database="archive"
        )  # pyright: ignore
    ) as conn:
        # this is so we don't cache query results and keep getting the same answer
        conn.autocommit = True

        with closing(conn.cursor(prepared=True)) as c:
            c.execute("SET SQL_LOG_BIN=0")  # disable any binary logging for this session
            print(f"Looking for sample_id corresponding to {args.history} days ago")
            c.execute(
                "SELECT MAX(sample_id) FROM sample WHERE smpl_time < TIMESTAMPADD(DAY, -?, NOW())",
                (args.history,),
            )
            sample_id = c.fetchone()[0]
            c.execute(
                "SELECT COUNT(sample_id) FROM sample "
                "WHERE smpl_time < TIMESTAMPADD(DAY, -?, NOW())",
                (args.history,),
            )
            count_sample_id = c.fetchone()[0]
            print(
                f"ID of last row to delete is {sample_id} and there are {count_sample_id} rows "
                f"-> {int(1 + count_sample_id / args.limit)} delete operations"
            )
            print(
                f"This will take at least {args.sleep * count_sample_id / args.limit:.1f} "
                "seconds based on sleep time alone"
            )
            if args.dry_run:
                print("Exiting as dry-run")
                return
            rowcount = 1
            it = 0
            while rowcount > 0:
                c.execute(f"DELETE FROM sample WHERE sample_id < {sample_id} LIMIT {args.limit}")
                rowcount = c.rowcount
                print(f"{it % 10}", end="", flush=True)
                it += 1
                time.sleep(args.sleep)
            print("")


if __name__ == "__main__":
    main()
