from src import config


class StepController:
    """
    Controls the maximum number of agent steps
    to prevent infinite loops.
    """

    def __init__(self, max_steps: int = config.MAX_STEP):
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self):
        """Reset step counter for a new run."""
        self.current_step = 0

    def next(self):
        """
        Move to next step.
        Returns True if more steps allowed, False if exceeded.
        """
        self.current_step += 1

        if self.current_step > self.max_steps:
            return False

        return True

    def remaining(self):
        """Return how many steps remain."""
        return self.max_steps - self.current_step

    def is_exceeded(self):
        """Check if step limit reached."""
        return self.current_step >= self.max_steps
