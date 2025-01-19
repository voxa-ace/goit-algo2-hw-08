import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        """
        Initializes the Throttling Rate Limiter with the given minimum interval.

        :param min_interval: Minimum interval (in seconds) between messages for a user.
        """
        self.min_interval = min_interval
        self.last_message_time: Dict[str, float] = {}  # Stores the last message time for each user

    def can_send_message(self, user_id: str) -> bool:
        """
        Checks if the user can send a message based on the time of the last message.

        :param user_id: ID of the user.
        :return: True if the user can send a message, False otherwise.
        """
        current_time = time.time()
        last_time = self.last_message_time.get(user_id, 0.0)
        return current_time - last_time >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Records a new message for the user if allowed.

        :param user_id: ID of the user.
        :return: True if the message was successfully recorded, False otherwise.
        """
        if self.can_send_message(user_id):
            self.last_message_time[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Calculates the time until the user can send the next message.

        :param user_id: ID of the user.
        :return: Time in seconds until the next allowed message.
        """
        current_time = time.time()
        last_time = self.last_message_time.get(user_id, 0.0)
        remaining_time = self.min_interval - (current_time - last_time)
        return max(0.0, remaining_time)

# Demonstration of functionality
def test_throttling_limiter():
    """
    Demonstrates the functionality of the Throttling Rate Limiter with example scenarios.
    """
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Simulating message stream (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")

        # Random delay between messages
        time.sleep(random.uniform(0.1, 1.0))

    print("\nWaiting 4 seconds...")
    time.sleep(4)

    print("\n=== New message stream after waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()
