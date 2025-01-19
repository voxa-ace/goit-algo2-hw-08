import random
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Initializes the Sliding Window Rate Limiter with the given parameters.

        :param window_size: Size of the sliding window in seconds.
        :param max_requests: Maximum number of requests allowed within the window.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history = {}  # Users and their request history

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Cleans up outdated requests for the given user.

        :param user_id: ID of the user.
        :param current_time: Current time in seconds.
        """
        if user_id not in self.user_history:
            return

        # Remove all requests outside the active window
        while self.user_history[user_id] and self.user_history[user_id][0] < current_time - self.window_size:
            self.user_history[user_id].popleft()

        # Remove the user if they have no remaining requests
        if not self.user_history[user_id]:
            del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Checks if the user can send a message within the current window.

        :param user_id: ID of the user.
        :return: True if the user can send a message, False otherwise.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Allow the request if the number of requests is below the limit
        return len(self.user_history.get(user_id, [])) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Records a new message for the user if allowed.

        :param user_id: ID of the user.
        :return: True if the message was successfully recorded, False otherwise.
        """
        if self.can_send_message(user_id):
            current_time = time.time()

            if user_id not in self.user_history:
                self.user_history[user_id] = deque()

            self.user_history[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Calculates the time until the user can send the next message.

        :param user_id: ID of the user.
        :return: Time in seconds until the next allowed message.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_history or len(self.user_history[user_id]) < self.max_requests:
            return 0.0

        # Calculate when the next message is allowed
        earliest_request_time = self.user_history[user_id][0]
        return max(0.0, self.window_size - (current_time - earliest_request_time))

# Demonstration of functionality
def test_rate_limiter():
    """
    Demonstrates the functionality of the Sliding Window Rate Limiter with example scenarios.
    """
    # Create a rate limiter: window size 10 seconds, 1 message allowed
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Simulate a stream of messages from users (IDs 1 to 5)
    print("\n=== Simulating message stream ===")
    for message_id in range(1, 11):
        # Simulate different users (IDs 1 to 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")

        # Small delay between messages for realism
        # Random delay between 0.1 and 1 second
        time.sleep(random.uniform(0.1, 1.0))

    # Wait for the window to clear
    print("\nWaiting 4 seconds...")
    time.sleep(4)

    print("\n=== New message stream after waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Message {message_id:2d} | User {user_id} | "
              f"{'✓' if result else f'× (wait {wait_time:.1f}s)'}")
        # Random delay between 0.1 and 1 second
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
