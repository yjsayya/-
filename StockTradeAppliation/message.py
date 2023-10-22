import datetime, requests

class Message:

    startMessage = "===[Program Init]======================"
    endMessage = "프로그램을 종료합니다."

    @staticmethod
    def send_message(msg,DISCORD_WEBHOOK_URL):
        """디스코드로 메세지 전송하기"""
        now = datetime.datetime.now()
        message = {"**" + f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
        requests.post(DISCORD_WEBHOOK_URL, data=message)
