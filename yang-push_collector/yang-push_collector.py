from ncclient.operations.subscribe import *
from ncclient import manager

device_params = {"name": "dev0"}

def do_yang_push(host, port, username, password):
    with manager.connect(host=host, port=port, username=username,
                         password=password) as m:
        m.establish_subscription("ds:operational",
                                 "/poweff:poweff/stats/device-current-total-power-draw",
                                 "500")
        while True:
            notif = m.take_notification().notification_ele
            print(notif[1][1][0][0][0].text)

if __name__ == '__main__':
    do_yang_push("localhost", 12022, username="admin", password="admin")
