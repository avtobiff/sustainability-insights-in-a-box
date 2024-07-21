from ncclient.operations.subscribe import *
from ncclient import manager

from utils import messaging
from utils.applog import logconfig, logger


device_params = {"name": "dev0"}


def do_yang_push(host, port, username, password):
    with manager.connect(host=host, port=port, username=username,
                         password=password) as m:
        m.establish_subscription("ds:operational",
                                 "/poweff:poweff/stats/device-current-total-power-draw",
                                 "500")
        while True:
            payload = messaging.consume(schedules_topic, "collector")
            task_config = json.loads(payload)
            customer = task_config["customer"]["name"]
            sites = task_config["sites"]
            device = task_config["device"]["name"]
            conn_type = task_config["device"]["connection"]
            loglevel = task_config["loglevel"]["console"]

            logconfig(customer, loglevel)

            # The YANG-Push notification
            notif = m.take_notification().notification_ele
            device_current_total_power_draw = notif[1][1][0][0][0].text

            logger.info(f"{device} sending poweff"
                        f"{device_current_total_power_draw} to message queue")

            batch_task.copy()
            batch_task["poweff"] = device_current_total_power_draw
            messaging.produce(topic="collections", key=device,
                              message=batch_task)


if __name__ == '__main__':
    do_yang_push("172.19.0.1", 12022, username="admin", password="admin")
