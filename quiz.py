class Quiz:
    """퀴즈 한 문제(문제, 선택지 4개, 정답 번호)를 표현하는 클래스."""

    def __init__(self, question, choices, answer):
        self.question = question  # 문제 문장 (str)
        self.choices = choices    # 선택지 4개 (list of str)
        self.answer = answer      # 정답 번호 1~4 (int)

    def display(self, number):
        """문제 번호와 함께 문제와 선택지를 출력한다."""
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")
        print()

    def is_correct(self, user_answer):
        """사용자가 고른 번호가 정답이면 True, 아니면 False를 반환한다."""
        return user_answer == self.answer

    def to_dict(self):
        """JSON으로 저장할 수 있도록 퀴즈를 dict로 바꿔 반환한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        """dict로부터 Quiz 객체를 만든다. 형식이 잘못되면 예외가 발생한다.

        - 키가 없으면 KeyError, data가 dict가 아니면 TypeError
        - 값이 규칙(문제는 빈 값 아님, 선택지 4개, 정답 1~4)에 맞지 않으면 ValueError
        """
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]

        if type(question) is not str or not question.strip():
            raise ValueError("문제가 비어 있거나 문자열이 아닙니다.")
        if type(choices) is not list or len(choices) != 4:
            raise ValueError("선택지는 4개의 리스트여야 합니다.")
        for choice in choices:
            if type(choice) is not str or not choice.strip():
                raise ValueError("선택지가 비어 있거나 문자열이 아닙니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4 사이의 정수여야 합니다.")

        return cls(question, choices, answer)
