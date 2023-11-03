import numpy as np


class UnbalancedExpressionError(Exception):
    pass


class CalulateError(Exception):
    pass


class Calculator:
    def __init__(self) -> None:
        self.OPERATORS = "+-*/^"
        self.FUNC_KEYWORD = "func"
        self.FUNCTIONS = {"cos": np.cos, "sin": np.sin, "tg": np.tan, "ctg": lambda x: 1 / np.tan(x)}
        self.OPEN_BRACKET = "("
        self.CLOSED_BRACKET = ")"
        self.BREAK = "?"
        self.SEPARATOR = "."
        self.stackNumbers: list[np.float64] = []
        self.stackOperators: list[str] = []
        self.stackRPN: list[str] = []
    
        self.enum_modifiers: dict[str, int] = {
            self.BREAK: 0,
            self.OPERATORS[0]: 1,
            self.OPERATORS[1]: 2,
            self.OPERATORS[2]: 3,
            self.OPERATORS[3]: 4,
            self.OPERATORS[4]: 5,
            self.FUNC_KEYWORD: 6,
            self.OPEN_BRACKET: 7,
            self.CLOSED_BRACKET: 8
        }

        self.priority: list[list[int]] = [
            [4, 1, 1, 1, 1, 1, 1, 1, 5],
            [2, 2, 2, 1, 1, 1, 1, 1, 2],
            [2, 2, 2, 1, 1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2, 1, 1, 1, 2],
            [2, 2, 2, 2, 2, 1, 1, 1, 2],
            [2, 2, 2, 2, 2, 2, 1, 1, 2],
            [2, 2, 2, 2, 2, 2, 1, 1, 2],
            [5, 1, 1, 1, 1, 1, 1, 1, 3]
        ]
    
    def stringSplit(self, expression: str) -> list[str]:
        expression = expression.replace(" ", "").replace("(-", "(0-").replace(f"{self.SEPARATOR}-", f"{self.SEPARATOR}0-")
        if expression[0] == '-':
            expression = "0" + expression

        extra = ""

        result: list[str] = []

        for i in expression:
            if i in self.OPERATORS or i == self.CLOSED_BRACKET or i == self.OPEN_BRACKET:
                if extra:
                    result.append(extra)
                    extra = ""
                result.append(i)
            else:
                extra += i

        if extra:
            result.append(extra)

        result.append(self.BREAK)
        return result
    
    def isNumber(self, item: str) -> bool:
        try:
            float(item)
        except ValueError:
            return False
        return True

    def listToRPN(self, arr: list[str]) -> None:
        self.stackRPN.clear()
        self.stackOperators.clear()
        self.stackOperators.append(self.BREAK)

        for item in arr:
            if self.isNumber(item):
                self.stackRPN.append(item)
            else:
                while True:
                    currentItem = item if item not in self.FUNCTIONS else self.FUNC_KEYWORD
                    previousItem = self.stackOperators[-1] if self.stackOperators[-1] not in self.FUNCTIONS else self.FUNC_KEYWORD
                    whatToDo = self.priority[self.enum_modifiers[previousItem]][self.enum_modifiers[currentItem]]

                    if whatToDo == 1:
                        self.stackOperators.append(item)
                        break
                    elif whatToDo == 2:
                        self.stackRPN.append(self.stackOperators.pop())
                    elif whatToDo == 3:
                        self.stackOperators.pop()
                        break
                    elif whatToDo == 4:
                        return
                    else:
                        raise UnbalancedExpressionError("Проверьте скобки")
                    
    
    def calculate(self, expression: str) -> np.float64 | float:
        self.listToRPN(self.stringSplit(expression))
        self.stackNumbers.clear()
        for item in self.stackRPN:
            if self.isNumber(item):
                self.stackNumbers.append(np.float64(float(item)))
            else:
                try:
                    val2 = self.stackNumbers.pop()
                    val1 = 0
                    if item in self.OPERATORS:
                        val1 = self.stackNumbers.pop()
                except IndexError:
                    raise IndexError
                if item == "+":
                    self.stackNumbers.append(val1 + val2)
                elif item == "-":
                    self.stackNumbers.append(val1 - val2)
                elif item == "*":
                    self.stackNumbers.append(val1 * val2)
                elif item == "/":
                    res = val1 / val2
                    if res == np.inf:
                        return np.inf
                    self.stackNumbers.append(res)
                elif item == "^":
                    self.stackNumbers.append(val1 ** val2)
                else:
                    self.stackNumbers.append(self.FUNCTIONS[item](val2))

        return self.stackNumbers[0]