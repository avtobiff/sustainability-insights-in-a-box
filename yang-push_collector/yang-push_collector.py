from ncclient.operations.subscribe import *
from ncclient import manager

from normalisers import normaliser_factory
from utils import messaging
from utils.applog import logconfig, logger


device_params = {"name": "dev0"}


def main(host, port, username, password):

    logconfig(level="INFO")
    logger.info("Waiting for collection requests")

    with manager.connect(host=host, port=port, username=username,
                         password=password) as m:
        m.establish_subscription("ds:operational",
                                 "/poweff:poweff/stats/device-current-total-power-draw",
                                 "500")
        while True:
            payload = messaging.consume("yang-push_collector", "collector")
            task_config = json.loads(payload)
            customer = task_config["customer"]["name"]
            sites = task_config["sites"]
            device = task_config["device"]["name"]
            conn_type = task_config["device"]["connection"]
            loglevel = task_config["loglevel"]["console"]

            logconfig(customer, loglevel)

            normaliser = normaliser_factory.get_normaliser(task_config)

            # The YANG-Push notification
            notif = m.take_notification().notification_ele
            device_current_total_power_draw = notif[1][1][0][0][0].text

            poweff_data = normaliser.normalise(sites, task_config["device"],
                                               device_current_total_power_draw)

            logger.info(f"{device} sending poweff"
                        f"{device_current_total_power_draw} to message queue")

            batch_task.copy()
            batch_task["poweff"] = poweff_data
            messaging.produce(topic="collections", key=device,
                              message=batch_task)


if __name__ == '__main__':
    main("172.17.0.1", 12022, username="admin", password="admin")
