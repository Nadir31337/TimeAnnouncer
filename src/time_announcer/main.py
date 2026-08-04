from time_announcer.speaker import Speaker
from time_announcer.scheduler import Scheduler


def announce(current_time: str) -> None:
    print(f"Announcing: {current_time}")
    speaker.say(f"It is now {current_time}")


if __name__ == "__main__":
    speaker = Speaker()
    scheduler = Scheduler(interval_seconds=10, on_tick=announce)

    print("Time Announcer running. Press Ctrl+C to stop.")
    scheduler.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nStopped.")