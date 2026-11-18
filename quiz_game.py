from default_quizzes import get_default_quizzes


class QuizGame:
    """퀴즈 게임 전체(메뉴, 입력, 진행)를 관리하는 클래스."""

    def __init__(self):
        self.quizzes = get_default_quizzes()  # 퀴즈 목록 (Quiz 객체들의 list)

    def show_menu(self):
        """메인 메뉴를 화면에 출력한다."""
        print()
        print("=" * 40)
        print("      📷 카메라와 필름 퀴즈 게임 🎞️")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

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

    def play_quiz(self):
        """저장된 퀴즈를 순서대로 출제하고, 다 풀면 결과를 보여준다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return

        total = len(self.quizzes)
        correct = 0
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")

        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            print("-" * 40)
            quiz.display(number)
            user_answer = self.ask_int("정답 입력: ", 1, 4)

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct += 1
            else:
                answer_text = quiz.choices[quiz.answer - 1]
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({answer_text}) 입니다.")

        score = round(correct / total * 100)
        print()
        print("=" * 40)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print("=" * 40)

    def run(self):
        """메뉴를 반복해서 보여주고, 선택한 번호에 맞는 기능을 실행한다."""
        try:
            while True:
                self.show_menu()
                choice = self.ask_int("선택: ", 1, 5)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    print("\n🚧 퀴즈 추가는 준비 중입니다.")
                elif choice == 3:
                    print("\n🚧 퀴즈 목록은 준비 중입니다.")
                elif choice == 4:
                    print("\n🚧 점수 확인은 준비 중입니다.")
                else:
                    print("\n👋 게임을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되어 프로그램을 종료합니다.")
            # TODO: 파일 저장 기능 구현 후, 여기서 현재 상태를 저장한다.
