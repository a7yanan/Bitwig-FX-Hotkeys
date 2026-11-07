import os, sys, time, tempfile, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fxhotkeys import keys, config, winapi, engine as eng

# ---------- config round trip
def test_config_roundtrip():
    d = tempfile.mkdtemp(); path = os.path.join(d, "c.json")
    cfg = config.load(path)
    assert len(cfg.profiles) == 2 and len(cfg.profiles[0].shortcuts) == 19
    cfg.profiles[0].shortcuts[0].text = "\u0645\u0631\u062d\u0628\u0627"
    config.save(cfg, path)
    cfg2 = config.load(path)
    assert cfg2.profiles[0].shortcuts[0].text == "\u0645\u0631\u062d\u0628\u0627"
    open(path, "w").write("{broken")
    assert len(config.load(path).profiles) == 2 and os.path.exists(path + ".bak")

def test_default_steps_parse_and_hotkeys_valid():
    cfg = config.default_config()
    for p in cfg.profiles:
        assert keys.validate_steps(p.steps)[1] is None
        for s in p.shortcuts:
            assert keys.parse_hotkey(s.hotkey), s.hotkey
            if s.steps: assert keys.validate_steps(s.steps)[1] is None

def test_profile_matching():
    p = config.Profile(exe="Bitwig-Studio.exe, other", title="")
    assert p.matches("bitwig-studio.exe", "x") and p.matches("OTHER.exe", "") and not p.matches("a.exe", "")
    q = config.Profile(title="Bitwig Studio")
    assert q.matches("anything.exe", "My Song - bitwig studio 5") and not q.matches("a.exe", "Notepad")
    assert config.Profile().is_global and not q.is_global

# ---------- engine with a fake Windows
class Fake:
    def __init__(self):
        self.calls = []; self.fg = ("bitwig-studio.exe", "Bitwig Studio - x")
        winapi.foreground_info = lambda: self.fg
        winapi.foreground_hkl = lambda: None
        winapi.async_down = lambda vk: True
        winapi.tap = lambda m, v: self.calls.append(("tap", m, v))
        winapi.type_text = lambda t, mode, hkl: self.calls.append(("type", t, mode))
        winapi.click = lambda b, c: self.calls.append(("click", b, c))
        winapi.release_modifiers = lambda v: self.calls.append(("release", tuple(v)))
        winapi.press_modifiers = lambda v: self.calls.append(("press", tuple(v)))

def wait_idle(e):
    for _ in range(200):
        if not e._busy.locked(): return
        time.sleep(0.01)
    raise AssertionError("still busy")

def test_hotkey_fires_and_runs_steps():
    f = Fake(); cfg = config.default_config()
    for p in cfg.profiles: p.delay_ms = 0
    e = eng.Engine(cfg); logs = []; e.on_log = logs.append
    assert e._on_key(0xA2, True) is False                 # Ctrl down
    assert e._on_key(0x61, True) is True                  # Numpad1 -> swallowed
    wait_idle(e); time.sleep(0.05)
    kinds = [c[0] for c in f.calls]
    assert f.calls[0] == ("release", (0xA2,))
    assert ("tap", 2, 0x43) in f.calls                    # alt+c  (custom steps for ctrl+numpad1)
    assert ("type", "EQ+", "keys") in f.calls and ("click", "left", 1) in f.calls
    assert f.calls[-1] == ("press", (0xA2,))              # ctrl restored (still held)
    assert logs and logs[0]["error"] == "" and logs[0]["label"] == "EQ+"
    assert e._on_key(0x61, True) is True                  # auto-repeat swallowed, not re-run
    assert e._on_key(0x61, False) is True                 # key-up swallowed
    assert e._on_key(0xA2, False) is False

def test_wrong_window_passes_through():
    f = Fake(); f.fg = ("notepad.exe", "Untitled")
    e = eng.Engine(config.default_config())
    e._on_key(0xA2, True)
    assert e._on_key(0x31, True) is False and f.calls == []

def test_global_profile_and_priority():
    f = Fake(); f.fg = ("anything.exe", "x")
    cfg = config.AppConfig(profiles=[
        config.Profile(name="All", delay_ms=0, steps="type G", shortcuts=[config.Shortcut(hotkey="f9", text="all")]),
        config.Profile(name="Any", exe="anything.exe", delay_ms=0, steps="type S", shortcuts=[config.Shortcut(hotkey="f9", text="spec")])])
    e = eng.Engine(cfg)
    assert e._on_key(0x78, True) is True; wait_idle(e); time.sleep(0.05)
    assert ("type", "S", "keys") in f.calls and ("type", "G", "keys") not in f.calls

def test_disabled_and_pause():
    f = Fake()
    cfg = config.default_config(); cfg.profiles[0].shortcuts[1].enabled = False
    e = eng.Engine(cfg)
    e._on_key(0xA2, True)
    assert e._on_key(0x62, True) is False                 # ctrl+numpad2 disabled
    e.paused = True
    assert e._on_key(0x63, True) is False                 # paused -> pass through

def test_capture():
    f = Fake(); e = eng.Engine(config.default_config()); got = []
    e.start_capture(got.append)
    e._on_key(0xA2, True); e._on_key(0xA0, True)
    assert e._on_key(0x61, True) is True
    assert got == ["ctrl+shift+numpad1"]
    assert e._on_key(0x61, True) is True and e._on_key(0x61, False) is True   # no re-trigger
    e.start_capture(got.append); e._on_key(0xA2, False); e._on_key(0xA0, False)
    assert e._on_key(0x1B, True) is True and got[-1] == ""

def test_bad_steps_logged_not_crash():
    f = Fake()
    cfg = config.AppConfig(profiles=[config.Profile(name="X", title="", steps="bogus", shortcuts=[config.Shortcut(hotkey="f8", text="t")])])
    e = eng.Engine(cfg); logs = []; e.on_log = logs.append
    assert e._on_key(0x77, True) is True; wait_idle(e); time.sleep(0.05)
    assert "unknown command" in logs[0]["error"] and not e._busy.locked()

def test_autosave_loop_sends_when_active():
    f = Fake()
    cfg = config.AppConfig(profiles=[config.Profile(name="B", title="Bitwig", autosave=True, autosave_every=5)])
    e = eng.Engine(cfg)
    orig_wait = e._stop.wait
    ticks = {"n": 0}
    base = time.monotonic()
    import fxhotkeys.engine as m
    clock = {"t": base}
    m.time = type("T", (), {"monotonic": staticmethod(lambda: clock["t"]), "sleep": time.sleep, "strftime": time.strftime})
    def fake_wait(_):
        ticks["n"] += 1; clock["t"] += 3
        return ticks["n"] > 6
    e._stop.wait = fake_wait
    e._autosave_loop()
    assert f.calls.count(("tap", 1, 0x53)) >= 1, f.calls

def test_schemes_and_contrast():
    from fxhotkeys import palette as P
    assert len(P.ORDER) == 5 and set(P.ORDER) == set(P.SCHEMES)
    for sch in P.ORDER:
        for mode in ("dark", "light"):
            c = P.build(mode, sch)
            assert P.contrast(c["text"], c["bg"]) >= 4.5 and P.contrast(c["text"], c["surface"]) >= 4.5
            assert P.contrast(c["muted"], c["surface"]) >= 3.0
            assert P.contrast(c["on_accent"], c["grad_a"]) >= 2.3 and P.contrast(c["on_accent"], c["grad_b"]) >= 2.3
    assert P.build("dark", "nope")["grad_a"] == P.build("dark", "aurora")["grad_a"]   # unknown -> default

def test_scheme_and_exe_path_persist():
    d = tempfile.mkdtemp(); path = os.path.join(d, "c.json")
    cfg = config.load(path)
    cfg.settings.scheme = "citrus"; cfg.profiles[0].exe_path = r"C:\\Apps\\bitwig-studio.exe"
    config.save(cfg, path)
    c2 = config.load(path)
    assert c2.settings.scheme == "citrus" and c2.profiles[0].exe_path.endswith("bitwig-studio.exe")
    import json
    data = json.load(open(path)); data["settings"]["scheme"] = "bogus"
    json.dump(data, open(path, "w")); assert config.load(path).settings.scheme == "aurora"

def test_log_reports_profile_id_and_path():
    f = Fake(); winapi.foreground_path = lambda: "/bin/ls"
    cfg = config.default_config()
    for p in cfg.profiles: p.delay_ms = 0
    e = eng.Engine(cfg); logs = []; e.on_log = logs.append
    e._on_key(0xA2, True); e._on_key(0x62, True); wait_idle(e); time.sleep(0.05)
    assert logs[0]["profile_id"] == cfg.profiles[0].id and logs[0]["path"] == "/bin/ls"

if __name__ == "__main__":
    import traceback
    ok = True
    for n, fn in list(globals().items()):
        if n.startswith("test_"):
            try: fn(); print("PASS", n)
            except Exception: ok = False; print("FAIL", n); traceback.print_exc()
    sys.exit(0 if ok else 1)
