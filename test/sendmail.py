import smtplib

server = smtplib.SMTP('mail.vietinterview.com', 587)
server.starttls()
server.login("contact@vietinterview.com", "Tc!@#6102")

msg = "YOUR MESSAGE!"
server.sendmail("contact@vietinterview.com", "technicalmanager@gmail.com", msg)
server.quit()