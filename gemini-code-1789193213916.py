import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서·논술형 자동 채점 시스템", page_icon="📝", layout="wide"
)

st.title("📝 서·논술형 답안 자동 채점 시스템")
st.caption(
    "1~3세트 문항별 필수 키워드, 오개념 방지, 설명 방법 특성, 결론 방향을 종합적으로 검증합니다."
)

# ------------------------------------------------------------------------------
# 채점 로직 함수 모음
# ------------------------------------------------------------------------------


def evaluate_set1_q1(a1, a2, a3):
    score = 0
    feedback = []

    # (1) 과제 특성 (허용 범위: 쉬운, 친숙, 노력이 적은)
    if any(k in a1 for k in ["쉬운", "친숙", "노력이 적", "부담 없는"]):
        score += 2
        feedback.append("(1) 정답 (쉬운 과제 특성 인지)")
    else:
        feedback.append(
            "(1) 오답/감점: '쉬운 과제' 또는 '친숙한 과목'의 의미가 포함되어야 합니다."
        )

    # (2) 학습 방법 (허용 범위: 혼자, 차분, 집중)
    if any(k in a2 for k in ["혼자", "독립"]) and any(
        k in a2 for k in ["집중", "연습", "차분"]
    ):
        score += 2
        feedback.append("(2) 정답 (혼자 집중하는 환경 인지)")
    else:
        feedback.append(
            "(2) 오답/감점: '혼자'와 '집중/차분'의 개념이 모두 포함되어야 합니다."
        )

    # (3) 관련 용어 (용어 엄격성: '사회적 억제' 정확히 명시 필요)
    if "사회적 억제" in a3.replace(" ", ""):
        score += 2
        feedback.append("(3) 정답 ('사회적 억제' 정확히 기재)")
    elif "사회적촉진" in a3.replace(" ", ""):
        feedback.append(
            "(3) 오답 [오개념]: '사회적 촉진'은 쉬운 과제에 해당하므로 오답 처리됩니다."
        )
    else:
        feedback.append(
            "(3) 오답: 정확한 용어인 '사회적 억제'를 기재해야 합니다."
        )

    return score, feedback


def evaluate_set1_q2(m1_type, ans1, m2_type, ans2):
    score = 0
    feedback = []

    # 오개념 및 결론 방향 검증용 키워드
    easy_keywords = ["쉬운", "친숙", "도서관", "커피숍", "모임", "함께"]
    hard_keywords = ["어려운", "도전", "혼자", "집중", "차분"]

    # (1) 문장 검증
    # 결론 방향 및 개념 혼동 확인 (쉬운 과제에 혼자 집중을 연결했는지 체크)
    if any(k in ans1 for k in easy_keywords):
        if "혼자" in ans1 and "함께" not in ans1:
            feedback.append(
                "(1) 오답 [오개념]: 쉬운 과제 특성에 '혼자 집중'이라는 어려운 과제 전략을 적용했습니다."
            )
        else:
            # 선택한 설명 방법의 특성 반영 여부 검증
            if m1_type == "예시" and any(
                k in ans1 for k in ["예를 들어", "예컨대", "커피숍", "도서관"]
            ):
                score += 3
                feedback.append(
                    "(1) 정답: 쉬운 과제 전략 설명 + '예시' 설명 방법의 특성이 드러남."
                )
            elif m1_type == "인과" and any(
                k in ans1 for k in ["때문에", "따라서", "하므로", "결과"]
            ):
                score += 3
                feedback.append(
                    "(1) 정답: 쉬운 과제 전략 설명 + '인과' 설명 방법의 특성이 드러남."
                )
            elif m1_type == "대조/비교" and any(
                k in ans1 for k in ["반면", "달리", "과 달리", "비해"]
            ):
                score += 3
                feedback.append(
                    "(1) 정답: 쉬운 과제 전략 설명 + '대조' 설명 방법의 특성이 드러남."
                )
            else:
                score += 1.5
                feedback.append(
                    f"(1) 부분 점수: 결론 방향은 맞으나 선택한 설명 방법('{m1_type}')의 표현 특성이 문장에 부족합니다."
                )
    else:
        feedback.append(
            "(1) 오답: 과제 난이도에 따른 결론 방향(쉬운 과제 전략)이 드러나지 않았습니다."
        )

    # (2) 문장 검증 (중복 설명 방법 금지)
    if m1_type == m2_type:
        feedback.append(
            "(2) 오답 [조건 위배]: (1)과 (2)에서 동일한 설명 방법을 중복 선택했습니다."
        )
    elif any(k in ans2 for k in hard_keywords):
        if "모임" in ans2 or "함께" in ans2:
            feedback.append(
                "(2) 오답 [오개념]: 어려운 과제 특성에 '함께/모임'이라는 쉬운 과제 전략을 적용했습니다."
            )
        else:
            if m2_type == "예시" and any(
                k in ans2 for k in ["예를 들어", "예컨대", "혼자 공부"]
            ):
                score += 3
                feedback.append(
                    "(2) 정답: 어려운 과제 전략 설명 + '예시' 설명 방법의 특성이 드러남."
                )
            elif m2_type == "인과" and any(
                k in ans2 for k in ["때문에", "따라서", "하므로", "결과"]
            ):
                score += 3
                feedback.append(
                    "(2) 정답: 어려운 과제 전략 설명 + '인과' 설명 방법의 특성이 드러남."
                )
            elif m2_type == "대조/비교" and any(
                k in ans2 for k in ["반면", "달리", "과 달리", "비해"]
            ):
                score += 3
                feedback.append(
                    "(2) 정답: 어려운 과제 전략 설명 + '대조' 설명 방법의 특성이 드러남."
                )
            else:
                score += 1.5
                feedback.append(
                    f"(2) 부분 점수: 결론 방향은 맞으나 선택한 설명 방법('{m2_type}')의 표현 특성이 문장에 부족합니다."
                )
    else:
        feedback.append(
            "(2) 오답: 과제 난이도에 따른 결론 방향(어려운 과제 전략)이 드러나지 않았습니다."
        )

    return score, feedback


def evaluate_set1_q3(vis_plan, vis_eff, aud_plan, aud_eff):
    score = 0
    feedback = []

    # 시각 요소 (어려운 과제 -> 혼자/독립 공간)
    if any(k in vis_plan for k in ["혼자", "독립", "방", "책상"]):
        score += 1.5
        if any(k in vis_eff for k in ["혼자", "집중", "방해 없이"]):
            score += 1.5
            feedback.append("(1) 시각 요소 및 효과: 완전 정답 (지문 근거 반영)")
        else:
            score += 0.5
            feedback.append(
                "(1) 시각 요소 효과 감점: '혼자 집중하는 환경의 필요성'이라는 지문 근거가 명시되어야 합니다."
            )
    else:
        feedback.append(
            "(1) 시각 요소 오답: 어려운 과제에 맞는 연출(혼자 있는 모습)이 부족합니다."
        )

    # 청각 요소 (정적, 잔잔함)
    if any(k in aud_plan for k in ["조용", "잔잔", "없애", "최소", "초침"]):
        score += 1.5
        if any(k in aud_eff for k in ["집중", "차분", "사회적 억제"]):
            score += 1.5
            feedback.append("(2) 청각 요소 및 효과: 완전 정답 (지문 근거 반영)")
        else:
            score += 0.5
            feedback.append(
                "(2) 청각 요소 효과 감점: '차분히 집중할 수 있는 분위기'라는 지문 근거가 필요합니다."
            )
    else:
        feedback.append(
            "(2) 청각 요소 오답: 주변 소음을 줄이거나 잔잔한 소리로 연출하는 기획이 필요합니다."
        )

    return score, feedback


# ------------------------------------------------------------------------------
# UI 레이아웃 구성
# ------------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["[세트 1] 과제 난이도", "[세트 2] 정전기 특성", "[세트 3] AI 예술"])

# ==============================================================================
# [세트 1] UI
# ==============================================================================
with tab1:
    st.subheader("[세트 1] 과제 난이도와 학습 환경 (2~3쪽)")

    st.markdown("---")
    st.markdown("#### **[서·논술형 1] 요약 표 채우기**")
    col1, col2, col3 = st.columns(3)
    with col1:
        s1_q1_a1 = st.text_input("(1) 과제의 특성 (사회적 촉진 관련)", key="s1_q1_1")
    with col2:
        s1_q1_a2 = st.text_input(
            "(2) 지나치게 어려운 과제 수행 방법", key="s1_q1_2"
        )
    with col3:
        s1_q1_a3 = st.text_input("(3) 관련 심리 현상 용어", key="s1_q1_3")

    if st.button("세트 1 - 문항 1 채점"):
        s, fb = evaluate_set1_q1(s1_q1_a1, s1_q1_a2, s1_q1_a3)
        st.metric("획득 점수", f"{s} / 6 점")
        for item in fb:
            st.write(f"- {item}")

    st.markdown("---")
    st.markdown("#### **[서·논술형 2] 설명문 작성**")
    st.info(
        "주어진 첫 문장: '과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.'"
    )

    col1, col2 = st.columns(2)
    with col1:
        m1_select = st.selectbox(
            "(1) 문장 사용 설명 방법 선택", ["예시", "대조/비교", "인과"], key="m1_s"
        )
        s1_q2_a1 = st.text_area("(1) 문장 작성", key="s1_q2_1")
    with col2:
        m2_select = st.selectbox(
            "(2) 문장 사용 설명 방법 선택", ["대조/비교", "인과", "예시"], key="m2_s"
        )
        s1_q2_a2 = st.text_area("(2) 문장 작성", key="s1_q2_2")

    with st.expander("💡 선택지별 모범 답안 확인하기"):
        st.markdown("""
        * **[선택지 A: 예시 + 대조]**
          * (1) 쉬운 과제를 할 때는 커피숍이나 도서관에서 다른 사람들과 함께 공부하는 것이 좋다. **(예시)**
          * (2) 반면에 지나치게 어려운 과제는 익숙해질 때까지 차분하게 혼자 집중해야 한다. **(대조)**
        * **[선택지 B: 대조 + 인과]**
          * (1) 쉬운 과제는 타인과 함께할 때 효율이 높지만, 어려운 과제는 혼자할 때 효율이 높다. **(대조)**
          * (2) 따라서 과제의 난이도를 고려하여 혼자 공부할지 모임을 만들지 결정해야 한다. **(인과)**
        """)

    if st.button("세트 1 - 문항 2 채점"):
        s, fb = evaluate_set1_q2(m1_select, s1_q2_a1, m2_select, s1_q2_a2)
        st.metric("획득 점수", f"{s} / 6 점")
        for item in fb:
            st.write(f"- {item}")

    st.markdown("---")
    st.markdown("#### **[서·논술형 3] 영상 기획안 (장면 2 연출)**")
    c1, c2 = st.columns(2)
    with c1:
        s1_q3_vp = st.text_input("(1) 시각 요소(Ⓐ) 연출 계획", key="s1_q3_vp")
        s1_q3_ve = st.text_area("시각 요소(Ⓐ)의 효과 및 근거", key="s1_q3_ve")
    with c2:
        s1_q3_ap = st.text_input("(2) 청각 요소(Ⓑ) 연출 계획", key="s1_q3_ap")
        s1_q3_ae = st.text_area("청각 요소(Ⓑ)의 효과 및 근거", key="s1_q3_ae")

    if st.button("세트 1 - 문항 3 채점"):
        s, fb = evaluate_set1_q3(s1_q3_vp, s1_q3_ve, s1_q3_ap, s1_q3_ae)
        st.metric("획득 점수", f"{s} / 6 점")
        for item in fb:
            st.write(f"- {item}")

# ==============================================================================
# [세트 2] UI
# ==============================================================================
with tab2:
    st.subheader("[세트 2] 정전기와 실생활 전기의 차이 (4~5쪽)")

    st.markdown("#### **[서·논술형 1] 요약 표 채우기**")
    c1, c2, c3 = st.columns(3)
    with c1:
        s2_q1_a1 = st.text_input(
            " 정전기의 물 상태 비유 (필수: 높은 곳)", key="s2_q1_1"
        )
    with c2:
        s2_q1_a2 = st.text_input(" 정전기 전하의 상태", key="s2_q1_2")
    with c3:
        s2_q1_a3 = st.text_input(" 정전기의 위험성 여부", key="s2_q1_3")

    if st.button("세트 2 - 문항 1 채점"):
        s = 0
        fb = []
        # (1) 높은 곳 필수 검증
        if "높은 곳" in s2_q1_a1 and "고여" in s2_q1_a1:
            s += 2
            fb.append(
                "(1) 정답 ('높은 곳'과 '고여 있는 물' 비유가 완벽함)"
            )
        elif "고여" in s2_q1_a1:
            s += 1
            fb.append(
                "(1) 부분 점수 [오개념/특성 누락]: 정전기의 높은 전압 특성을 나타내는 '높은 곳'이 누락되었습니다."
            )
        else:
            fb.append(
                "(1) 오답: '높은 곳에 고여 있는 물'이 들어가야 합니다."
            )

        # (2) 전하 상태 (이동하지 않음/머물러 있음)
        if any(k in s2_q1_a2 for k in ["이동하지", "머물", "멈춰", "움직이지"]):
            s += 2
            fb.append("(2) 정답 (전하가 머물러 있는 상태 인지)")
        else:
            fb.append(
                "(2) 오답: '전하가 이동하지 않고 머물러 있다'는 내용이 필요합니다."
            )

        # (3) 위험성 (위험하지 않음)
        if any(k in s2_q1_a3 for k in ["위험하지 않", "피해가 없", "위험 없음"]):
            s += 2
            fb.append("(3) 정답 (위험하지 않다는 결론 방향 정답)")
        elif "위험하" in s2_q1_a3:
            fb.append(
                "(3) 오답 [오개념]: 정전기는 전압이 높아도 전하가 머물러 있어 위험하지 않습니다."
            )
        else:
            fb.append(
                "(3) 오답: '위험하지 않음' 또는 '피해가 없음'이 기술되어야 합니다."
            )

        st.metric("획득 점수", f"{s} / 6 점")
        for item in fb:
            st.write(f"- {item}")

    st.markdown("---")
    st.markdown("#### **[서·논술형 2] 모범 답안 선택지 가이드**")
    with st.expander("💡 선택지별 모범 답안 확인하기"):
        st.markdown("""
        * **[선택지 A: 비교/대조 + 인과]**
          * (1) 실생활 전기는 흐르는 물과 같지만 정전기는 높은 곳에 고여 있는 물과 같다. **(비교와 대조)**
          * (2) 따라서 정전기는 전압이 높더라도 전하가 머물러 있어 위험하지 않다. **(인과)**
        * **[선택지 B: 정의 + 대조]**
          * (1) 정전기란 전하가 정지 상태로 머물러 있어 변화하지 않는 전기를 의미한다. **(정의)**
          * (2) 이와 달리 실생활 전기는 전하가 계속 이동하며 흐른다는 차이가 있다. **(대조)**
        """)

# ==============================================================================
# [세트 3] UI
# ==============================================================================
with tab3:
    st.subheader("[세트 3] AI 그림과 인간 예술의 가치 (6~7쪽)")

    st.markdown("#### **[서·논술형 1] 요약 표 채우기**")
    c1, c2, c3 = st.columns(3)
    with c1:
        s3_q1_a1 = st.text_input(" AI 올림픽 경기 비유", key="s3_q1_1")
    with c2:
        s3_q1_a2 = st.text_input(
            " 예술 여부 판정 및 근거", key="s3_q1_2"
        )
    with c3:
        s3_q1_a3 = st.text_input(" AI 그림의 예술적 가치", key="s3_q1_3")

    if st.button("세트 3 - 문항 1 채점"):
        s = 0
        fb = []
        # (1) 비유 (로봇, 피겨 스케이팅)
        if "로봇" in s3_q1_a1 and "피겨" in s3_q1_a1:
            s += 2
            fb.append("(1) 정답 (로봇 피겨 스케이팅 비유 정확함)")
        else:
            fb.append(
                "(1) 오답/감점: '로봇이 완벽하게 해내는 피겨 스케이팅'이 명시되어야 합니다."
            )

        # (2) 예술 인정 여부 (근거 필수: 감정/철학 부재)
        if any(k in s3_q1_a2 for k in ["감정", "철학", "이야기"]) and any(
            k in s3_q1_a2 for k in ["아니다", "어렵다", "없다"]
        ):
            s += 2
            fb.append(
                "(2) 정답 (감정/철학의 부재 근거 및 결론 방향 정답)"
            )
        else:
            fb.append(
                "(2) 오답/감점: '감정이나 철학이 없어서 예술로 보기 어렵다'는 근거와 결론이 함께 써야 합니다."
            )

        # (3) 가치 (변화, 범주 확장)
        if any(k in s3_q1_a3 for k in ["변화", "확장", "상징"]):
            s += 2
            fb.append("(3) 정답 (예술 범주 확장 및 변화 가치 인지)")
        else:
            fb.append(
                "(3) 오답: '기존 미술계의 변화' 또는 '예술 범주의 확장'이라는 가치가 명시되어야 합니다."
            )

        st.metric("획득 점수", f"{s} / 6 점")
        for item in fb:
            st.write(f"- {item}")

    st.markdown("---")
    st.markdown("#### **[서·논술형 2] 모범 답안 선택지 가이드**")
    with st.expander("💡 선택지별 모범 답안 확인하기"):
        st.markdown("""
        * **[선택지 A: 대조 + 인과]**
          * (1) 인간 작품은 감정과 경험이 담겨 있지만 AI 그림은 독자적인 철학이 없다. **(대조)**
          * (2) 따라서 AI 그림은 예술로 보긴 힘들지만 범주를 확장하는 가치가 있다. **(인과)**
        * **[선택지 B: 예시 + 대조]**
          * (1) 예를 들어 「에드몽 드 벨라미」는 알고리즘으로 그려진 대표적인 AI 그림이다. **(예시)**
          * (2) 이 작품은 인간의 예술과 달리 작가의 삶의 경험이나 관점이 담겨 있지 않다. **(대조)**
        """)