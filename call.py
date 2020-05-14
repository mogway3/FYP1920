from twilio.rest import Client


def send_message():
    account_sid = ''
    auth_token = ''
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                              body='You have a good smile!',
                              from_='whatsapp:+14155238886',
                              to='whatsapp:+'
                          )
