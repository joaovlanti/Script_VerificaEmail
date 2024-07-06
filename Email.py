import imaplib
import email
from email.header import decode_header
from telegram import Bot
import asyncio
import time
import logging

# Configurações do servidor IMAP e credenciais
IMAP_SERVER = 'imap.gmail.com'
EMAIL = 'youremail@gmail.com'
PASSWORD = 'your password application'  # Use a senha de aplicativo do Gmail

# Configuração de logging
logging.basicConfig(filename='logEmail.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Função assíncrona para enviar a mensagem
async def send_telegram_message(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

def fetch_unread_emails():
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)

        # Selecionar a caixa de entrada (inbox)
        mail.select('inbox')

        # Procurar por emails não lidos direcionados a você (joao.lanti@a7.net.br)
        status, messages = mail.search(None, '(UNSEEN TO "%s")' % EMAIL)

        if not messages[0].split():
            logging.info("Nenhum email novo encontrado.")
        else:
            # Loop através dos IDs dos emails não lidos
            for num in messages[0].split():
                status, msg = mail.fetch(num, '(RFC822)')
                for response_part in msg:
                    if isinstance(response_part, tuple):
                        # Parsear o email
                        email_message = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(email_message['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        sender = email_message['From']
                        date = email_message['Date']

                        # Formatar mensagem para o Telegram e logs
                        log_message = f"Email de: {sender}\nTítulo: {subject}\nData: {date}"
                        logging.info(log_message)

                        telegram_message = (
                            f"📧 **Novo email recebido**:\n"
                            f"👤 **De**: {sender}\n"
                            f"📝 **Título**: {subject}\n"
                            f"📅 **Data**: {date}"
                        )

                        # Enviar notificação no Telegram
                        bot_token = '6499614985:AAE6TtbsWErKKiAgK3iW2-GoIsKTy8FFc5I'
                        chat_id = '-4110102247'
                        asyncio.run(send_telegram_message(bot_token, chat_id, telegram_message))

                        # Aguardar um intervalo para evitar flood control no Telegram
                        time.sleep(5)

        # Fechar conexão com o servidor IMAP
        mail.logout()

    except imaplib.IMAP4.error as e:
        logging.error(f"Erro IMAP: {e}")
    except Exception as e:
        logging.error(f"Erro geral: {e}")

if __name__ == "__main__":
    while True:
        fetch_unread_emails()
        time.sleep(60)  # Espera 60 segundos antes de verificar novamente
