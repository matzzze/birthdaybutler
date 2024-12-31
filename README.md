# birthdaybutler
This is a small python application that reads vcards that are e.g. stored on a radicale carddav instance or locally from a file and extracts the birthdays from the contacts.
You can configure it to send you notifications via nfty or email - so you'll get e.g. notified on your smartphone. Up to two additional pre-reminders are configurable, so you still have time to buy a present for your contact before the actual birthday.
Alternatively it can also update a remote caldav instance on radicale and insert an all-day event into the calendar for the contacts birthday.

# requirements
* debian 12 host machine (ideally a tiny LXC container on proxmox)
* a few python libraries
* (external) ntfy instance
* (external) radicale instance

# Limitations
very basic and dumb application. No warranty. Use at your own risk.

# Installation Instructions
* Get prerequisites
* <code>apt install python3 python3-vobject python3-requests python3-yaml python3-schedule</code>
* Clone repo

# Configuration Instructions

