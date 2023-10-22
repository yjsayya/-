import datetime, requests, yaml

# config.yaml 파일 읽기
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']

class Message:

    @staticmethod
    def send_message(msg):
        """디스코드로 메세지 전송하기"""
        now = datetime.datetime.now()
        message = {"**" + f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}

        requests.post(DISCORD_WEBHOOK_URL, data=message)
