import smtplib


class Mail:
    def __init__(self):
        self.email = "idan6767.angela_python@outlook.co.il"
        self.password = "Aa12313081308"

    def send_mail(self, message):
        with smtplib.SMTP("outlook.office365.com") as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            connection.sendmail(
                from_addr=self.email,
                to_addrs="idan6767@gmail.com",
                msg=f"Subject:📉 Auto-Stocks(Bot) Update\r\n\r\n{message}"
                .encode('utf-8'))

