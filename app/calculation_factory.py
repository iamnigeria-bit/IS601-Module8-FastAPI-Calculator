
class Add:
    def calculate(self, a: float, b: float) -> float:
        return a + b


class Subtract:
    def calculate(self, a: float, b: float) -> float:
        return a - b


class Multiply:
    def calculate(self, a: float, b: float) -> float:
        return a * b


class Divide:
    def calculate(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b


class CalculationFactory:
    _operations = {
        "add": Add,
        "sub": Subtract,
        "multiply": Multiply,
        "divide": Divide,
    }

    @classmethod
    def create(cls, calculation_type: str):
        operation_class = cls._operations.get(calculation_type)

        if operation_class is None:
            raise ValueError("Unsupported calculation type.")

        return operation_class()
