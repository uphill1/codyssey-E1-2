from default_quizzes import get_default_quizzes
from quiz import Quiz


class QuizGame:
    """퀴즈 게임 전체(메뉴, 입력, 진행, 점수)를 관리하는 클래스."""

    # 메뉴 번호 (클래스 속성: 모든 QuizGame 객체가 함께 쓰는 고정값)
    MENU_PLAY = 1
    MENU_ADD = 2
    MENU_LIST = 3
    MENU_SCORE = 4
    MENU_EXIT = 5

    CHOICE_COUNT = 4  # 퀴즈 한 문제의 선택지 개수
    LINE_WIDTH = 40   # 구분선 길이

    def __init__(self):
        self.quizzes = get_default_quizzes()  # 퀴즈 목록 (Quiz 객체들의 list)
        self.best_score = None  # 최고 점수(0~100점). 아직 푼 적 없으면 None
        self.best_correct = 0   # 최고 점수를 냈을 때 맞힌 문제 수
        self.best_total = 0     # 최고 점수를 냈을 때 전체 문제 수

    # ---------- 입력 처리 ----------

    def ask_int(self, prompt, lo, hi):
        """lo~hi 범위의 정수를 입력받아 반환한다. 올바른 값이 들어올 때까지 다시 묻는다."""
        while True:
            raw = input(prompt).strip()

            if raw == "":
                print(f"⚠️ 입력이 비어 있습니다. {lo}-{hi} 사이의 숫자를 입력하세요.")
                continue

            try:
                value = int(raw)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {lo}-{hi} 사이의 숫자를 입력하세요.")
                continue

            if value < lo or value > hi:
                print(f"⚠️ 범위를 벗어났습니다. {lo}-{hi} 사이의 숫자를 입력하세요.")
                continue

            return value

    def ask_text(self, prompt):
        """비어 있지 않은 문자열을 입력받아 반환한다. 빈 값이면 다시 묻는다."""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print("⚠️ 빈 값은 입력할 수 없습니다. 다시 입력하세요.")

    # ---------- 화면 출력 도우미 ----------

    def print_line(self, char):
        """char 문자로 구분선을 출력한다. (예: "=" 또는 "-")"""
        print(char * self.LINE_WIDTH)

    def has_quizzes(self):
        """퀴즈가 있으면 True. 없으면 안내 메시지를 출력하고 False를 반환한다."""
        if self.quizzes:
            return True
        print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
        return False

    def show_menu(self):
        """메인 메뉴를 화면에 출력한다."""
        print()
        self.print_line("=")
        print("      📷 카메라와 필름 퀴즈 게임 🎞️")
        self.print_line("=")
        print(f"{self.MENU_PLAY}. 퀴즈 풀기")
        print(f"{self.MENU_ADD}. 퀴즈 추가")
        print(f"{self.MENU_LIST}. 퀴즈 목록")
        print(f"{self.MENU_SCORE}. 점수 확인")
        print(f"{self.MENU_EXIT}. 종료")
        self.print_line("=")

    # ---------- 메뉴 기능 ----------

    def play_quiz(self):
        """저장된 퀴즈를 순서대로 출제하고, 다 풀면 결과를 보여준다."""
        if not self.has_quizzes():
            return

        total = len(self.quizzes)
        correct = 0
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")

        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            self.print_line("-")
            quiz.display(number)
            user_answer = self.ask_int("정답 입력: ", 1, self.CHOICE_COUNT)

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct += 1
            else:
                answer_text = quiz.choices[quiz.answer - 1]
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({answer_text}) 입니다.")

        score = round(correct / total * 100)
        print()
        self.print_line("=")
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if self.update_best_score(score, correct, total):
            print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"(최고 점수: {self.best_score}점)")
        self.print_line("=")

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 목록에 추가한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")

        question = self.ask_text("문제를 입력하세요: ")
        choices = []
        for i in range(1, self.CHOICE_COUNT + 1):
            choices.append(self.ask_text(f"선택지 {i}: "))
        answer = self.ask_int(f"정답 번호 (1-{self.CHOICE_COUNT}): ", 1, self.CHOICE_COUNT)

        self.quizzes.append(Quiz(question, choices, answer))
        # TODO: 파일 저장 기능(10단계) 구현 후, 여기서 state.json에 저장한다.
        print(f"\n✅ 퀴즈가 추가되었습니다! (현재 {len(self.quizzes)}개)")

    def list_quizzes(self):
        """등록된 퀴즈의 문제 목록을 번호와 함께 출력한다."""
        if not self.has_quizzes():
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        self.print_line("-")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        self.print_line("-")

    def show_score(self):
        """최고 점수를 출력한다. 아직 푼 기록이 없으면 안내한다."""
        if self.best_score is None:
            print("\n⚠️ 아직 퀴즈를 푼 기록이 없습니다. 먼저 퀴즈를 풀어보세요.")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점 "
              f"({self.best_total}문제 중 {self.best_correct}문제 정답)")

    # ---------- 점수 로직 ----------

    def update_best_score(self, score, correct, total):
        """이번 점수가 최고 점수보다 높으면 갱신하고 True, 아니면 False를 반환한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            # TODO: 파일 저장 기능(10단계) 구현 후, 여기서 state.json에 저장한다.
            return True
        return False

    # ---------- 실행 ----------

    def run(self):
        """메뉴를 반복해서 보여주고, 선택한 번호에 맞는 기능을 실행한다."""
        try:
            while True:
                self.show_menu()
                choice = self.ask_int("선택: ", self.MENU_PLAY, self.MENU_EXIT)

                if choice == self.MENU_PLAY:
                    self.play_quiz()
                elif choice == self.MENU_ADD:
                    self.add_quiz()
                elif choice == self.MENU_LIST:
                    self.list_quizzes()
                elif choice == self.MENU_SCORE:
                    self.show_score()
                else:
                    print("\n👋 게임을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되어 프로그램을 종료합니다.")
            # TODO: 파일 저장 기능 구현 후, 여기서 현재 상태를 저장한다.
