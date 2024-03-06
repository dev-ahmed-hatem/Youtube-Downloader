from PyQt5.Qt import QObject, QThread


# takes an array of signals and bounded slots then initiating QThread
def initiate_thread(
        thread: QThread,
        handler: QObject,
        **kwargs,
):
    handler.moveToThread(thread)

    for event in kwargs["events"]:
        for slot in event["slots"]:
            event['signal'].connect(slot)

    thread.start()
