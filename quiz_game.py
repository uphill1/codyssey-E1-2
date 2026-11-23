import json
import os
import random
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

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
    MENU_DELETE = 6
    MENU_HISTORY = 7

    CHOICE_COUNT = 4  # 퀴즈 한 문제의 선택지 개수
    HINT_PENALTY = 10  # 힌트를 사용한 문제당 차감 점수
    LINE_WIDTH = 40   # 구분선 길이

    # 데이터 파일: 실행 위치와 상관없이 항상 이 파일(quiz_game.py)이 있는 프로젝트 루트의 state.json
    STATE_FILE = Path(__file__).parent / "state.json"

    def __init__(self):
        self.quizzes = get_default_quizzes()  # 퀴즈 목록 (Quiz 객체들의 list)
        self.best_score = None  # 최고 점수(0~100점). 아직 푼 적 없으면 None
        self.best_correct = 0   # 최고 점수를 냈을 때 맞힌 문제 수
        self.best_total = 0     # 최고 점수를 냈을 때 전체 문제 수
        self.score_history = []  # 완료한 게임 기록 (오래된 순서부터 저장)

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
        print(f"{self.MENU_DELETE}. 퀴즈 삭제")
        print(f"{self.MENU_HISTORY}. 점수 기록")
        self.print_line("=")

    # ---------- 메뉴 기능 ----------

    def play_quiz(self):
        """선택한 수만큼 퀴즈를 무작위로 출제하고, 다 풀면 결과를 보여준다."""
        if not self.has_quizzes():
            return

        available = len(self.quizzes)
        total = self.ask_int(f"풀 문제 수 (1-{available}): ", 1, available)
        round_quizzes = self.quizzes.copy()
        random.shuffle(round_quizzes)
        round_quizzes = round_quizzes[:total]
        correct = 0
        hints_used = 0
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")

        for number, quiz in enumerate(round_quizzes, start=1):
            print()
            self.print_line("-")
            quiz.display(number)
            user_answer = self.ask_int(
                f"정답 입력 (0: 힌트, -{self.HINT_PENALTY}점): ", 0, self.CHOICE_COUNT
            )
            if user_answer == 0:
                print(f"💡 힌트: {quiz.get_hint()}")
                hints_used += 1
                user_answer = self.ask_int("정답 입력: ", 1, self.CHOICE_COUNT)

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct += 1
            else:
                answer_text = quiz.choices[quiz.answer - 1]
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({answer_text}) 입니다.")

        base_score = round(correct / total * 100)
        penalty = min(base_score, hints_used * self.HINT_PENALTY)
        score = base_score - penalty
        is_new_best = self.record_result(score, correct, total)
        print()
        self.print_line("=")
        if hints_used:
            print(f"💡 힌트 {hints_used}회 사용 · {penalty}점 차감")
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if is_new_best:
            print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"(최고 점수: {self.best_score}점)")
        self.print_line("=")

    def add_quiz(self):
        """문제, 선택지, 정답, 선택 사항인 힌트를 입력받아 퀴즈를 추가한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")

        question = self.ask_text("문제를 입력하세요: ")
        choices = []
        for i in range(1, self.CHOICE_COUNT + 1):
            choices.append(self.ask_text(f"선택지 {i}: "))
        answer = self.ask_int(f"정답 번호 (1-{self.CHOICE_COUNT}): ", 1, self.CHOICE_COUNT)
        hint = input("힌트 (생략하려면 Enter): ").strip()

        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save_state()
        print(f"\n✅ 퀴즈가 추가되었습니다! (현재 {len(self.quizzes)}개)")

    def list_quizzes(self):
        """문제 목록을 번호와 함께 출력하고, 목록이 비어 있으면 False를 반환한다."""
        if not self.has_quizzes():
            return False

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        self.print_line("-")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        self.print_line("-")
        return True

    def delete_quiz(self):
        """목록에서 고른 퀴즈를 확인 후 삭제하고 저장한다."""
        if not self.list_quizzes():
            return

        total = len(self.quizzes)
        number = self.ask_int(f"삭제할 문제 번호 (1-{total}, 0: 취소): ", 0, total)
        if number == 0:
            print("\n삭제를 취소했습니다.")
            return

        index = number - 1
        quiz = self.quizzes[index]
        print(f"\n삭제할 문제: {quiz.question}")
        if self.ask_int("이 문제를 삭제할까요? (1: 삭제, 0: 취소): ", 0, 1) == 0:
            print("\n삭제를 취소했습니다.")
            return

        self.quizzes.pop(index)
        if not self.save_state():
            self.quizzes.insert(index, quiz)
            print("\n저장에 실패해 삭제를 취소했습니다.")
            return
        print(f"\n✅ 퀴즈를 삭제했습니다. (현재 {len(self.quizzes)}개)")

    def show_score(self):
        """최고 점수를 출력한다. 아직 푼 기록이 없으면 안내한다."""
        if self.best_score is None:
            print("\n⚠️ 아직 퀴즈를 푼 기록이 없습니다. 먼저 퀴즈를 풀어보세요.")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점 "
              f"({self.best_total}문제 중 {self.best_correct}문제 정답)")

    def show_history(self):
        """완료한 게임의 날짜, 시간, 문제 수, 점수를 최근 순서로 보여준다."""
        if not self.score_history:
            print("\n⚠️ 아직 기록된 게임이 없습니다. 먼저 퀴즈를 풀어보세요.")
            return

        print(f"\n📜 점수 기록 (총 {len(self.score_history)}판 · 최근 순)")
        self.print_line("-")
        for record in reversed(self.score_history):
            played_at = record["played_at"].replace("T", " ", 1)
            print(f"{played_at} | {record['total']}문제 | {record['score']}점")
        self.print_line("-")

    # ---------- 점수 로직 ----------

    def record_result(self, score, correct, total):
        """완료한 게임을 기록하고 최고 점수와 함께 저장한다."""
        self.score_history.append({
            "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "total": total,
            "score": score,
        })
        is_new_best = self.update_best_score(score, correct, total)
        self.save_state()
        return is_new_best

    def update_best_score(self, score, correct, total):
        """이번 점수가 최고 점수보다 높으면 갱신하고 True, 아니면 False를 반환한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            return True
        return False

    # ---------- 파일 저장/불러오기 ----------

    def save_state(self):
        """현재 상태를 UTF-8로 저장하고 성공 여부를 반환한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
            "score_history": self.score_history,
        }
        try:
            if self.STATE_FILE.exists() and not os.access(self.STATE_FILE, os.W_OK):
                raise PermissionError(f"쓰기 권한이 없습니다: {self.STATE_FILE}")

            # 기록 중 오류가 나도 기존 저장 파일이 손상되지 않도록 한다.
            with TemporaryDirectory(dir=self.STATE_FILE.parent) as directory:
                pending_file = Path(directory) / self.STATE_FILE.name
                with pending_file.open("w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                pending_file.replace(self.STATE_FILE)
        except OSError as e:
            print(f"⚠️ 데이터를 저장하지 못했습니다. ({e})")
            return False
        return True

    def load_state(self):
        """state.json에서 데이터를 불러온다. 파일이 없거나 손상됐으면 기본 퀴즈를 쓴다."""
        try:
            with open(self.STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            quizzes, best_score, best_correct, best_total, score_history = self.parse_state(data)
        except FileNotFoundError:
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            return
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            print("⚠️ 저장 파일이 손상되어 기본 퀴즈 데이터로 복구합니다.")
            self.save_state()  # 손상된 파일을 기본 데이터로 덮어써서 초기화
            return
        except OSError as e:
            print(f"⚠️ 저장 파일을 읽지 못해 기본 퀴즈로 시작합니다. ({e})")
            return

        # 모든 검사를 통과했을 때만 한꺼번에 반영한다.
        self.quizzes = quizzes
        self.best_score = best_score
        self.best_correct = best_correct
        self.best_total = best_total
        self.score_history = score_history

        score_text = "기록 없음" if best_score is None else f"{best_score}점"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {score_text})")

    def parse_state(self, data):
        """불러온 dict를 검사해 퀴즈 목록, 최고 점수 정보, 점수 기록으로 바꾼다.

        형식이 잘못되면 KeyError / TypeError / ValueError가 발생한다.
        """
        quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
        best_score = data["best_score"]
        best_correct = data.get("best_correct", 0)
        best_total = data.get("best_total", 0)

        if best_score is not None:
            if type(best_score) is not int or not 0 <= best_score <= 100:
                raise ValueError("best_score는 0~100 사이의 정수 또는 null이어야 합니다.")
        if type(best_correct) is not int or type(best_total) is not int:
            raise ValueError("best_correct, best_total은 정수여야 합니다.")
        if not 0 <= best_correct <= best_total:
            raise ValueError("best_correct는 0 이상, best_total 이하여야 합니다.")

        score_history = data.get("score_history", [])
        self.validate_score_history(score_history)
        return quizzes, best_score, best_correct, best_total, score_history

    def validate_score_history(self, history):
        """각 게임 기록의 날짜/시간, 문제 수, 점수를 검사한다."""
        if type(history) is not list:
            raise ValueError("score_history는 리스트여야 합니다.")
        for record in history:
            played_at = datetime.fromisoformat(record["played_at"])
            if played_at.tzinfo is None:
                raise ValueError("게임 기록의 시간에는 시간대 정보가 있어야 합니다.")
            if type(record["total"]) is not int or record["total"] < 1:
                raise ValueError("게임 기록의 문제 수는 1 이상의 정수여야 합니다.")
            if type(record["score"]) is not int or not 0 <= record["score"] <= 100:
                raise ValueError("게임 기록의 점수는 0~100 사이의 정수여야 합니다.")

    # ---------- 실행 ----------

    def run(self):
        """저장된 데이터를 불러온 뒤, 메뉴를 반복해서 보여주고 선택한 기능을 실행한다."""
        try:
            self.load_state()
            while True:
                self.show_menu()
                choice = self.ask_int("선택: ", self.MENU_PLAY, self.MENU_HISTORY)

                if choice == self.MENU_PLAY:
                    self.play_quiz()
                elif choice == self.MENU_ADD:
                    self.add_quiz()
                elif choice == self.MENU_LIST:
                    self.list_quizzes()
                elif choice == self.MENU_SCORE:
                    self.show_score()
                elif choice == self.MENU_DELETE:
                    self.delete_quiz()
                elif choice == self.MENU_HISTORY:
                    self.show_history()
                else:
                    self.save_state()
                    print("\n👋 게임을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되어 저장 후 프로그램을 종료합니다.")
            self.save_state()
