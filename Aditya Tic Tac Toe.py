import streamlit as st
 
# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Tic Tac Toe", page_icon="🎮", layout="centered")
 
# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #1a1a2e; }
    h1 { color: #e94560; text-align: center; font-size: 2.5rem; }
    .status-box {
        background: #16213e;
        border-radius: 12px;
        padding: 14px 20px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 16px;
        color: #f5a623;
    }
    .score-box {
        background: #0f3460;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        color: white;
        font-size: 1rem;
    }
    .winner-msg {
        background: #e94560;
        color: white;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 12px;
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        height: 100px;
        font-size: 2.5rem;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #e94560;
        background-color: #0f3460;
        color: white;
        transition: 0.2s;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #1a4a80;
        border-color: #f5a623;
    }
</style>
""", unsafe_allow_html=True)
 
# ── Initialize session state ──────────────────────────────────
def init_state():
    defaults = {
        "board": [""] * 9,
        "current": 1,       # 1 = Player 1, 2 = Player 2
        "winner": None,
        "draw": False,
        "p1_score": 0,
        "p2_score": 0,
        "draws": 0,
        "p1_name": "Player 1",
        "p2_name": "Player 2",
        "p1_symbol": "X",
        "p2_symbol": "O",
        "setup_done": False,
        "winning_cells": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
 
init_state()
 
# ── Win check ─────────────────────────────────────────────────
WINNING_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]
 
def check_winner(board, symbol):
    for combo in WINNING_COMBOS:
        if all(board[i] == symbol for i in combo):
            return list(combo)
    return None
 
def handle_click(idx):
    s = st.session_state
    if s.board[idx] != "" or s.winner or s.draw:
        return
    sym = s.p1_symbol if s.current == 1 else s.p2_symbol
    s.board[idx] = sym
    winning = check_winner(s.board, sym)
    if winning:
        s.winner = s.current
        s.winning_cells = winning
        if s.current == 1:
            s.p1_score += 1
        else:
            s.p2_score += 1
    elif all(c != "" for c in s.board):
        s.draw = True
        s.draws += 1
    else:
        s.current = 2 if s.current == 1 else 1
 
def restart():
    st.session_state.board = [""] * 9
    st.session_state.current = 1
    st.session_state.winner = None
    st.session_state.draw = False
    st.session_state.winning_cells = []
 
def new_game():
    restart()
    st.session_state.setup_done = False
 
# ── SETUP SCREEN ──────────────────────────────────────────────
if not st.session_state.setup_done:
    st.markdown("<h1>⚔️ Tic Tac Toe</h1>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Game Setup")
 
    SYMBOLS = ["X", "O", "★", "♦", "♠", "♥", "♣", "▲", "●"]
 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔴 Player 1**")
        p1_name = st.text_input("Name", value="Player 1", key="inp_p1_name")
        p1_sym  = st.selectbox("Symbol", SYMBOLS, index=0, key="inp_p1_sym")
    with col2:
        st.markdown("**🔵 Player 2**")
        p2_name = st.text_input("Name", value="Player 2", key="inp_p2_name")
        p2_sym  = st.selectbox("Symbol", SYMBOLS, index=1, key="inp_p2_sym")
 
    if st.button("▶  Start Game", use_container_width=True):
        if p1_sym == p2_sym:
            st.error("⚠️ Both players have the same symbol! Please choose different ones.")
        else:
            st.session_state.p1_name   = p1_name or "Player 1"
            st.session_state.p2_name   = p2_name or "Player 2"
            st.session_state.p1_symbol = p1_sym
            st.session_state.p2_symbol = p2_sym
            st.session_state.setup_done = True
            restart()
            st.rerun()
 
# ── GAME SCREEN ───────────────────────────────────────────────
else:
    s = st.session_state
    st.markdown("<h1>🎮 Tic Tac Toe</h1>", unsafe_allow_html=True)
 
    # Score board
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div class="score-box">
            <div style="color:#ff6b6b;font-weight:bold">{s.p1_name}</div>
            <div style="font-size:0.85rem">{s.p1_symbol} · {s.p1_score} wins</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class="score-box">
            <div style="color:#aaa">Draws</div>
            <div style="font-size:1.2rem;font-weight:bold">{s.draws}</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class="score-box">
            <div style="color:#4ecdc4;font-weight:bold">{s.p2_name}</div>
            <div style="font-size:0.85rem">{s.p2_symbol} · {s.p2_score} wins</div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # Status bar
    if s.winner:
        name = s.p1_name if s.winner == 1 else s.p2_name
        sym  = s.p1_symbol if s.winner == 1 else s.p2_symbol
        st.markdown(f'<div class="winner-msg">🏆 {name} ({sym}) Wins!</div>', unsafe_allow_html=True)
    elif s.draw:
        st.markdown('<div class="winner-msg" style="background:#555">🤝 It\'s a Draw!</div>', unsafe_allow_html=True)
    else:
        cur_name = s.p1_name if s.current == 1 else s.p2_name
        cur_sym  = s.p1_symbol if s.current == 1 else s.p2_symbol
        st.markdown(f'<div class="status-box">🎯 {cur_name}\'s turn &nbsp;({cur_sym})</div>', unsafe_allow_html=True)
 
    # Game board — 3x3 grid
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            cell_val = s.board[idx]
            is_winning = idx in s.winning_cells
 
            label = cell_val if cell_val else " "
            with cols[col]:
                if st.button(label, key=f"cell_{idx}", disabled=bool(s.winner or s.draw or cell_val != "")):
                    handle_click(idx)
                    st.rerun()
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # Action buttons
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("↺  Restart (same players)", use_container_width=True):
            restart()
            st.rerun()
    with btn2:
        if st.button("⚙️  New Game (change names)", use_container_width=True):
            new_game()
            st.rerun()
 
