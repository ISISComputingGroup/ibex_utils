import argparse
import datetime
import subprocess
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
        "--days",
        dest="days",
        action="store",
        type=int,
        help="How many days to keep (default: 7)",
        default=7,
    )
    parser.add_argument(
        "--hours",
        dest="hours",
        action="store",
        type=int,
        help="How many hours to keep (default: 0)",
        default=0,
    )
    parser.add_argument(
        "--minutes",
        dest="minutes",
        action="store",
        type=int,
        help="How many minutes to keep (default: 0)",
        default=0,
    )
    parser.add_argument("--user", dest="user", action="store", help="mysql user", default="root")
    parser.add_argument(
        "--password", dest="password", action="store", help="mysql password", default=""
    )
    parser.add_argument(
        "--backup", dest="backup", action="store", help="backup data before deleting to file"
    )
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="dry run")

    args = parser.parse_args()
    sample_id_max = None
    sample_id_min = None
    count_sample_id = None
    time_interval = datetime.timedelta(days=args.days, hours=args.hours, minutes=args.minutes)
    cutoff_time = datetime.datetime.now() - time_interval
    cutoff_isotime = cutoff_time.isoformat(" ", "seconds")
    # ignore pyright checking as oracle bug in type signature of close() method
    with closing(
        mysql.connector.connect(
            user=args.user, password=args.password, host=args.host, database="archive"
        )  # pyright: ignore
    ) as conn:
        # this is so we don't cache query results and keep getting the same answer
        conn.autocommit = True

        with closing(conn.cursor(prepared=True)) as c:
            print(f"Looking for sample_id corresponding to {cutoff_isotime}")
            c.execute(f"SELECT MAX(sample_id) FROM sample WHERE smpl_time < '{cutoff_isotime}'")
            sample_id_max = c.fetchone()[0]
            c.execute(f"SELECT MIN(sample_id) FROM sample WHERE smpl_time < '{cutoff_isotime}'")
            sample_id_min = c.fetchone()[0]
            c.execute(f"SELECT COUNT(sample_id) FROM sample WHERE smpl_time < '{cutoff_isotime}'")
            count_sample_id = c.fetchone()[0]
            print(
                f"ID range to delete is {sample_id_min} to {sample_id_max} "
                f"and there are {count_sample_id} rows "
                f"-> {int(1 + count_sample_id / args.limit)} delete operations"
            )

    if args.backup:
        command = [
            r"C:\Instrument\Apps\MySQL\bin\mysqldump.exe",
            f"--user={args.user}",
            f"--password={args.password}",
            f"--host={args.host}",
            "--single-transaction",
            f"--result-file={args.backup}",
            "--no-create-db",
            "--no-create-info",
            "--skip-triggers",
            "--quick",
            f"--where=sample_id >= {sample_id_min} AND sample_id <= {sample_id_max} "
            f"AND smpl_time < '{cutoff_isotime}'",
            "archive",
            "sample",
        ]
        if args.dry_run:
            print(command)
        else:
            subprocess.run(command, check=True)

    # ignore pyright checking as oracle bug in type signature of close() method
    with closing(
        mysql.connector.connect(
            user=args.user, password=args.password, host=args.host, database="archive"
        )  # pyright: ignore
    ) as conn:
        # this is so we don't cache query results and keep getting the same answer
        conn.autocommit = True

        with closing(conn.cursor(prepared=True)) as c:
            c.execute("SET SQL_LOG_BIN=0")  # disable any binary logging for this session
            delete_ops = int(1 + count_sample_id / args.limit)

            print(
                f"ID range to delete is {sample_id_min} to {sample_id_max} "
                f"and there are {count_sample_id} rows "
                f"-> {delete_ops} delete operations"
            )
            print(
                f"This will take at least {args.sleep * delete_ops:.1f} "
                "seconds based on sleep time alone"
            )
            if args.dry_run:
                print("Exiting as dry-run")
                return
            rowcount = 1
            it = 0
            progress = 0
            while rowcount > 0:
                c.execute(
                    f"DELETE FROM sample WHERE sample_id >= {sample_id_min} AND "
                    f"sample_id <= {sample_id_max} AND smpl_time < '{cutoff_isotime}' "
                    f"LIMIT {args.limit}"
                )
                rowcount = c.rowcount
                so_far = 100.0 * it / delete_ops
                if so_far > progress:
                    print(f"{progress}% ", end="", flush=True)
                    progress += 5
                it += 1
                time.sleep(args.sleep)
            print("")


if __name__ == "__main__":
    main()
