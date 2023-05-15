import email
import imaplib
import dateparser
from dotenv import dotenv_values

ENV = dotenv_values('.env')
# EXTRACAO_OUT = ENV['EXTRACAO_OUT']
EMAIL = ENV['EMAIL']
PW = ENV['PW']


def email_to_html(parsed):
    """
    iterate over all the parts from email body (parsed)
    and concatenates into a string.

    returns: str
    """

    all_parts = []
    for part in parsed.walk():
        if type(part.get_payload()) == list:
            for subpart in part.get_payload():
                all_parts += email_to_html(subpart)
        else:
            if encoding := part.get_content_charset():
                all_parts.append(
                    part.get_payload(decode=True).decode(encoding)
                )
    return ''.join(all_parts)


def imap_session(func):
    def wrapper(*args, **kwargs):
        imap_session = imaplib.IMAP4_SSL('imap.gmail.com')
        typ, accountDetails = imap_session.login(EMAIL, PW)
        if typ != 'OK':
            print('Not able to sign in!')
            return False

        imap_session.select('INBOX')
        result = func(*args, **kwargs, imap_session=imap_session)

        imap_session.close()
        imap_session.logout()

        return result

    return wrapper


@imap_session
def get_email_ids(FROM, imap_session):
    typ, data = imap_session.search(None, f'(UNSEEN FROM "{FROM}")')
    if typ != 'OK':
        print('Error searching Inbox.')
        return False

    return data[0].split()[::-1]


@imap_session
def get_email_info(msg_id, imap_session):
    typ, messageParts = imap_session.fetch(msg_id, '(RFC822)')
    if typ != 'OK':
        print('Error fetching mail.')

    emailBody = messageParts[0][1]
    mail = email.message_from_bytes(emailBody)

    sub_ = mail['Subject']
    from_ = mail['From']
    mail_date = dateparser.parse(mail['Date'])
    body_html = email_to_html(mail)

    return {
        'mail_id': int(msg_id),
        'from': from_,
        'subject': sub_,
        'date': mail_date,
        'body': body_html,
    }
