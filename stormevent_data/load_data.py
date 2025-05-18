#!/bin/python3

import sqlite3
from pathlib import Path
import csv
import sys

conn = sqlite3.connect('data.db')
cursor = conn.cursor()


def main():
    load_storm_event_data()


def load_storm_event_data():
    pathroot = Path('storm_events/data/').glob('**/*.csv')
    for path in pathroot:
        print(path)
        path = str(path)

        ## get the table name to insert data into
        table_name = ''
        if 'fatalities' in path:
            table_name = 'stormevent_fatalities'
        elif 'details' in path:
            table_name = 'stormevent_details'
        elif 'locations' in path:
            table_name = 'stormevent_locations'

        ## read the data file
        with open(path) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            headers = list()
            for i, row in enumerate(reader):
                ## get the headers
                if i == 0:
                    headers = row
                    continue

                ## create the statement
                stmt = f"""
                insert into {table_name}({', '.join(headers)})
                values("""
                for entry in row:
                    if entry.isdigit():
                        stmt += entry+',\n\t'
                    else:
                        stmt += '\''+entry.replace('\'', '\'\'')+'\',\n\t'

                stmt = stmt.strip()[:-1]+')'

                ## insert the row into the database
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(stmt)
                    print(e)
                    sys.exit(1)
            conn.commit()


if __name__ == "__main__":
    main()
