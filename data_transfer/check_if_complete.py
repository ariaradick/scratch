import os,time
import email
from email.message import EmailMessage
import smtplib

logfile = "test_error.txt"

if (time.time() - os.path.getmtime(logfile)) > 1:
    smtp = smtplib.SMTP("localhost")
    send_from = 'data_transfer_bot'
    send_to = 'aria.radick@noaa.gov'
    msg = EmailMessage()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = email.utils.formatdate(localtime=True)
    
    with open(logfile) as f:
        for line in f:
            pass
        last_line = line
    print(last_line)
    if last_line == "Transfer complete!":
        msg['Subject'] = "Data transfer complete"
        smtp.send_message(msg)
        smtp.quit()
    else:
        msg.set_content("It has been more than one hour since a file has been transferred. The cron job has been stopped.\nThe last line of the log is:\n\n")
        msg.add_attachment(last_line)
        msg['Subject'] = "Data transfer stalled"
        smtp.send_message(msg)
        smtp.quit()
