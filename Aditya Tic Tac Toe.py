from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import urllib.request
import os

# ──────────────────────────────────────────────
#  SETUP WINDOW
# ──────────────────────────────────────────────
root = Tk()
root.title("Tic Tac Toe")
root.resizable(False, False)

Player1 = Player2 = Draws = 0

# ──────────────────────────────────────────────
#  BACKGROUND IMAGE (downloaded once, cached)
# ──────────────────────────────────────────────
BG_URL  = "https://images.unsplash.com/photo-1538370965046-79c0d6907d47?w=800&q=80"
BG_FILE = "ttt_bg.png"
bg_photo = None   # keep reference alive

def load_background():
    global bg_photo
    # Try to get PIL for image support
    try:
        from PIL import Image, ImageTk, ImageFilter
    except ImportError:
        try:
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
            from PIL import Image, ImageTk, ImageFilter
        except Exception:
            return   # silently skip background if PIL unavailable

    if not os.path.exists(BG_FILE):
        try:
            urllib.request.urlretrieve(BG_URL, BG_FILE)
        except Exception:
            return

    try:
        img = Image.open(BG_FILE).resize((520, 620), Image.LANCZOS)
        # Slight dark overlay so text pops
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")
        bg_photo = ImageTk.PhotoImage(img)
        bg_label = Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()   # push to back
    except Exception:
        pass

# ──────────────────────────────────────────────
#  FONTS & COLORS
# ──────────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_ENTRY  = ("Segoe UI", 12)
FONT_BTN    = ("Segoe UI", 28, "bold")
FONT_STATUS = ("Segoe UI", 11, "italic")
FONT_SCORE  = ("Segoe UI", 10)

CLR_BG      = "#1a1a2e"
CLR_PANEL   = "#16213e"
CLR_ACCENT  = "#e94560"
CLR_GOLD    = "#f5a623"
CLR_TEXT    = "#eaeaea"
CLR_MUTED   = "#8899aa"
CLR_X       = "#ff6b6b"
CLR_O       = "#4ecdc4"
CLR_BTN_BG  = "#0f3460"
CLR_BTN_HOV = "#1a4a80"

root.configure(bg=CLR_BG)
root.geometry("520x620")

# ──────────────────────────────────────────────
#  GAME STATE
# ──────────────────────────────────────────────
p1_name   = StringVar(value="Player 1")
p2_name   = StringVar(value="Player 2")
p1_symbol = StringVar(value="X")
p2_symbol = StringVar(value="O")

current_turn = 1   # 1 or 2
move_count   = 0
game_over    = False
buttons      = []

WINNING_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # cols
    (0,4,8),(2,4,6)            # diagonals
]

# ──────────────────────────────────────────────
#  SETUP DIALOG  (shown before main game)
# ──────────────────────────────────────────────
def open_setup_dialog():
    dlg = Toplevel(root)
    dlg.title("Game Setup")
    dlg.geometry("380x420")
    dlg.configure(bg=CLR_PANEL)
    dlg.resizable(False, False)
    dlg.grab_set()                    # modal
    dlg.transient(root)

    # ── Title ──
    Label(dlg, text="⚔  Tic Tac Toe", font=("Segoe UI", 18, "bold"),
          bg=CLR_PANEL, fg=CLR_ACCENT).pack(pady=(20, 4))
    Label(dlg, text="Customize your game before you begin",
          font=FONT_STATUS, bg=CLR_PANEL, fg=CLR_MUTED).pack(pady=(0, 18))

    frame = Frame(dlg, bg=CLR_PANEL)
    frame.pack(padx=30, fill=X)

    def row(parent, label_text, var, options=None, width=14):
        f = Frame(parent, bg=CLR_PANEL)
        f.pack(fill=X, pady=5)
        Label(f, text=label_text, font=FONT_LABEL, bg=CLR_PANEL,
              fg=CLR_TEXT, width=18, anchor=W).pack(side=LEFT)
        if options:
            cb = ttk.Combobox(f, textvariable=var, values=options,
                              width=width, state="readonly", font=FONT_ENTRY)
            cb.pack(side=LEFT)
        else:
            e = Entry(f, textvariable=var, width=width+2, font=FONT_ENTRY,
                      bg=CLR_BTN_BG, fg=CLR_TEXT, insertbackground=CLR_TEXT,
                      relief=FLAT, bd=4)
            e.pack(side=LEFT)

    SYMBOLS = ["X", "O", "★", "♦", "♠", "♥", "♣", "▲", "●", "✦"]

    Label(frame, text="── Player 1 ──", font=("Segoe UI", 10, "bold"),
          bg=CLR_PANEL, fg=CLR_X).pack(anchor=W, pady=(6, 2))
    row(frame, "Name:",   p1_name)
    row(frame, "Symbol:", p1_symbol, SYMBOLS)

    Label(frame, text="── Player 2 ──", font=("Segoe UI", 10, "bold"),
          bg=CLR_PANEL, fg=CLR_O).pack(anchor=W, pady=(12, 2))
    row(frame, "Name:",   p2_name)
    row(frame, "Symbol:", p2_symbol, SYMBOLS)

    def validate_and_start():
        s1 = p1_symbol.get().strip()
        s2 = p2_symbol.get().strip()
        n1 = p1_name.get().strip() or "Player 1"
        n2 = p2_name.get().strip() or "Player 2"
        if s1 == s2:
            tkinter.messagebox.showwarning("Oops",
                "Both players have the same symbol!\nPlease pick different ones.", parent=dlg)
            return
        p1_name.set(n1)
        p2_name.set(n2)
        dlg.destroy()
        build_game_ui()

    Button(dlg, text="▶  Start Game", font=("Segoe UI", 12, "bold"),
           bg=CLR_ACCENT, fg="white", activebackground="#c73652",
           relief=FLAT, bd=0, padx=20, pady=10,
           command=validate_and_start).pack(pady=24)

    dlg.protocol("WM_DELETE_WINDOW", validate_and_start)
    root.wait_window(dlg)

# ──────────────────────────────────────────────
#  MAIN GAME UI
# ──────────────────────────────────────────────
main_frame = None

def build_game_ui():
    global main_frame, buttons, current_turn, move_count, game_over
    global Player1, Player2, Draws

    # Reset state
    current_turn = 1
    move_count   = 0
    game_over    = False
    buttons      = []

    if main_frame:
        main_frame.destroy()

    main_frame = Frame(root, bg="", bd=0)   # transparent to show bg
    main_frame.pack(expand=True, fill=BOTH, padx=18, pady=14)

    # ── Title bar ──
    title_bar = Frame(main_frame, bg=CLR_PANEL, bd=0)
    title_bar.pack(fill=X, pady=(0, 10))
    Label(title_bar, text="✦  TIC TAC TOE  ✦",
          font=FONT_TITLE, bg=CLR_PANEL, fg=CLR_ACCENT,
          pady=8).pack()

    # ── Score board ──
    score_bar = Frame(main_frame, bg=CLR_PANEL)
    score_bar.pack(fill=X, pady=(0, 8))

    score_bar.columnconfigure(0, weight=1)
    score_bar.columnconfigure(1, weight=1)
    score_bar.columnconfigure(2, weight=1)

    p1_score_var = StringVar()
    p2_score_var = StringVar()
    draw_var      = StringVar()

    def refresh_scores():
        p1_score_var.set(f"{p1_name.get()}\n{p1_symbol.get()}  ·  {Player1} wins")
        p2_score_var.set(f"{p2_name.get()}\n{p2_symbol.get()}  ·  {Player2} wins")
        draw_var.set(f"Draws\n{Draws}")

    Label(score_bar, textvariable=p1_score_var, font=FONT_SCORE,
          bg=CLR_PANEL, fg=CLR_X, pady=6).grid(row=0, column=0, sticky=EW)
    Label(score_bar, textvariable=draw_var, font=FONT_SCORE,
          bg=CLR_PANEL, fg=CLR_MUTED, pady=6).grid(row=0, column=1, sticky=EW)
    Label(score_bar, textvariable=p2_score_var, font=FONT_SCORE,
          bg=CLR_PANEL, fg=CLR_O, pady=6).grid(row=0, column=2, sticky=EW)

    refresh_scores()

    # ── Status label ──
    status_var = StringVar(value=f"{p1_name.get()}'s turn  ({p1_symbol.get()})")
    status_lbl = Label(main_frame, textvariable=status_var,
                       font=FONT_STATUS, bg=CLR_BG, fg=CLR_GOLD, pady=4)
    status_lbl.pack()

    # ── Game grid ──
    grid_frame = Frame(main_frame, bg=CLR_ACCENT, bd=2)
    grid_frame.pack(pady=8)

    style = ttk.Style()
    style.configure("Game.TButton",
                    font=FONT_BTN, padding=20,
                    background=CLR_BTN_BG, foreground=CLR_TEXT)

    for i in range(9):
        btn = Button(
            grid_frame, text=" ", font=FONT_BTN,
            width=3, height=1,
            bg=CLR_BTN_BG, fg=CLR_TEXT,
            activebackground=CLR_BTN_HOV,
            relief=FLAT, bd=0,
            command=lambda idx=i: on_click(idx)
        )
        btn.grid(row=i//3, column=i%3, padx=2, pady=2, ipadx=18, ipady=14)
        buttons.append(btn)

    # ── Restart button ──
    def restart():
        global current_turn, move_count, game_over
        current_turn = 1
        move_count   = 0
        game_over    = False
        for b in buttons:
            b.config(text=" ", state=NORMAL, fg=CLR_TEXT, bg=CLR_BTN_BG)
        status_var.set(f"{p1_name.get()}'s turn  ({p1_symbol.get()})")

    def new_game():
        open_setup_dialog()

    btn_row = Frame(main_frame, bg=CLR_BG)
    btn_row.pack(pady=10, fill=X)

    Button(btn_row, text="↺  Restart", font=("Segoe UI", 10, "bold"),
           bg=CLR_BTN_BG, fg=CLR_TEXT, activebackground=CLR_BTN_HOV,
           relief=FLAT, bd=0, padx=14, pady=7,
           command=restart).pack(side=LEFT, expand=True, padx=6)

    Button(btn_row, text="⚙  New Game", font=("Segoe UI", 10, "bold"),
           bg=CLR_ACCENT, fg="white", activebackground="#c73652",
           relief=FLAT, bd=0, padx=14, pady=7,
           command=new_game).pack(side=LEFT, expand=True, padx=6)

    # ── Click handler ──
    def on_click(idx):
        global current_turn, move_count, game_over, Player1, Player2, Draws

        if game_over or buttons[idx]["text"] != " ":
            return

        sym  = p1_symbol.get() if current_turn == 1 else p2_symbol.get()
        clr  = CLR_X            if current_turn == 1 else CLR_O
        name = p1_name.get()    if current_turn == 1 else p2_name.get()

        buttons[idx].config(text=sym, fg=clr, state=DISABLED, disabledforeground=clr)
        move_count += 1

        # Check win
        board = [b["text"] for b in buttons]
        winner = None
        for combo in WINNING_COMBOS:
            a, bv, c = combo
            if board[a] == board[bv] == board[c] == sym:
                winner = combo
                break

        if winner:
            game_over = True
            for idx2 in winner:
                buttons[idx2].config(bg=CLR_ACCENT)
            if current_turn == 1:
                Player1 += 1
            else:
                Player2 += 1
            refresh_scores()
            status_var.set(f"🏆  {name} wins!")
            save_result(f"Winner is {name} ({sym})")
            tkinter.messagebox.showinfo("🏆 Winner!", f"{name} wins this round!")
            return

        if move_count == 9:
            game_over = True
            Draws += 1
            refresh_scores()
            status_var.set("🤝  It's a Draw!")
            save_result("Match is Drawn")
            tkinter.messagebox.showinfo("Draw!", "It's a draw! Well played both.")
            return

        current_turn = 2 if current_turn == 1 else 1
        next_name = p1_name.get() if current_turn == 1 else p2_name.get()
        next_sym  = p1_symbol.get() if current_turn == 1 else p2_symbol.get()
        status_var.set(f"{next_name}'s turn  ({next_sym})")

# ──────────────────────────────────────────────
#  RESULT FILE
# ──────────────────────────────────────────────
def save_result(text):
    try:
        with open("result.txt", "a") as f:
            f.write(text + "\n")
    except Exception:
        pass

# ──────────────────────────────────────────────
#  LAUNCH
# ──────────────────────────────────────────────
load_background()
open_setup_dialog()

root.mainloop()