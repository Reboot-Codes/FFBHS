# Firefox Browser History Scrubber

Clean up your firefox browser history & bookmarks.

## Usage

Place a valid `places.sqlite` file in the same working directory, add regexes to scrub to the script, then run to get a scubbed `places_scrubbed.sqlite` file in the same working directory.

## Theory

Cleaning up firefox browser history is a fucking pain, and editing it is impossible, so this script exists. An example of history **manipulation** is turning outlook into gmail. It will edit in place so the times line up.

It's all just SQL and Regex.
