import random


class Dice:
    PROBABILITY_TOLERANCE = 1e-6  # Allowed floating-point deviation from sum=1.0

    def __init__(self, probabilities: list):
        self._validate(probabilities)
        self.probabilities = list(probabilities)
        self.num_faces = len(probabilities)


    def roll(self) -> int:

        faces = list(range(1, self.num_faces + 1))
        return random.choices(faces, weights=self.probabilities, k=1)[0]

    def roll_many(self, number_of_rolls: int) -> list:

        self._validate_rolls(number_of_rolls)
        faces = list(range(1, self.num_faces + 1))
        return random.choices(faces, weights=self.probabilities, k=number_of_rolls)

    def summarize(self, number_of_rolls: int) -> dict:

        rolls = self.roll_many(number_of_rolls)
        counts = {face: 0 for face in range(1, self.num_faces + 1)}
        for r in rolls:
            counts[r] += 1
        frequencies = {face: round(counts[face] / number_of_rolls, 6)
                       for face in counts}
        return {
            "rolls": rolls,
            "counts": counts,
            "frequencies": frequencies,
            "num_faces": self.num_faces,
            "number_of_rolls": number_of_rolls,
        }

    def __repr__(self) -> str:
        return (f"Dice(num_faces={self.num_faces}, "
                f"probabilities={self.probabilities})")


    def _validate(self, probabilities):
        if not isinstance(probabilities, (list, tuple)):
            raise TypeError(
                f"probabilities must be a list or tuple, got {type(probabilities).__name__}."
            )
        if len(probabilities) == 0:
            raise ValueError("probabilities must not be empty.")
        for i, p in enumerate(probabilities):
            if not isinstance(p, (int, float)):
                raise TypeError(
                    f"All probabilities must be numeric; "
                    f"got {type(p).__name__} at index {i}."
                )
            if p < 0:
                raise ValueError(
                    f"All probabilities must be >= 0; "
                    f"got {p} at index {i}."
                )
        total = sum(probabilities)
        if abs(total - 1.0) > self.PROBABILITY_TOLERANCE:
            raise ValueError(
                f"Probabilities must sum to 1.0; current sum = {total:.8f}."
            )

    @staticmethod
    def _validate_rolls(number_of_rolls):
        if not isinstance(number_of_rolls, int):
            raise TypeError(
                f"number_of_rolls must be an int, got {type(number_of_rolls).__name__}."
            )
        if number_of_rolls < 1:
            raise ValueError(
                f"number_of_rolls must be >= 1, got {number_of_rolls}."
            )