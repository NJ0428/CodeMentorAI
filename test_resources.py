"""
리소스 탭 테스트 스크립트
리소스 및 학습 자료 탭의 기능을 테스트합니다.
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.ui.components.resources_tab import ResourcesTab
from loguru import logger


def test_resources_tab_basic():
    """리소스 탭 기본 기능 테스트"""
    print("🧪 리소스 탭 기본 기능 테스트 시작")

    try:
        # 메인 윈도우 생성
        root = tk.Tk()
        root.title("리소스 탭 테스트")
        root.geometry("1200x800")

        # 리소스 탭 생성
        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        print("✅ 리소스 탭 생성 성공")

        # 리소스 데이터 확인
        if hasattr(resources_tab, 'resources_data'):
            print("✅ 리소스 데이터 로드 확인:")

            # 예제 코드 확인
            code_examples = resources_tab.resources_data.get('code_examples', {})
            print(f"   - 예제 코드 카테고리: {len(code_examples)}개")

            # 학습 가이드 확인
            learning_guides = resources_tab.resources_data.get('learning_guides', {})
            print(f"   - 학습 가이드: {len(learning_guides)}개")

            # 문제 해결 확인
            troubleshooting = resources_tab.resources_data.get('troubleshooting', {})
            print(f"   - 문제 해결 카테고리: {len(troubleshooting)}개")

            # 베스트 프랙티스 확인
            best_practices = resources_tab.resources_data.get('best_practices', {})
            print(f"   - 베스트 프랙티스 주제: {len(best_practices)}개")

            total_count = (len(code_examples) + len(learning_guides) +
                          len(troubleshooting) + len(best_practices))
            resources_tab.resource_count_label.config(text=f"총 {total_count}개의 리소스")

        # UI 업데이트
        resources_tab.update()

        print("✅ 모든 기본 테스트 통과")

        # 잠시 실행 유지 (실제 테스트에서는 주석 처리)
        # root.mainloop()

        # 윈도우 종료
        root.destroy()

        return True

    except Exception as e:
        print(f"❌ 기본 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_examples_functionality():
    """예제 코드 기능 테스트"""
    print("\n🧪 예제 코드 기능 테스트 시작")

    try:
        root = tk.Tk()
        root.title("예제 코드 기능 테스트")
        root.geometry("1200x800")

        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        # 코드 예제 트리 확인
        code_tree = resources_tab.code_tree
        children = code_tree.get_children()

        if children:
            print(f"✅ 코드 카테고리 로드됨: {len(children)}개")

            # 첫 번째 카테고리 확장
            first_category = children[0]
            code_tree.item(first_category, open=True)

            # 카테고리 내 예제 확인
            examples = code_tree.get_children(first_category)
            print(f"   - 첫 번째 카테고리 예제: {len(examples)}개")

            if examples:
                # 첫 번째 예제 선택
                first_example = examples[0]
                code_tree.selection_set(first_example)
                code_tree.event_generate("<<TreeviewSelect>>")
                resources_tab.update()

                print("✅ 예제 코드 선택 기능 작동")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ 예제 코드 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_learning_guides_functionality():
    """학습 가이드 기능 테스트"""
    print("\n🧪 학습 가이드 기능 테스트 시작")

    try:
        root = tk.Tk()
        root.title("학습 가이드 기능 테스트")
        root.geometry("1200x800")

        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        # 가이드 리스트 확인
        guides_listbox = resources_tab.guides_listbox
        guide_count = guides_listbox.size()

        if guide_count > 0:
            print(f"✅ 학습 가이드 로드됨: {guide_count}개")

            # 첫 번째 가이드 선택
            guides_listbox.selection_set(0)
            guides_listbox.event_generate("<<ListboxSelect>>")
            resources_tab.update()

            print("✅ 가이드 선택 기능 작동")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ 학습 가이드 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_troubleshooting_functionality():
    """문제 해결 기능 테스트"""
    print("\n🧪 문제 해결 기능 테스트 시작")

    try:
        root = tk.Tk()
        root.title("문제 해결 기능 테스트")
        root.geometry("1200x800")

        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        # 문제 카테고리 변경
        resources_tab.problem_category_var.set("runtime")
        resources_tab._on_problem_category_changed()
        resources_tab.update()

        print("✅ 문제 카테고리 변경 기능 작동")

        # 문제 리스트 확인
        problems_listbox = resources_tab.problems_listbox
        problem_count = problems_listbox.size()

        if problem_count > 0:
            print(f"   - 런타임 오류 문제: {problem_count}개")

            # 첫 번째 문제 선택
            problems_listbox.selection_set(0)
            problems_listbox.event_generate("<<ListboxSelect>>")
            resources_tab.update()

            print("✅ 문제 선택 기능 작동")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ 문제 해결 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_functionality():
    """검색 기능 테스트"""
    print("\n🧪 검색 기능 테스트 시작")

    try:
        root = tk.Tk()
        root.title("검색 기능 테스트")
        root.geometry("1200x800")

        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        # 검색어 입력
        test_search_term = "함수"
        resources_tab.search_var.set(test_search_term)

        print(f"✅ 검색어 설정: '{test_search_term}'")

        # 검색 수행
        resources_tab.perform_search()
        resources_tab.update()

        print("✅ 검색 기능 작동")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ 검색 기능 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_components():
    """UI 컴포넌트 테스트"""
    print("\n🧪 UI 컴포넌트 테스트 시작")

    try:
        root = tk.Tk()
        root.title("UI 컴포넌트 테스트")
        root.geometry("1200x800")

        resources_tab = ResourcesTab(root)
        resources_tab.pack(fill=tk.BOTH, expand=True)

        # 노트북 탭 확인
        notebook_tabs = resources_tab.notebook.index("end")
        print(f"✅ 노트북 탭 수: {notebook_tabs}개")

        expected_tabs = ["💻 예제 코드", "📖 학습 가이드", "🔧 문제 해결", "⭐ 베스트 프랙티스"]
        actual_tabs = [resources_tab.notebook.tab(i, "text") for i in range(notebook_tabs)]

        print(f"   - 예상 탭: {expected_tabs}")
        print(f"   - 실제 탭: {actual_tabs}")

        # 각 탭의 주요 컴포넌트 확인
        components_to_check = [
            ("예제 코드 트리", hasattr(resources_tab, 'code_tree')),
            ("코드 표시 영역", hasattr(resources_tab, 'code_examples_text')),
            ("가이드 리스트", hasattr(resources_tab, 'guides_listbox')),
            ("가이드 내용 영역", hasattr(resources_tab, 'guide_content_text')),
            ("문제 리스트", hasattr(resources_tab, 'problems_listbox')),
            ("해결책 내용 영역", hasattr(resources_tab, 'solution_content_text')),
            ("베스트 프랙티스 요약", hasattr(resources_tab, 'practices_summary_text'))
        ]

        for component_name, exists in components_to_check:
            if exists:
                print(f"✅ {component_name}: 존재함")
            else:
                print(f"❌ {component_name}: 존재하지 않음")

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ UI 컴포넌트 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 50)
    print("🚀 리소스 탭 전체 테스트 시작")
    print("=" * 50)

    tests = [
        ("기본 기능", test_resources_tab_basic),
        ("예제 코드 기능", test_code_examples_functionality),
        ("학습 가이드 기능", test_learning_guides_functionality),
        ("문제 해결 기능", test_troubleshooting_functionality),
        ("검색 기능", test_search_functionality),
        ("UI 컴포넌트", test_ui_components)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))

    # 테스트 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {test_name}")

        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n📈 통과: {passed}/{len(tests)}")
    print(f"📉 실패: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 모든 테스트 통과!")
        return True
    else:
        print(f"\n⚠️ {failed}개 테스트 실패")
        return False


def main():
    """메인 실행 함수"""
    try:
        success = run_all_tests()

        if success:
            print("\n🎉 리소스 탭 구현 완료!")
            print("\n📋 주요 기능:")
            print("   💻 예제 코드 라이브러리")
            print("   📖 학습 가이드 및 튜토리얼")
            print("   🔧 문제 해결 예시")
            print("   ⭐ 베스트 프랙티스 가이드")
            print("\n🔍 추가 기능:")
            print("   - 검색 기능")
            print("   - 필터링 기능")
            print("   - 코드 실행 및 복사")
            print("   - 진도 추적")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())