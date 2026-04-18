import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import re

def fake_visitor_widget():
    import random
    from datetime import datetime
    today_str = datetime.now().strftime("%Y%m%d")
    random.seed(int(today_str))
    daily_target = random.randint(240, 330)
    
    now = datetime.now()
    total_min = now.hour * 60 + now.minute
    current_v = max(1, int((daily_target * total_min) / 1440))
    
    # 디자이너의 감각을 살린 애니메이션 포함 UI
    st.markdown(f"""
        <style>
            @keyframes blink {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
                100% {{ opacity: 1; }}
            }}
            .live-dot {{
                color: #d9534f;
                font-weight: bold;
                animation: blink 1.5s infinite;
                margin-right: 5px;
            }}
        </style>
        <div style="
            background-color: #f8f9fa;
            border-bottom: 2px solid #1a1a1a;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-family: 'Pretendard', sans-serif;
        ">
            <div style="font-size: 14px; color: #333; font-weight: 600;">
                <span class="live-dot">●</span> LIVE <span style="margin-left:5px; color:#666; font-weight:400;">실시간 빌드 상담 현황</span>
            </div>
            <div style="font-size: 18px; font-weight: 800; color: #000;">
                {current_v} <span style="font-size: 13px; font-weight: 400; color: #777;">명 접속 중</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 실행 부분 ---
# GA 스크립트 실행 직후에 배치하세요.
fake_visitor_widget() 

# 이후 기존 코드(df 로드 및 탭 생성)가 이어집니다.
# df = load_data()
# t_gal, t_comp, t_adm = st.tabs([" 맞춤 사양 갤러리", ...])

# --- 1. 환경 설정 및 연결 ---
st.set_page_config(page_title="컴선생 출고 컴퓨터 갤러리", layout="wide")
st.markdown("""
    <style>
        /* 스트림릿 기본 메뉴바, 헤더, 툴바 싹 다 강제 숨김 */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stHeader"] {visibility: hidden !important;}
        [data-testid="stDecoration"] {visibility: hidden !important;}
        
        /* 여백 조정 */
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
""", unsafe_allow_html=True)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 🕵️‍♂️ 구글 애널리틱스 CCTV 배선 (새로운 ID로 교체 완료) ---
ga_id = "G-PBEE9318GB" 

ga_js = f"""
<script>
    var script = window.parent.document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id={ga_id}';
    window.parent.document.head.appendChild(script);

    var script2 = window.parent.document.createElement('script');
    script2.innerHTML = `
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{ga_id}');
    `;
    window.parent.document.head.appendChild(script2);
</script>
"""
st.components.v1.html(ga_js, height=0)



# --- 2. 세션 상태 관리 ---
if 'search_cpu' not in st.session_state: st.session_state.search_cpu = "전체"
if 'search_gpu' not in st.session_state: st.session_state.search_gpu = "전체"
if 'search_ram' not in st.session_state: st.session_state.search_ram = "전체"
if 'search_active' not in st.session_state: st.session_state.search_active = False
if 'view_history' not in st.session_state: st.session_state.view_history = []
if 'search_id' not in st.session_state: st.session_state.search_id = ""
if 'search_id' not in st.session_state: st.session_state.search_id = ""
if 'search_category' not in st.session_state: st.session_state.search_category = None
# --- 3. 함수 정의 구역 ---
def kakao_button():
    st.markdown("""
        <a href="https://open.kakao.com/o/seyfAN0c" target="_blank" style="text-decoration: none;">
            <div style="background-color: #FEE500; color: #3A1D1D; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; margin: 10px 0;">
                 컴선생 실시간 카톡 상담하기
            </div>
        </a>
    """, unsafe_allow_html=True)

def add_to_history(pc_id):
    now = datetime.now()
    st.session_state.view_history = [h for h in st.session_state.view_history if now - h['time'] < timedelta(minutes=15)]
    if pc_id not in [h['id'] for h in st.session_state.view_history]:
        st.session_state.view_history.insert(0, {'id': pc_id, 'time': now})
    st.session_state.view_history = st.session_state.view_history[:5]

def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl="3600")
        if 'ID' in df.columns:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        for col in ['현금가', '카드가']:
            if col in df.columns:
                # 콤마(,) 등이 포함되어 있을 경우를 대비해 처리 후 변환
                df[col] = pd.to_numeric(df[col].replace('[^0-9]', '', regex=True), errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def get_embed_url(url):
    if not url or pd.isna(url): return None
    v_match = re.search(r"(?:shorts/|v=|\/)([0-9A-Za-z_-]{11})", str(url))
    if v_match: return f"https://www.youtube.com/embed/{v_match.group(1)}"
    return None

def render_history_ui(df, prefix):
    if st.session_state.view_history:
        st.write("🕒 **최근 15분간 본 사양 (클릭 시 이동):**")
        h_cols = st.columns(10)
        for i, h in enumerate(st.session_state.view_history):
            if h_cols[i].button(f"#{h['id']}", key=f"{prefix}_{h['id']}", use_container_width=True):
                t = df[df['ID'] == h['id']].iloc[0]
                
                # 🚀 수리 완료: search_id 값도 클릭한 번호로 함께 바꿔줍니다.
                st.session_state.update({
                    "search_id": str(h['id']), 
                    "search_cpu": t['CPU'], 
                    "search_gpu": t['GPU'], 
                    "search_ram": t['메모리'], 
                    "search_active": True
                })
                st.rerun()

def display_pc_card(df_to_show, is_expanded=False):
    if st.session_state.search_active:
        if st.button(" 검색 목록 돌아가기", key="top_back", use_container_width=True):
            st.session_state.search_active = False
            st.rerun()

    for idx, row in df_to_show.iterrows():
        b_no = row.get('ID', idx + 1)
        header = f"🆔 #{b_no} | 💻 {row['CPU']} + {row['GPU']} + {row.get('메모리','-')} | 📅 {row['날짜']} 출고"
        with st.expander(header, expanded=is_expanded):
            add_to_history(b_no)
            c1, c2, c3 = st.columns([0.3, 0.4, 0.3])
            with c1:
                st.write("###  조립 갤러리")
                urls = [u.strip() for u in str(row.get('사진URL들','')).split('\n') if u.strip()]
                if urls:
                    for u in urls: st.image(u, use_container_width=True)
                else: st.info(" 사진 준비 중")
            with c2:
                parts = "".join([f"<tr><td style='padding:8px; border-bottom:1px dashed #eee; font-size:13px;'>{p}</td></tr>" for p in str(row.get('다나와견적','')).split('\n') if p.strip()])
                st.components.v1.html(f"""
                <div style="background:white; color:black; padding:20px; border:1px solid #ddd; border-radius:8px; font-family:'Malgun Gothic';">
                    <div style="text-align:center; border-bottom:2px solid black; padding-bottom:10px;">
                        <h2 style="margin:0; font-size:18px;">매출 내역 (#{b_no})</h2>
                        <div style="position:absolute; right:10px; top:10px; border:2px solid #d9534f; color:#d9534f; padding:2px; font-weight:bold; font-size:10px;">컴선생 인</div>
                    </div>
                    <div style="margin-top:10px; font-size:12px; line-height:1.6;">
                        <b>상호:</b> 컴선생 | <b>사업자:</b> 446-13-02183<br>
                        <b>출고일자:</b> {row.get('날짜', '')}
                    </div>
                    <table style="width:100%; margin-top:10px; border-collapse:collapse;">{parts}</table>
                    <div style="margin-top:15px; text-align:right; font-size:14px; border-top:2px solid black; padding-top:10px;">
                        <b>현금가:</b> <span style="color:#d9534f; font-weight:bold;">{int(row.get('현금가',0)):,}원</span><br>
                        <b>카드가:</b> <span style="color:#d9534f; font-weight:bold;">{int(row.get('카드가',0)):,}원</span>
                    </div>
                </div>""", height=450, scrolling=True)
            with c3:
                st.write("###  테스트 결과")
                st.info(row.get('테스트상세', '준비 중'))
                st.divider()
                embed = get_embed_url(row.get('유튜브URL', ''))
                if embed: st.components.v1.html(f'<iframe width="100%" height="350" src="{embed}" frameborder="0" allowfullscreen style="border-radius:10px;"></iframe>', height=360)

# --- 4. 메인 로직 및 레이아웃 ---
df = load_data()
render_history_ui(df, "top")

# 여기서 탭이 생성됩니다. 이 시점 이후부터 with t_gal을 사용할 수 있습니다.
t_gal, t_comp, t_adm = st.tabs([" 맞춤 사양 갤러리", " 성능 비교하기", " 사장님 관리"])

with st.sidebar:
    st.write("###  조립 문의")
    kakao_button()
    st.divider()

with t_gal:
    st.markdown('<div style="background:#f0f7ff; padding:10px; border-radius:10px; border-left:5px solid #007bff; margin-bottom:15px; font-size:13px; color:#333;">⚠️ <b>공지:</b> 게임은 업데이트 될때마다 수시로 요구 사양이 변합니다. 오래된 과거 데이터 말고 최신 데이터로 성능 확인하세요!</div>', unsafe_allow_html=True)
    
    if not df.empty:
        with st.container(border=True):
            # 4개 컬럼 (번호 검색 포함)
            c_id, c1, c2, c3 = st.columns([0.15, 0.3, 0.3, 0.25])
            
            s_id = c_id.text_input("번호(#)", value=st.session_state.search_id, placeholder="예: 15")
            opts = lambda col: ["전체"] + sorted(df[col].dropna().astype(str).unique().tolist())
            s_cpu = c1.selectbox("CPU", opts('CPU'), index=opts('CPU').index(st.session_state.search_cpu) if st.session_state.search_cpu in opts('CPU') else 0)
            s_gpu = c2.selectbox("GPU", opts('GPU'), index=opts('GPU').index(st.session_state.search_gpu) if st.session_state.search_gpu in opts('GPU') else 0)
            s_ram = c3.selectbox("RAM", opts('메모리'), index=opts('메모리').index(st.session_state.search_ram) if st.session_state.search_ram in opts('메모리') else 0)
            
            bc1, bc2 = st.columns(2)
            if bc1.button("🔍 최신 견적 검색", use_container_width=True, type="primary"):
                # 번호를 입력했거나, 최소 2개 사양을 선택했을 때만 검색 활성화
                if s_id.strip() or sum([s_cpu!="전체", s_gpu!="전체", s_ram!="전체"]) >= 2:
                    st.session_state.update({
                        "search_id": s_id.strip(),
                        "search_cpu": s_cpu,
                        "search_gpu": s_gpu,
                        "search_ram": s_ram,
                        "search_active": True,
                        "search_category": None
                    })
                    st.rerun()
                else:
                    st.warning("⚠️ 제품 번호를 입력하거나 최소 2개 이상의 사양을 선택해 주세요.")

            if bc2.button("🔄 초기화", use_container_width=True):
                st.session_state.update({
                    "search_id": "", "search_cpu": "전체", "search_gpu": "전체", 
                    "search_ram": "전체", "search_active": False, "search_category": None # 👈 추가
                })
                st.rerun()
            # --- 🚀 추가 구간 B: 정형화된 4대 카테고리 버튼 ---
        st.write("###  용도별 빠른 추천 (최저가순 정렬)")
        categories = ["배그 렉안걸림", "배그 렉걸림", "스팀게임", "영상편집"]
        cat_cols = st.columns(4)
        for i, cat in enumerate(categories):
            if cat_cols[i].button(cat, use_container_width=True):
                st.session_state.update({
                    "search_id": "", "search_cpu": "전체", "search_gpu": "전체", "search_ram": "전체",
                    "search_active": True, "search_category": cat
                })
                st.rerun()
    if st.session_state.search_active:
        f = df.copy()
        
        # [카테고리 클릭 시] 최저가순 정렬 적용
        if st.session_state.get("search_category"):
            cat = st.session_state.search_category
            if '카테고리' in f.columns:
                f = f[f['카테고리'].str.contains(cat, na=False)]
            f = f.sort_values('현금가', ascending=True) # 여기서 최저가 정렬 완료
            
        # [번호 직접 검색 시]
        elif st.session_state.search_id:
            f = f[f['ID'].astype(str) == st.session_state.search_id.strip()]
            
        # [일반 사양 검색 시] 최신순 정렬 적용
        else:
            if st.session_state.search_cpu != "전체": f = f[f['CPU'] == st.session_state.search_cpu]
            if st.session_state.search_gpu != "전체": f = f[f['GPU'] == st.session_state.search_gpu]
            if st.session_state.search_ram != "전체": f = f[f['메모리'] == st.session_state.search_ram]
            f = f.sort_values('날짜', ascending=False)

        if f.empty: 
            st.error("데이터 없음")
        else:
            # 핵심: 이미 위에서 정렬된 f를 그대로 사용함
            display_pc_card(f, is_expanded=(len(f)==1)) 
            st.divider()

            st.subheader(" 견적 상담이 필요하신가요? 구매 상담이 아니어도 괜찮습니다. 타사 견적의 호환성·안정성, 13년 차의 눈으로 '무료 검토' 해드립니다. ")
            kakao_button() 
            
            st.subheader(" 비용 약간 추가해서 올릴만한 견적 추천")
            cp = f['현금가'].max()
            recs = df[(df['현금가'] > cp) & (df['현금가'] <= cp + 250000)]
            if not recs.empty:
                rcs = st.columns(min(len(recs), 2))
                for i, (_, r) in enumerate(recs.sample(n=min(len(recs), 2)).iterrows()):
                    with rcs[i]:
                        with st.container(border=True):
                            st.write(f"**{r['CPU']} + {r['GPU']}**")
                            st.write(f" {int(r['현금가']):,}원")
                            
                            if st.button(f"#{r['ID']} 보러가기", key=f"rec_{r['ID']}"):
                                # 🚀 수리 완료: 여기도 search_id를 덮어씌워 줍니다.
                                st.session_state.update({
                                    "search_id": str(r['ID']), 
                                    "search_cpu": r['CPU'], 
                                    "search_gpu": r['GPU'], 
                                    "search_ram": r['메모리'], 
                                    "search_active": True
                                })
                                st.rerun()
            st.button(" 검색 목록 돌아가기", key="bottom_back", use_container_width=True)
            render_history_ui(df, "bottom")

# ==============================================================
# ✂️ 여기서부터 아래 코드를 통째로 복사해서 덮어씌우세요!
# (기존 코드의 'with t_comp:' 부터 'with t_adm:' 바로 윗줄까지 대체)
# ==============================================================

with t_comp:
    if not df.empty:
        # --- 🚀 UX 개선: 답답한 드롭다운 제거 -> 직관적인 텍스트 입력창 도입 ---
        id_input = st.text_input(" 비교할 PC 번호 입력 (최대 3개)", placeholder="예: 1 또는 1, 15, 23 (쉼표로 구분하여 입력)")
        
        valid_ids = []
        if id_input.strip():
            # 쉼표 기준으로 자르고 띄어쓰기 무시, 숫자만 쏙쏙 뽑아내기
            raw_ids = [int(x.strip()) for x in id_input.split(',') if x.strip().isdigit()]
            # 엑셀 데이터에 진짜 있는 번호만 걸러내고, 최대 3개까지만 자르기
            valid_ids = [i for i in raw_ids if i in df['ID'].values][:3]
            
        if valid_ids:
            cdf = df[df['ID'].isin(valid_ids)]
            
            # 🚀 튜닝 1: 절대 닫히지 않는 'HTML 풀-오픈 비교표' 생성
            st.markdown("###  스펙 및 성능 비교")
            
            # 테이블 헤더 조립 (최소 너비를 넉넉하게 줘서 모바일에서 찌그러지지 않게 방어)
            th_html = "<th style='padding:12px; border-bottom:2px solid #555; background:rgba(255,255,255,0.05); min-width:100px;'>항목</th>"
            for _, r in cdf.iterrows():
                th_html += f"<th style='padding:12px; border-bottom:2px solid #555; background:rgba(255,255,255,0.05); min-width:280px;'>#{r['ID']}</th>"
            
            # 테이블 본문 조립
            rows_html = ""
            items = ["CPU", "GPU", "메모리", "테스트상세"]
            for item in items:
                td_html = f"<td style='padding:12px; border-bottom:1px solid #444; font-weight:bold;'>{item}</td>"
                for _, r in cdf.iterrows():
                    val = str(r.get(item, '-'))
                    if item == "테스트상세":
                        # 💡 핵심: 엑셀 데이터를 가져올 때 엔터키(\n)를 HTML 줄바꿈(<br>)으로 강제 변환
                        val = val.replace('\n', '<br>')
                    
                    # 수직 정렬을 'top'으로 줘서 글씨가 위에서부터 깔끔하게 정렬되도록 세팅
                    td_html += f"<td style='padding:12px; border-bottom:1px solid #444; line-height:1.7; vertical-align:top;'>{val}</td>"
                rows_html += f"<tr>{td_html}</tr>"
            
            # 최종 HTML 출력 (overflow-x: auto 를 줘서 모바일 가로 스크롤 활성화)
            st.markdown(f'''
            <div style="overflow-x: auto; border: 1px solid #444; border-radius: 8px; margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; color: inherit;">
                    <thead><tr>{th_html}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            ''', unsafe_allow_html=True)
            
            st.divider()
            
            # 🚀 튜닝 2: 사진과 영상은 표 아래에 따로 배치
            st.markdown("###  갤러리 및 영상")
            cols = st.columns(len(valid_ids))
            for i, (_, r) in enumerate(cdf.iterrows()):
                with cols[i]:
                    st.success(f"#{r['ID']} 시각 자료")
                    
                    # 유튜브 영상 송출
                    embed = get_embed_url(r['유튜브URL'])
                    if embed: 
                        st.components.v1.html(f'<iframe width="100%" height="200" src="{embed}" frameborder="0"></iframe>', height=210)
                    
                    # 첫 번째 사진 송출
                    urls = [u.strip() for u in str(r.get('사진URL들','')).split('\n') if u.strip()]
                    if urls:
                        st.image(urls[0], use_container_width=True)

# ==============================================================
# ✂️ 딱 여기까지 복사하시면 됩니다.
# 이 줄 바로 밑에는 기존 사장님 코드인 'with t_adm:' (관리자 탭)이 이어지면 완벽합니다.
# ==============================================================

with t_adm:
    # 🔐 비밀번호 보안 (secrets.toml에 설정된 비번 사용)
    if st.text_input("비밀번호", type="password", key="admin_pw_input") == st.secrets["admin_password"]:
        s1, s2 = st.tabs(["🆕 등록", "🛠️ 관리"])
        
        with s1:
            with st.form("add_pc_form"):
                st.write("### 💻 새로운 출고 사양 등록")
                nid = int(df['ID'].max() + 1) if not df.empty else 1
                c1, c2 = st.columns(2)
                
                # 고유 key를 부여하여 검색창 위젯과 충돌 방지
                dt = c1.date_input("날짜", key="reg_date")
                cpu = c1.text_input("CPU", key="reg_cpu")
                gpu = c1.text_input("GPU", key="reg_gpu")
                ram = c1.text_input("RAM", key="reg_ram")
                
                # 쫀득한 가격 입력 UI (텍스트 입력 후 숫자 변환)
                cash_str = c2.text_input("현금가", placeholder="0", key="reg_cash")
                card_str = c2.text_input("카드가", placeholder="0", key="reg_card")
                cash = int(cash_str) if cash_str.isdigit() else 0
                card = int(card_str) if card_str.isdigit() else 0

                # 🎯 정형화된 4대 카테고리 선택
                fixed_cat_list = ["배그 렉안걸림", "배그 렉걸림", "스팀게임", "영상편집"]
                selected_cats = st.multiselect("해당하는 용도 선택 (중복 가능)", fixed_cat_list, key="reg_cats")
                cat_str = ", ".join(selected_cats)
                
                imgs = st.text_area("사진URL (한 줄에 하나씩)", key="reg_imgs")
                tst = st.text_area("테스트 상세 결과", key="reg_test")
                yt = st.text_input("유튜브 링크", key="reg_yt")
                dan = st.text_area("다나와 견적 리스트", key="reg_dan")
                
                # ✅ 전송 버튼 (반드시 form 안에 있어야 함)
                submit_button = st.form_submit_button("🚀 사양 등록하기")
                
                if submit_button:
                    # 데이터 저장 로직
                    nr = pd.DataFrame([{
                        'ID': nid, '날짜': dt.strftime("%Y-%m-%d"), 'CPU': cpu, 
                        'GPU': gpu, '메모리': ram, '다나와견적': dan, 
                        '현금가': cash, '카드가': card, '사진URL들': imgs, 
                        '테스트상세': tst, '유튜브URL': str(yt), '카테고리': cat_str
                    }])
                    conn.update(data=pd.concat([df, nr], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"#{nid}번 사양 등록 완료!")
                    st.rerun()
                    
        with s2:
            st.write("### 🛠️ 등록 데이터 수정 및 관리")
            mdf = load_data()
            if not mdf.empty:
                if st.button("🔥 3개월 경과 데이터 일괄 삭제", key="del_old_data"):
                    mdf['dt'] = pd.to_datetime(mdf['날짜'])
                    cleaned = mdf[mdf['dt'] >= pd.Timestamp.now() - pd.DateOffset(months=3)].drop(columns=['dt'])
                    conn.update(data=cleaned)
                    st.cache_data.clear()
                    st.rerun()
                
                # 데이터 에디터 (여기서 직접 수정 가능)
                edf = st.data_editor(mdf, num_rows="dynamic", use_container_width=True, key="main_editor")
                if st.button("💾 변경사항 저장하기", key="save_changes"):
                    if '유튜브URL' in edf.columns:
                        edf['유튜브URL'] = edf['유튜브URL'].astype(str)
                    conn.update(data=edf)
                    st.cache_data.clear()
                    st.success("데이터베이스에 성공적으로 저장되었습니다.")
