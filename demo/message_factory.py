import os
import smtplib
import sys
import typing as t
from email.mime.text import MIMEText

from webexteamssdk import WebexTeamsAPI

from create_config import create_config

GREETINGS = 'Hello from yang-catalog'


class MessageFactory:
    """This class serves to automatically send a message to
    Webex Teams cisco admins private room and/or to send
    a message to a group of admin e-mails
    """

    def __init__(self, config_path: str = os.environ['YANGCATALOG_CONFIG_PATH']):
        """Setup Webex teams rooms and smtp

        Arguments:
            :param config_path: (str) path to a yangcatalog.conf file
        """

        def list_matching_rooms(a: WebexTeamsAPI, title_match: str) -> list:
            return [r for r in a.rooms.list() if title_match in r.title]

        config = create_config(config_path)
        token = config.get('Secrets-Section', 'webex-access-token')
        self._email_from = config.get('Message-Section', 'email-from')
        self._is_production = config.get('General-Section', 'is-prod') == 'True'
        self._email_to = ['bodiakonovalenko@gmail.com']
        self._developers_email = config.get('Message-Section', 'developers-email').split()
        self._temp_dir = config.get('Directory-Section', 'temp')
        self._domain_prefix = config.get('Web-Section', 'domain-prefix')
        self._me = 'YANGCATALOG DEMO'

        self._api = WebexTeamsAPI(access_token=token)
        rooms = list_matching_rooms(self._api, 'YANG Catalog Test')
        self._validate_rooms_count(rooms)
        self._room = rooms[0]

        self._smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self._smtp.starttls()
        self._smtp.login('bgram.info.service@gmail.com', 'tgyflsirtewrgozj')
        self._message_log_file = os.path.join(self._temp_dir, 'message-log.txt')

    def _validate_rooms_count(self, rooms: list):
        if len(rooms) == 0:
            sys.exit(1)
        if len(rooms) != 1:
            sys.exit(1)

    def _post_to_webex(self, msg: str, markdown: bool = False, files: t.Union[list, tuple] = ()):
        """Send message to a webex room

        Arguments:
            :param msg          (str) message to send
            :param markdown     (bool) whether to use markdown. Default False
            :param files        (list) list of paths to files that need to be attached with the message. Default None
        """
        msg += f'\n\nMessage sent from {self._me}'
        if not self._is_production:
            if files:
                for f in files:
                    os.remove(f)
            return
        if markdown:
            self._api.messages.create(self._room.id, markdown=msg, files=files or None)
        else:
            self._api.messages.create(self._room.id, text=msg, files=files or None)

        if files:
            for f in files:
                os.remove(f)

    def _post_to_email(
        self,
        message: str,
        email_to: t.Union[list, tuple] = (),
        subject: str = '',
        subtype: str = 'plain',
    ):
        """Send message to an e-mail

        Arguments:
            :param message      (str) message to send
            :param email_to     (list) list of emails to send the message to
            :param subject      (str) subject string
            :param subtype      (str) MIME text sybtype of the message. Default is "plain".
        """
        send_to = self._email_to
        newline_character = '<br>' if subtype == 'html' else '\n'
        msg = MIMEText(f'{message}{newline_character}{newline_character}Message sent from {self._me}', _subtype=subtype)
        msg['Subject'] = subject or 'Automatic generated message - RFC IETF'
        msg['From'] = self._email_from
        msg['To'] = ', '.join(send_to)

        self._smtp.sendmail(self._email_from, send_to, msg.as_string())
        self._smtp.quit()
