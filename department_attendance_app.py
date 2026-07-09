#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import os, json, sqlite3, pickle, threading
import cv2
import cloudscraper
from datetime import datetime
from PIL import Image, ImageTk
from face_recognizer import FaceRecognizer, TRAINER_FILE
from database import init_db, add_student, get_student_by_id
from student_mapper import StudentMapper

CONFIG_FILE = "educonnect_config.json"
AUTH_FILE = ".educonnect_auth"

PRODUCTION_URL = "https://educonnect.onrender.com"
LOCALHOST_URL = "http://localhost:5002"

def _browser_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

def detect_server_url():
    urls = [PRODUCTION_URL, LOCALHOST_URL]
    cfg = load_config()
    if cfg.get("base_url") and cfg["base_url"] not in urls:
        urls.insert(0, cfg["base_url"])
    for url in urls:
        try:
            scraper = cloudscraper.create_scraper()
            r = scraper.get(f"{url}/api/auth/login", timeout=10)
            if r.status_code in (200, 405, 401):
                return url
        except:
            pass
    return PRODUCTION_URL

BG = "#f1f5f9"
CARD_BG = "#ffffff"
HDR_BG = "#0f172a"
BTN_LOGIN = "#0f172a"
BTN_LOAD = "#334155"
BTN_SCAN = "#047857"
BTN_SUBMIT = "#1d4ed8"
BTN_CAPTURE = "#1d4ed8"
BTN_TRAIN = "#b45309"
BTN_CLOSE = "#b91c1c"
CARD_GREEN_BG = "#dcfce7"
CARD_GREEN_BORDER = "#16a34a"
CARD_GREEN_FG = "#14532d"
CARD_RED_BG = "#fee2e2"
CARD_RED_BORDER = "#dc2626"
CARD_RED_FG = "#7f1d1d"
TEXT_DARK = "#0f172a"
TEXT_MUTED = "#475569"
TEXT_WHITE = "#ffffff"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_config(d):
    with open(CONFIG_FILE, "w") as f: json.dump(d, f, indent=2)

def load_auth():
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE) as f: return json.load(f)
        except: return {}
    return {}

def clear_auth():
    if os.path.exists(AUTH_FILE): os.remove(AUTH_FILE)


def make_btn(parent, text, cmd, bg, fg=TEXT_WHITE, w=12):
    return tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                    bg=bg, fg=fg, padx=18, pady=8, bd=1,
                    relief="raised", cursor="hand2",
                    activebackground=bg, activeforeground=fg,
                    highlightbackground="#94a3b8", highlightthickness=1,
                    command=cmd, width=w)


CARD_GRAY_BG = "#f1f5f9"
CARD_GRAY_BORDER = "#94a3b8"
CARD_GRAY_FG = "#475569"
CARD_TEAL_BG = "#ccfbf1"
CARD_TEAL_BORDER = "#0d9488"
CARD_TEAL_FG = "#115e59"


def build_student_card(parent, name, sid, total, today_status, is_present=False, trained=False):
    bg = CARD_GREEN_BG if is_present else CARD_RED_BG
    border = CARD_GREEN_BORDER if is_present else CARD_RED_BORDER
    fg = CARD_GREEN_FG if is_present else CARD_RED_FG
    today_label = today_status.title() if today_status else "Not Marked"

    card = tk.Frame(parent, bg=CARD_BG, highlightthickness=1,
                   highlightbackground="#e2e8f0", padx=16, pady=10)
    card.pack(fill=tk.X, padx=6, pady=3)

    bar = tk.Frame(card, bg=border, width=6)
    bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
    bar.pack_propagate(False)

    content = tk.Frame(card, bg=CARD_BG)
    content.pack(side=tk.LEFT, fill=tk.X, expand=True)

    row1 = tk.Frame(content, bg=CARD_BG)
    row1.pack(fill=tk.X)
    tk.Label(row1, text=name, font=("Segoe UI", 14, "bold"),
            bg=CARD_BG, fg=TEXT_DARK, anchor="w").pack(side=tk.LEFT)

    badge = tk.Label(row1, text=today_label, font=("Segoe UI", 9, "bold"),
                    bg=bg, fg=fg, padx=8, pady=2)
    badge.pack(side=tk.RIGHT, padx=(0, 8))

    if trained:
        t_bg = CARD_TEAL_BG
        t_border = CARD_TEAL_BORDER
        t_fg = CARD_TEAL_FG
        t_label = "TRAINED"
    else:
        t_bg = CARD_GRAY_BG
        t_border = CARD_GRAY_BORDER
        t_fg = CARD_GRAY_FG
        t_label = "NOT TRAINED"
    tk.Label(row1, text=t_label, font=("Segoe UI", 9, "bold"),
            bg=t_bg, fg=t_fg, padx=8, pady=2).pack(side=tk.RIGHT)

    row2 = tk.Frame(content, bg=CARD_BG)
    row2.pack(fill=tk.X, pady=(2, 4))
    if sid:
        tk.Label(row2, text=f"ID: {sid}", font=("Segoe UI", 10),
                bg=CARD_BG, fg=TEXT_MUTED, anchor="w").pack(side=tk.LEFT)

    meta = tk.Frame(content, bg=CARD_BG)
    meta.pack(fill=tk.X)
    tk.Label(meta, text=f"Today: {today_label}",
            font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=border).pack(side=tk.LEFT)


def build_scanner_card(parent, name, status, is_present):
    bg = CARD_GREEN_BG if is_present else CARD_RED_BG
    border = CARD_GREEN_BORDER if is_present else CARD_RED_BORDER
    fg = CARD_GREEN_FG if is_present else CARD_RED_FG
    label = "PRESENT" if is_present else "ABSENT"

    card = tk.Frame(parent, bg=CARD_BG, highlightthickness=1,
                   highlightbackground="#e2e8f0", padx=14, pady=8)
    card.pack(fill=tk.X, padx=6, pady=2)

    bar = tk.Frame(card, bg=border, width=5)
    bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    bar.pack_propagate(False)

    content = tk.Frame(card, bg=CARD_BG)
    content.pack(side=tk.LEFT, fill=tk.X, expand=True)

    tk.Label(content, text=name, font=("Segoe UI", 12, "bold"),
            bg=CARD_BG, fg=TEXT_DARK, anchor="w").pack(fill=tk.X)
    tk.Label(content, text=label, font=("Segoe UI", 9, "bold"),
            bg=bg, fg=fg).pack(anchor="w")


class App:
    def __init__(self, root, token=None, class_id=None, date=None):
        self.root = root
        self.root.title("EduConnect - Face Attendance")
        self.root.geometry("1100x720")
        self.root.configure(bg=BG)

        init_db()
        self.mapper = StudentMapper()
        self.face_recognizer = FaceRecognizer()
        self.session = cloudscraper.create_scraper()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.base_url = "http://localhost:5002"
        self.token = None
        self.class_id = None
        self.roster_students = []
        self.existing_status_map = {}
        self.recognized_ids = set()
        self.subject_map = {}
        self.scanner_cards = {}

        cfg = load_config()
        if cfg.get("base_url"): self.base_url = cfg["base_url"]
        self.base_url = detect_server_url()
        if not cfg.get("base_url") or cfg["base_url"] != self.base_url:
            save_config({**cfg, "base_url": self.base_url})

        # Warm up Cloudflare connection in background
        if self.base_url == PRODUCTION_URL:
            threading.Thread(target=self._warmup_connection, daemon=True).start()

        if token:
            self.token = token
            self.class_id = class_id
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"
            })
            self._build_main()
            self._load_subjects_and_select_class(class_id, date)
            self.root.after(1000, self._start_scan)
        else:
            auth = load_auth()
            if auth.get("token") and auth.get("base_url"):
                self.base_url = auth["base_url"]
                self.token = auth["token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"
                })
                clear_auth()
                self._build_main()
                self._load_subjects()
            else:
                self._build_login()

    def _clear(self):
        for w in self.root.winfo_children(): w.destroy()

    # ═══ LOGIN ═══════════════════════════════════════════════════════
    def _build_login(self):
        self._clear()
        tk.Frame(self.root, bg=HDR_BG, height=180).pack(fill=tk.X)

        card = tk.Frame(self.root, bg=CARD_BG, padx=50, pady=40,
                        highlightbackground="#cbd5e1", highlightthickness=1)
        card.place(relx=0.5, rely=0.42, anchor="center", width=420)

        tk.Label(card, text="Sign In", font=("Segoe UI", 26, "bold"),
                bg=CARD_BG, fg=TEXT_DARK).pack(pady=(0, 28))

        tk.Label(card, text="Email", font=("Segoe UI", 11), bg=CARD_BG,
                anchor="w", fg=TEXT_MUTED).pack(fill=tk.X, padx=5)
        self.login_email = tk.Entry(card, font=("Segoe UI", 13),
                                     relief="solid", bd=1)
        self.login_email.pack(fill=tk.X, padx=5, pady=(2, 16), ipady=6)
        c = load_config()
        if c.get("email"): self.login_email.insert(0, c["email"])

        tk.Label(card, text="Password", font=("Segoe UI", 11), bg=CARD_BG,
                anchor="w", fg=TEXT_MUTED).pack(fill=tk.X, padx=5)
        self.login_pwd = tk.Entry(card, font=("Segoe UI", 13), show="*",
                                   relief="solid", bd=1)
        self.login_pwd.pack(fill=tk.X, padx=5, pady=(2, 26), ipady=6)

        make_btn(card, "LOGIN", self._do_login, BTN_LOGIN).pack(pady=8, padx=5, fill=tk.X)
        self.login_err = tk.Label(card, text="", font=("Segoe UI", 9),
                                  bg=CARD_BG, fg=CARD_RED_BORDER)
        self.login_err.pack()

    def _do_login(self):
        try:
            e = self.login_email.get().strip()
            p = self.login_pwd.get().strip()
        except: return
        if not e or not p:
            try: self.login_err.config(text="Enter email and password")
            except: pass
            return

        try: self.login_err.config(text="Connecting...", fg=TEXT_MUTED)
        except: pass
        self.root.update()

        detected = detect_server_url()
        if detected:
            self.base_url = detected
            cfg = load_config()
            save_config({**cfg, "base_url": self.base_url, "email": e})

        try:
            try: self.login_err.config(text="Logging in...", fg=TEXT_MUTED)
            except: pass
            self.root.update()
            resp = self.session.post(f"{self.base_url}/api/auth/login",
                                     json={"email": e, "password": p, "role": "teacher"}, timeout=30)
            resp.raise_for_status()
            d = resp.json()
            if d.get("success") and "token" in d.get("data", {}):
                self.token = d["data"]["token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}", "Content-Type": "application/json"
                })
                self.root.after(0, self._post_login)
            else:
                try: self.login_err.config(text="Invalid credentials", fg=CARD_RED_BORDER)
                except: pass
        except Exception as ex:
            msg = str(ex)[:80]
            if '403' in msg or 'Forbidden' in msg:
                msg = "Blocked by Cloudflare.\nGo to Render Dashboard → disable Cloudflare proxy,\nor use http://localhost:5002 for local development."
            try: self.login_err.config(text=msg, fg=CARD_RED_BORDER)
            except: pass

    def _warmup_connection(self):
        try:
            self.session.get(self.base_url, timeout=30)
        except:
            pass

    def _post_login(self):
        self._build_main()
        self._load_subjects()

    # ═══ MAIN UI ══════════════════════════════════════════════════════
    def _build_main(self):
        self._clear()

        hdr = tk.Frame(self.root, bg=HDR_BG, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Frame(hdr, bg="#1d4ed8", height=3).pack(fill=tk.X)
        tk.Label(hdr, text="EduConnect \u2014 Face Recognition Attendance",
                font=("Segoe UI", 16, "bold"), bg=HDR_BG, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=20, pady=8)

        tb = tk.Frame(self.root, bg=CARD_BG, height=52)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)

        tk.Label(tb, text="Subject", font=("Segoe UI", 11, "bold"),
                bg=CARD_BG, fg=TEXT_DARK).pack(side=tk.LEFT, padx=(20, 6))
        self.sub_dd = ttk.Combobox(tb, state="readonly", width=30, font=("Segoe UI", 11))
        self.sub_dd.pack(side=tk.LEFT, padx=6)
        self.sub_dd.bind("<<ComboboxSelected>>", self._on_sub)

        tk.Label(tb, text="Date", font=("Segoe UI", 10, "bold"),
                bg=CARD_BG, fg=TEXT_DARK).pack(side=tk.LEFT, padx=(16, 6))
        self.date_ent = tk.Entry(tb, width=13, font=("Segoe UI", 11),
                                  justify="center", relief="solid", bd=1)
        self.date_ent.pack(side=tk.LEFT, padx=6)
        self.date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))

        make_btn(tb, "LOAD", self._load_ro, BTN_LOAD, w=7).pack(side=tk.LEFT, padx=12)
        make_btn(tb, "START SCANNER", self._start_scan, BTN_SCAN).pack(side=tk.RIGHT, padx=14)
        make_btn(tb, "SUBMIT", self._submit_att, BTN_SUBMIT, w=9).pack(side=tk.RIGHT)

        self.submit_count = tk.Label(tb, text="Present: 0 / 0", font=("Segoe UI", 12, "bold"),
                                  bg=CARD_BG, fg=BTN_SUBMIT)
        self.submit_count.pack(side=tk.RIGHT, padx=12)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[18, 6])
        style.map("TNotebook.Tab", background=[("selected", CARD_BG)])

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 12))

        for title, builder in [
            ("Students", self._tab_students),
            ("Training", self._tab_training),
            ("Scanner", self._tab_scanner)
        ]:
            f = tk.Frame(self.nb, bg=BG)
            self.nb.add(f, text=title)
            builder(f)

    def _tab_students(self, parent):
        self._rs = tk.Label(parent, text="Select a subject from the toolbar",
                           font=("Segoe UI", 11), bg="#cbd5e1", fg=TEXT_DARK,
                           anchor="w", padx=18, pady=8)
        self._rs.pack(fill=tk.X)
        c = tk.Frame(parent, bg=BG)
        c.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        cv = tk.Canvas(c, bg=BG, highlightthickness=0)
        vs = tk.Scrollbar(c, orient=tk.VERTICAL, command=cv.yview)
        self._ri = tk.Frame(cv, bg=BG)
        self._ri.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=self._ri, anchor="nw")
        cv.configure(yscrollcommand=vs.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vs.pack(side=tk.RIGHT, fill=tk.Y)

    def _tab_training(self, parent):
        tk.Label(parent, text="Capture face samples and train the recognition model",
                font=("Segoe UI", 11), bg=CARD_BG, fg=TEXT_MUTED,
                anchor="w", padx=18, pady=10).pack(fill=tk.X)
        row = tk.Frame(parent, bg=CARD_BG, padx=18, pady=8)
        row.pack(fill=tk.X)
        tk.Label(row, text="Student:", font=("Segoe UI", 11, "bold"),
                bg=CARD_BG, fg=TEXT_DARK).pack(side=tk.LEFT)
        self._tdd = ttk.Combobox(row, state="readonly", width=34, font=("Segoe UI", 11))
        self._tdd.pack(side=tk.LEFT, padx=10)
        make_btn(row, "CAPTURE 30 PHOTOS", self._do_capture, BTN_CAPTURE).pack(side=tk.LEFT, padx=6)
        make_btn(row, "TRAIN MODEL", self._do_train, BTN_TRAIN).pack(side=tk.LEFT, padx=6)
        self._ts = tk.Label(parent, text="", font=("Segoe UI", 11), bg="#cbd5e1",
                            fg=TEXT_DARK, anchor="w", padx=12)
        self._ts.pack(fill=tk.X, pady=(6, 0))
        lf = tk.Frame(parent, bg=BG)
        lf.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self._tl = tk.Text(lf, font=("Consolas", 11), bg="#0f172a",
                           fg="#22c55e", padx=16, pady=10,
                           insertbackground="#22c55e", relief="flat")
        self._tl.pack(fill=tk.BOTH, expand=True)

    def _tab_scanner(self, parent):
        self._ss = tk.Label(parent, text="Select subject from toolbar",
                           font=("Segoe UI", 11), bg="#cbd5e1", fg=TEXT_DARK,
                           anchor="w", padx=18, pady=8)
        self._ss.pack(fill=tk.X)
        c = tk.Frame(parent, bg=BG)
        c.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        cv = tk.Canvas(c, bg=BG, highlightthickness=0)
        vs = tk.Scrollbar(c, orient=tk.VERTICAL, command=cv.yview)
        self._si = tk.Frame(cv, bg=BG)
        self._si.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=self._si, anchor="nw")
        cv.configure(yscrollcommand=vs.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vs.pack(side=tk.RIGHT, fill=tk.Y)

    # ═══ DATA ══════════════════════════════════════════════════════════
    def _load_subjects(self):
        try:
            resp = self.session.get(f"{self.base_url}/api/classes", timeout=10)
            resp.raise_for_status()
            d = resp.json()
            if d.get("success"):
                classes = d["data"]["classes"] if "classes" in d["data"] else d["data"]
                self.subject_map = {c["name"]: c for c in classes}
                names = list(self.subject_map.keys())
                self.sub_dd["values"] = names
                if names:
                    self.sub_dd.set(names[0])
                    self._load_ro()
        except Exception as ex:
            try: self._rs.config(text=f"Error: {ex}")
            except: pass

    def _load_subjects_and_select_class(self, class_id, date=None):
        try:
            resp = self.session.get(f"{self.base_url}/api/classes", timeout=10)
            resp.raise_for_status()
            d = resp.json()
            if d.get("success"):
                classes = d["data"]["classes"] if "classes" in d["data"] else d["data"]
                self.subject_map = {c["name"]: c for c in classes}
                names = list(self.subject_map.keys())
                self.sub_dd["values"] = names
                for name, cls in self.subject_map.items():
                    if cls["_id"] == class_id:
                        self.sub_dd.set(name)
                        if date:
                            self.date_ent.delete(0, tk.END)
                            self.date_ent.insert(0, date)
                        self._load_ro()
                        return
        except Exception as ex:
            try: self._rs.config(text=f"Error: {ex}")
            except: pass

    def _on_sub(self, e):
        self._load_ro()

    def _load_ro(self):
        name = self.sub_dd.get()
        if not name or name not in self.subject_map: return
        cls = self.subject_map[name]
        self.class_id = cls["_id"]
        try: self._rs.config(text=f"Loading {name}...")
        except: pass
        try:
            resp = self.session.get(f"{self.base_url}/api/classes/{self.class_id}", timeout=10)
            resp.raise_for_status()
            d = resp.json()
            if d.get("success"):
                self.roster_students = d["data"].get("students", [])
                self._load_existing()
        except Exception as ex:
            try: self._rs.config(text=f"Error: {ex}")
            except: pass

    def _load_existing(self):
        d = self.date_ent.get().strip() or datetime.now().strftime("%Y-%m-%d")
        self.existing_status_map = {}
        try:
            resp = self.session.get(
                f"{self.base_url}/api/attendance/class-status?classId={self.class_id}&date={d}", timeout=10)
            resp.raise_for_status()
            dd = resp.json()
            if dd.get("success"):
                for s in dd["data"]:
                    mid = s.get("mongoId") or s.get("studentId")
                    self.existing_status_map[mid] = s.get("status", "not_marked")
        except: pass
        self._render_roster()
        self._render_scanner()
        self._refresh_train_dd()
        p = sum(1 for v in self.existing_status_map.values() if v == "present")
        t = len(self.roster_students)
        sn = self.sub_dd.get()
        try:
            self._rs.config(text=f"{sn}  |  {d}  |  Students: {t}  |  Present: {p}")
            self._ss.config(text=f"{sn}  |  {d}  |  Present: {p}/{t}")
        except: pass
        self.recognized_ids = set(mid for mid, st in self.existing_status_map.items() if st == "present")
        self.submit_count.config(text=f"Present: {len(self.recognized_ids)} / {t}")
        if os.path.exists(TRAINER_FILE):
            try:
                with open(TRAINER_FILE, "rb") as f:
                    td = pickle.load(f)
                try: self._ts.config(text=f"Model trained: {len(set(td['ids']))} students")
                except: pass
            except: pass
        else:
            try: self._ts.config(text="Model not trained \u2014 go to Training tab")
            except: pass

    def _render_roster(self):
        try:
            for w in self._ri.winfo_children(): w.destroy()
        except: return
        for s in self.roster_students:
            mid = s["_id"]
            st = self.existing_status_map.get(mid, "not_marked")
            is_present = st == "present"
            today_label = "Present" if is_present else "Absent" if st == "absent" else "Not Marked"
            local_id = None
            for lid, rid in self.mapper.mappings.items():
                if rid == mid:
                    local_id = int(lid)
                    break
            trained = False
            if local_id is not None:
                trained = os.path.exists(os.path.join("dataset", str(local_id))) and \
                          len(os.listdir(os.path.join("dataset", str(local_id)))) > 0
            build_student_card(self._ri, s["name"], s.get("studentId", ""),
                             st, today_label, is_present, trained)
        if not self.roster_students:
            tk.Label(self._ri, text="No students enrolled",
                   font=("Segoe UI", 12), bg=BG, fg=TEXT_MUTED).pack(pady=40)

    def _render_scanner(self):
        try:
            for w in self._si.winfo_children(): w.destroy()
        except: return
        self.scanner_cards = {}
        for s in self.roster_students:
            mid = s["_id"]
            st = self.existing_status_map.get(mid, "not_marked")
            is_present = st == "present"
            build_scanner_card(self._si, s["name"], st, is_present)
            self.scanner_cards[mid] = {"present": is_present}

    def _refresh_train_dd(self):
        names = [s["name"] for s in self.roster_students]
        self._tdd["values"] = names
        if names: self._tdd.set(names[0])

    def _do_capture(self):
        name = self._tdd.get()
        if not name:
            messagebox.showwarning("Warning", "Select a student")
            return
        mid = None
        for s in self.roster_students:
            if s["name"] == name: mid = s["_id"]; break
        if not mid: return
        fid = None
        for lid, rid in self.mapper.mappings.items():
            if rid == mid: fid = int(lid); break
        if not fid:
            conn = sqlite3.connect("attendance.db")
            cur = conn.cursor()
            cur.execute("SELECT id FROM students WHERE name=?", (name,))
            r = cur.fetchone()
            if r: fid = r[0]
            else: fid = add_student(name, "", "")
            conn.close()
            self.mapper.add_mapping(fid, mid)
        CaptureWin(self, self, fid, name)

    def _do_train(self):
        self._tl.insert(tk.END, "\n>>> Training model...\n")
        self._tl.see(tk.END)
        self.root.update()
        try:
            self.face_recognizer._known_encodings = None
            self.face_recognizer._known_ids = None
            ok = self.face_recognizer.train_model()
            if ok:
                self._tl.insert(tk.END, ">> Model trained!\n")
                try: self._ts.config(text="Model ready")
                except: pass
            else:
                self._tl.insert(tk.END, ">> Failed \u2014 capture photos first\n")
        except Exception as ex:
            self._tl.insert(tk.END, f">> Error: {ex}\n")
        self._tl.see(tk.END)

    def _start_scan(self):
        if not self.class_id:
            messagebox.showwarning("No Subject", "Select a subject first")
            return
        if not self.roster_students:
            messagebox.showwarning("No Students", "Load a class first")
            return
        ScannerWin(self, self)

    def _mark_green(self, mid):
        if mid not in self.scanner_cards: return
        self.scanner_cards[mid]["present"] = True
        self.submit_count.config(text=f"Present: {len([c for c in self.scanner_cards.values() if c['present']])} / {len(self.scanner_cards)}")

    def update_single_attendance_portal(self, student_mid):
        d = self.date_ent.get().strip() or datetime.now().strftime("%Y-%m-%d")
        def _sync():
            try:
                self.session.post(f"{self.base_url}/api/attendance",
                                  json={"classId": self.class_id, "date": d,
                                        "attendance": [{"studentId": student_mid, "status": "present"}]},
                                  timeout=10)
            except:
                pass
        threading.Thread(target=_sync, daemon=True).start()

    def _submit_att(self):
        if not self.scanner_cards:
            messagebox.showwarning("No Data", "No attendance data")
            return
        d = self.date_ent.get().strip() or datetime.now().strftime("%Y-%m-%d")
        records = []
        for mid, entry in self.scanner_cards.items():
            s = "present" if entry["present"] else "absent"
            records.append({"studentId": mid, "status": s})
        try:
            resp = self.session.post(f"{self.base_url}/api/attendance",
                                      json={"classId": self.class_id, "date": d, "attendance": records}, timeout=10)
            resp.raise_for_status()
            p = len([c for c in self.scanner_cards.values() if c["present"]])
            messagebox.showinfo("Success", f"Submitted!\nPresent: {p}/{len(records)}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex)[:60])


# ═══ CAPTURE WINDOW ══════════════════════════════════════════════════
class CaptureWin:
    def __init__(self, outer, app, student_id, student_name):
        self.outer = outer
        self.app = app
        self.student_id = student_id
        self.student_name = student_name
        self.target_count = 30
        self.count = 0

        self.win = tk.Toplevel(outer.root)
        self.win.title(f"Capture - {student_name}")
        self.win.geometry("700x520")
        self.win.configure(bg=BG)

        hdr = tk.Frame(self.win, bg=HDR_BG, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Frame(hdr, bg=BTN_CAPTURE, height=3).pack(fill=tk.X)
        tk.Label(hdr, text=f"Capturing: {student_name}",
                font=("Segoe UI", 15, "bold"), bg=HDR_BG, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=16, pady=8)

        self.cnt_label = tk.Label(hdr, text=f"0 / {self.target_count}",
                                  font=("Segoe UI", 14, "bold"), bg=HDR_BG, fg="#22c55e")
        self.cnt_label.pack(side=tk.RIGHT, padx=16)

        self.feed_frame = tk.Frame(self.win, bg="black")
        self.feed_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.feed = tk.Label(self.feed_frame, bg="black")
        self.feed.pack(fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(self.win, bg=CARD_BG, height=50)
        btn_row.pack(fill=tk.X)
        btn_row.pack_propagate(False)
        make_btn(btn_row, "START CAPTURE", self._start, BTN_CAPTURE, w=14).pack(side=tk.LEFT, padx=16, pady=8)
        make_btn(btn_row, "CLOSE", self._close, BTN_CLOSE, w=10).pack(side=tk.RIGHT, padx=16, pady=8)

        self.log = tk.Label(btn_row, text="Click START to begin", font=("Segoe UI", 10),
                           bg=CARD_BG, fg=TEXT_MUTED)
        self.log.pack(side=tk.LEFT, padx=10)

        self.cap = None
        self.running = False
        self.capturing = False
        self.student_path = os.path.join("dataset", str(student_id))
        if not os.path.exists(self.student_path):
            os.makedirs(self.student_path)

    def _start(self):
        if self.capturing: return
        self.cap = cv2.VideoCapture(0)
        if not self.cap or not self.cap.isOpened():
            self.log.config(text="ERROR: Camera not found!")
            return
        self.running = True
        self.capturing = True
        self.count = 0
        self.log.config(text="Capturing...")
        self._update()

    def _update(self):
        if not self.running: return
        if self.cap is None or not self.capturing:
            self.win.after(200, self._update); return
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.win.after(30, self._update); return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.face_recognizer.detect_face(frame)
        for (x, y, w, h) in faces[0]:
            if self.count < self.target_count:
                self.count += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_img = gray[max(0,y):y+h, max(0,x):x+w]
                cv2.imwrite(f"{self.student_path}/sample_{self.count}.jpg", face_img)
                cv2.rectangle(rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(rgb, f"{self.count}/{self.target_count}", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                self.cnt_label.config(text=f"{self.count} / {self.target_count}")
            else:
                cv2.rectangle(rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(rgb, "DONE", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.feed.imgtk = imgtk
        self.feed.configure(image=imgtk)
        if self.count >= self.target_count:
            self.capturing = False
            self.log.config(text=f"Done! {self.count} photos saved")
            self.app.face_recognizer._known_encodings = None
            self.app.face_recognizer._known_ids = None
        self.win.after(30, self._update)

    def _close(self):
        self.running = False
        self.capturing = False
        if self.cap: self.cap.release()
        self.win.destroy()


# ═══ SCANNER WINDOW ══════════════════════════════════════════════════
class ScannerWin:
    def __init__(self, outer, app):
        self.outer = outer
        self.app = app
        self.win = tk.Toplevel(outer.root)
        self.win.title(f"Scanner - {app.sub_dd.get()}")
        self.win.geometry("980x660")
        self.win.configure(bg=BG)

        self.recognized_mids = set(mid for mid, entry in outer.scanner_cards.items() if entry["present"])
        self.blink_states = {}

        left = tk.Frame(self.win, bg="black")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.feed = tk.Label(left, bg="black")
        self.feed.pack(fill=tk.BOTH, expand=True)

        right = tk.Frame(self.win, bg=CARD_BG, width=300)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right.pack_propagate(False)

        tk.Label(right, text="Scanner Status", font=("Segoe UI", 17, "bold"),
                bg=CARD_BG, fg=TEXT_DARK).pack(pady=(18, 4), padx=16, anchor="w")
        self.cnt = tk.Label(right, text=f"Present: 0/0",
                           font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=BTN_SUBMIT)
        self.cnt.pack(padx=16, anchor="w")
        ttk.Separator(right, orient="horizontal").pack(fill=tk.X, padx=16, pady=6)

        cf = tk.Frame(right, bg=CARD_BG)
        cf.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        cv = tk.Canvas(cf, bg=CARD_BG, highlightthickness=0)
        vs = tk.Scrollbar(cf, orient=tk.VERTICAL, command=cv.yview)
        self.ci = tk.Frame(cv, bg=CARD_BG)
        self.ci.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=self.ci, anchor="nw")
        cv.configure(yscrollcommand=vs.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vs.pack(side=tk.RIGHT, fill=tk.Y)

        self.cw = {mid: {"present": mid in self.recognized_mids} for mid in outer.scanner_cards}
        self._render_scanner_cards()

        make_btn(right, "CLOSE SCANNER", self._close, BTN_CLOSE).pack(fill=tk.X, padx=16, pady=8)
        self.log = tk.Text(right, height=3, font=("Consolas", 9),
                          fg=TEXT_MUTED, bg=CARD_BG, relief="flat")
        self.log.pack(fill=tk.X, padx=16, pady=(0, 10))
        self.win.protocol("WM_DELETE_WINDOW", self._close)

        self.cap = None
        for attempt in range(5):
            try:
                self.cap = cv2.VideoCapture(0)
                if self.cap and self.cap.isOpened():
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        self.log.delete(1.0, tk.END)
                        self.log.insert(tk.END, "Camera ready")
                        break
                    else:
                        self.cap = None
                else:
                    self.cap = None
            except:
                pass
            self.cap = None
            self.win.update()
        if self.cap is None:
            self.log.delete(1.0, tk.END)
            self.log.insert(tk.END, "ERROR: No camera detected!\nGrant camera permission in\nSystem Settings > Privacy > Camera")
        self.running = True
        self._update()

    def _render_scanner_status(self):
        p = len([c for c in self.cw.values() if c["present"]])
        t = len(self.cw)
        try:
            self.cnt.config(text=f"Present: {p}/{t}")
        except:
            pass

    def _render_scanner_cards(self):
        try:
            for w in self.ci.winfo_children(): w.destroy()
        except:
            return
        for mid, entry in self.cw.items():
            name = next((s["name"] for s in self.app.roster_students if s["_id"] == mid), "")
            is_present = entry.get("present", False)
            build_scanner_card(self.ci, name, "present" if is_present else "absent", is_present)
        if not self.cw:
            tk.Label(self.ci, text="No students loaded",
                   font=("Segoe UI", 12), bg=CARD_BG, fg=TEXT_MUTED).pack(pady=40)

    def _mark_green(self, mid):
        if mid not in self.cw: return
        self.cw[mid]["present"] = True
        self.outer.scanner_cards[mid]["present"] = True
        self._render_scanner_status()
        self._render_scanner_cards()
        p = len([c for c in self.outer.scanner_cards.values() if c["present"]])
        t = len(self.outer.scanner_cards)
        self.outer.submit_count.config(text=f"Present: {p}/{t}")

    def _update(self):
        if not self.running: return
        if self.cap is None:
            self.win.after(500, self._update); return
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.win.after(30, self._update); return
        recognized = []
        try:
            recognized = self.app.face_recognizer.recognize_face_with_liveness(frame)
        except Exception as ex:
            self.log.delete(1.0, tk.END)
            self.log.insert(tk.END, f"Error: {str(ex)[:40]}")
        for item in recognized:
            if len(item) == 4:
                fid, conf, (x, y, w, h), ear = item
                if fid is not None:
                    mid = self.app.mapper.get_educonnect_id(fid)
                    student = next((s for s in self.app.roster_students if s["_id"] == mid), None) if mid else None
                    if mid and student:
                        student_name = student.get("name", "")
                        student_id = student.get("studentId", "")
                        display_text = f"{student_name} ({student_id})"
                        if fid not in self.blink_states:
                            self.blink_states[fid] = {"c": False, "b": 0, "cc": 0}
                        if ear < 0.22:
                            self.blink_states[fid]["cc"] += 1
                            if self.blink_states[fid]["cc"] >= 2:
                                self.blink_states[fid]["c"] = True
                        else:
                            if self.blink_states[fid]["c"]:
                                self.blink_states[fid]["b"] += 1
                            self.blink_states[fid]["cc"] = 0
                            self.blink_states[fid]["c"] = False
                        if self.blink_states[fid]["b"] >= 1:
                            if mid not in self.cw or not self.cw[mid]["present"]:
                                self.recognized_mids.add(mid)
                                self._mark_green(mid)
                                self.app.update_single_attendance_portal(mid)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, f"{display_text} | {conf:.0f}%", (x, y - 12),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
                            cv2.putText(frame, "VERIFIED", (x, y + h + 18),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                            cv2.putText(frame, f"{display_text} | {conf:.0f}%", (x, y - 12),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1)
                            cv2.putText(frame, "PLEASE BLINK", (x, y + h + 18),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                    else:
                        local_student = get_student_by_id(fid) if fid else None
                        if local_student:
                            local_name = local_student[1]
                            local_roll = local_student[2]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(frame, f"{local_name} ({local_roll}) | {conf:.0f}%", (x, y - 12),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                            cv2.putText(frame, "NOT IN CLASS ROSTER", (x, y + h + 18),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(frame, f"UNKNOWN | {conf:.0f}%", (x, y - 12),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, f"UNKNOWN | {conf:.0f}%", (x, y - 12),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        p = len([c for c in self.cw.values() if c["present"]])
        t = len(self.cw)
        cv2.putText(frame, f"Present: {p}/{t}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.feed.imgtk = imgtk
        self.feed.configure(image=imgtk)
        self.win.after(30, self._update)

    def _close(self):
        self.running = False
        if self.cap: self.cap.release()
        self.win.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()