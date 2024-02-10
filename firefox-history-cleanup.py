import os
import sqlite3
import re
from shutil import copyfile


places_db = os.path.join(os.getcwd(), 'places.sqlite')
copyfile(places_db, os.path.join(os.getcwd(), "places_scrubbed.sqlite"))
places_toMod_db = os.path.join(os.getcwd(), "places_scrubbed.sqlite")

c = sqlite3.connect(places_toMod_db)
cursor = c.cursor()

do_not_include_in_hist = []
do_not_include_in_doms = []
to_obfuscate = []
fake_email = ""


def scrub_hist():
    cursor.execute("select moz_places.url, moz_places.id from moz_places;")
    place_entries = cursor.fetchall()

    for place_entry in place_entries:
        for pattern in do_not_include_in_hist:
            regexTest = re.findall(pattern, place_entry[0], flags=re.IGNORECASE)
            if len(regexTest) > 0:
                print(f"deleting {place_entry} (matches {regexTest})")
                
                try:
                    cursor.execute(f"delete from moz_places where moz_places.id={place_entry[1]};")
                except sqlite3.OperationalError:
                    print(f"Warn: failed to delete \"{place_entry[0]}\" ({place_entry[1]})...")
    
    c.commit()


def scrub_doms():
    cursor.execute("select moz_origins.prefix, moz_origins.host, moz_origins.id from moz_origins;")
    dom_entries = cursor.fetchall()

    for dom_entry in dom_entries:
        for pattern in do_not_include_in_doms:
            regexTest = re.findall(pattern, dom_entry[1], flags=re.IGNORECASE)
            if len(regexTest) > 0:
                print(f"deleting {dom_entry} (matches {regexTest})")

                try:
                    cursor.execute(f"delete from moz_origins where moz_origins.id={dom_entry[2]};")
                except sqlite3.OperationalError:
                    print(f"Warn: failed to delete \"{dom_entry[1]}\" ({dom_entry[2]})...")
    
    c.commit()


def obscure_outlook():
    cursor.execute("select moz_places.url, moz_places.id from moz_places;")
    place_entries = cursor.fetchall()

    for place_entry in place_entries:
        for pattern in to_obfuscate:
            regexTest = re.findall(pattern, place_entry[0], flags=re.IGNORECASE)
            if len(regexTest) > 0:
                new_url = ""
                new_title = "Gmail"

                if len(re.findall("outlook.live.com/mail(/0)?/?$", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/"
                    new_title = "Gmail"
                elif len(re.findall("outlook.live.com/mail(/0)?/junkemail/?$", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/#spam"
                    new_title = f"Spam - {fake_email} - Gmail"
                elif len(re.findall("outlook.live.com/mail(/0)?/junkemail/id/", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/#spam"
                elif len(re.findall("outlook.live.com/mail(/0)?/deeplink/compose", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/#inbox?compose=new"
                    new_title = f"Compose - {fake_email} - Gmail"
                elif len(re.findall("outlook.live.com/mail(/0)?/inbox/?$", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/"
                    new_title = f"Inbox - {fake_email} - Gmail"
                elif len(re.findall("outlook.live.com/mail(/0)?/inbox/id/", place_entry[0], flags=re.IGNORECASE)) > 0:
                    new_url = "https://mail.google.com/mail/u/0/#inbox"
                    new_title = f"Inbox - {fake_email} - Gmail"

                if new_url == "":
                    print(f"deleting {place_entry} (matches {regexTest})")
                    try:
                        cursor.execute(f"delete from moz_origins where host={place_entry[1]};")
                    except sqlite3.OperationalError:
                        print(f"Warn: failed to delete \"{place_entry[0]}\" ({place_entry[1]})...")
                else:
                    print(f"obscuring {place_entry} (matches {regexTest}) as \"{new_url}\"")
                    if new_title == "":
                        try:
                            cursor.execute("update moz_places set url = ? where id=?", (new_url, place_entry[1]))
                        except sqlite3.OperationalError:
                            print(f"Warn: failed to obscure \"{place_entry[0]}\" ({place_entry[1]})...")
                    else:
                        try:
                            cursor.execute("update moz_places set url = ?, title = ? where id=?", (new_url, new_title, place_entry[1]))
                        except sqlite3.OperationalError:
                            print(f"Warn: failed to obfuscate \"{place_entry[0]}\" ({place_entry[1]})...")
    
    c.commit()

def scrub_bookies():
    cursor.execute("select moz_bookmarks.title, moz_bookmarks.id from moz_bookmarks;")
    bookie_entries = cursor.fetchall()

    for bookie_entry in bookie_entries:
        for pattern in do_not_include_in_hist:
            regexTest = re.findall(pattern, str(bookie_entry[0]), flags=re.IGNORECASE)
            if len(regexTest) > 0:
                print(f"deleting {bookie_entry} (matches {regexTest})")
                
                try:
                    cursor.execute(f"delete from moz_bookmarks where moz_bookmarks.id={bookie_entry[1]};")
                except sqlite3.OperationalError:
                    print(f"Warn: failed to delete \"{bookie_entry[0]}\" ({bookie_entry[1]})...")
    
    c.commit()


if __name__ == "__main__":
    try:
        scrub_doms()
        obscure_outlook()
        scrub_hist()
        scrub_bookies()
    except KeyboardInterrupt:
        print("Stopping...")

