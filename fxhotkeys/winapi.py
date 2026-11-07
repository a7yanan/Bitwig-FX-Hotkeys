"""Thin ctypes layer over the Win32 API.

Everything here degrades to harmless stubs on non-Windows systems so the rest of
the app (and the unit tests) can be imported anywhere.
"""
from __future__ import annotations

import ctypes
import os
import sys
import threading
import time

IS_WIN = sys.platform == "win32"

VK_LSHIFT, VK_LCONTROL, VK_LMENU, VK_LWIN = 0xA0, 0xA2, 0xA4, 0x5B
_EXTENDED = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2C, 0x2D, 0x2E,
             0x5B, 0x5C, 0xA3, 0xA5, 0x6F, 0x90}
_MASK_KEY = 0xE8      # unassigned key, used to stop Alt/Win from opening menus

if IS_WIN:
    from ctypes import wintypes as wt

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    try:
        dwmapi = ctypes.WinDLL("dwmapi")
    except OSError:
        dwmapi = None

    ULONG_PTR = ctypes.c_size_t

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                    ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                    ("dwFlags", wt.DWORD), ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wt.DWORD), ("wParamL", wt.WORD), ("wParamH", wt.WORD)]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wt.DWORD), ("u", _INPUTUNION)]

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [("vkCode", wt.DWORD), ("scanCode", wt.DWORD), ("flags", wt.DWORD),
                    ("time", wt.DWORD), ("dwExtraInfo", ULONG_PTR)]

    HOOKPROC = ctypes.WINFUNCTYPE(wt.LPARAM, ctypes.c_int, wt.WPARAM, wt.LPARAM)
    WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    user32.GetForegroundWindow.restype = wt.HWND
    user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
    user32.GetWindowTextLengthW.argtypes = [wt.HWND]
    user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
    user32.GetWindowThreadProcessId.restype = wt.DWORD
    user32.IsWindowVisible.argtypes = [wt.HWND]
    user32.EnumWindows.argtypes = [WNDENUMPROC, wt.LPARAM]
    user32.SendInput.argtypes = [wt.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    user32.SendInput.restype = wt.UINT
    user32.MapVirtualKeyW.argtypes = [wt.UINT, wt.UINT]
    user32.MapVirtualKeyW.restype = wt.UINT
    user32.VkKeyScanExW.argtypes = [wt.WCHAR, wt.HKL]
    user32.VkKeyScanExW.restype = ctypes.c_short
    user32.GetKeyboardLayout.argtypes = [wt.DWORD]
    user32.GetKeyboardLayout.restype = wt.HKL
    user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    user32.GetAsyncKeyState.restype = ctypes.c_short
    user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wt.HINSTANCE, wt.DWORD]
    user32.SetWindowsHookExW.restype = wt.HHOOK
    user32.UnhookWindowsHookEx.argtypes = [wt.HHOOK]
    user32.UnhookWindowsHookEx.restype = wt.BOOL
    user32.CallNextHookEx.argtypes = [wt.HHOOK, ctypes.c_int, wt.WPARAM, wt.LPARAM]
    user32.CallNextHookEx.restype = wt.LPARAM
    user32.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT]
    user32.GetMessageW.restype = ctypes.c_int
    user32.PeekMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT, wt.UINT]
    user32.PostThreadMessageW.argtypes = [wt.DWORD, wt.UINT, wt.WPARAM, wt.LPARAM]
    kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    kernel32.OpenProcess.restype = wt.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wt.BOOL
    kernel32.CloseHandle.argtypes = [wt.HANDLE]
    kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wt.HMODULE
    kernel32.GetCurrentThreadId.restype = wt.DWORD
    shell32.ShellExecuteW.argtypes = [wt.HWND, wt.LPCWSTR, wt.LPCWSTR, wt.LPCWSTR, wt.LPCWSTR, ctypes.c_int]
    shell32.ShellExecuteW.restype = ctypes.c_void_p
    if dwmapi:
        dwmapi.DwmGetWindowAttribute.argtypes = [wt.HWND, wt.DWORD, ctypes.c_void_p, wt.DWORD]


# ------------------------------------------------------------ window info
def _proc_path(pid: int) -> str:
    if not IS_WIN or not pid:
        return ""
    h = kernel32.OpenProcess(0x1000, False, pid)      # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wt.DWORD(1024)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return buf.value
        return ""
    finally:
        kernel32.CloseHandle(h)


def _proc_name(pid: int) -> str:
    return os.path.basename(_proc_path(pid)).lower()


def foreground_path() -> str:
    """Full path of the active window's program ('' for our own windows)."""
    if not IS_WIN:
        return ""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == os.getpid():
        return ""
    return _proc_path(pid.value)


def foreground_info():
    """-> (exe_name_lowercase, window_title) of the active window."""
    if not IS_WIN:
        return "", ""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "", ""
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return _proc_name(pid.value), buf.value


def foreground_hkl():
    if not IS_WIN:
        return None
    hwnd = user32.GetForegroundWindow()
    tid = user32.GetWindowThreadProcessId(hwnd, None) if hwnd else 0
    return user32.GetKeyboardLayout(tid)


def _cloaked(hwnd) -> bool:
    if not dwmapi:
        return False
    v = wt.DWORD(0)
    try:
        dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(v), ctypes.sizeof(v))
    except Exception:
        return False
    return v.value != 0


def list_windows_full():
    """Visible top-level windows -> [(exe, title, full_path)]"""
    if not IS_WIN:
        return []
    out, own = [], os.getpid()

    def cb(hwnd, _lp):
        try:
            if user32.IsWindowVisible(hwnd):
                n = user32.GetWindowTextLengthW(hwnd)
                if n and not _cloaked(hwnd):
                    buf = ctypes.create_unicode_buffer(n + 1)
                    user32.GetWindowTextW(hwnd, buf, n + 1)
                    pid = wt.DWORD()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value != own:
                        path = _proc_path(pid.value)
                        if path:
                            out.append((os.path.basename(path).lower(), buf.value, path))
        except Exception:
            pass
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return sorted(set(out), key=lambda t: (t[0], t[1].lower()))


def list_windows():
    return [(e, t) for e, t, _p in list_windows_full()]


def async_down(vk: int) -> bool:
    if not IS_WIN:
        return True
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


# ------------------------------------------------------------ sending input
def _send(inputs) -> None:
    if not IS_WIN or not inputs:
        return
    arr = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))


def _kb(vk=0, scan=0, flags=0):
    i = INPUT(type=1)
    i.ki = KEYBDINPUT(vk, scan, flags, 0, 0)
    return i


def _key_input(vk: int, up: bool):
    flags = (0x0002 if up else 0) | (0x0001 if vk in _EXTENDED else 0)
    return _kb(vk, user32.MapVirtualKeyW(vk, 0), flags)


def key_down(vk: int) -> None:
    if IS_WIN:
        _send([_key_input(vk, False)])


def key_up(vk: int) -> None:
    if IS_WIN:
        _send([_key_input(vk, True)])


_MOD_VKS = ((1, VK_LCONTROL), (2, VK_LMENU), (4, VK_LSHIFT), (8, VK_LWIN))


def tap(mask: int, vk: int) -> None:
    """Press modifiers + key, then release everything."""
    if not IS_WIN:
        return
    seq = [_key_input(m, False) for bit, m in _MOD_VKS if mask & bit]
    seq.append(_key_input(vk, False))
    seq.append(_key_input(vk, True))
    seq += [_key_input(m, True) for bit, m in reversed(_MOD_VKS) if mask & bit]
    _send(seq)


def release_modifiers(vks) -> None:
    """Send key-up for modifiers the user is physically holding."""
    if not IS_WIN:
        return
    for vk in vks:
        if vk in (0xA4, 0xA5, 0x5B, 0x5C):          # Alt / Win would open a menu
            _send([_key_input(_MASK_KEY, False), _key_input(_MASK_KEY, True)])
        key_up(vk)


def press_modifiers(vks) -> None:
    for vk in vks:
        key_down(vk)


def _unicode_char(ch: str) -> None:
    data = ch.encode("utf-16-le")
    for i in range(0, len(data), 2):
        unit = int.from_bytes(data[i:i + 2], "little")
        _send([_kb(0, unit, 0x0004), _kb(0, unit, 0x0004 | 0x0002)])


def type_text(text: str, mode: str = "keys", hkl=None) -> None:
    if not IS_WIN:
        return
    for ch in text:
        if ch in "\r":
            continue
        if ch == "\n":
            tap(0, 0x0D)
        elif mode == "keys":
            r = user32.VkKeyScanExW(ch, hkl)
            vk, state = r & 0xFF, (r >> 8) & 0xFF
            if r == -1 or vk == 0xFF or state & 0x06:     # unmapped or needs Ctrl/AltGr
                _unicode_char(ch)
            else:
                tap(4 if state & 1 else 0, vk)
        else:
            _unicode_char(ch)
        time.sleep(0.005)


def click(button: str = "left", count: int = 1) -> None:
    if not IS_WIN:
        return
    down, up = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010), "middle": (0x0020, 0x0040)}[button]
    for _ in range(count):
        for flag in (down, up):
            i = INPUT(type=0)
            i.mi = MOUSEINPUT(0, 0, 0, flag, 0, 0)
            _send([i])
        time.sleep(0.03)


# ------------------------------------------------------------ keyboard hook
class KeyboardHook:
    """Low-level keyboard hook running on its own thread.

    handler(vk, is_down) -> True to swallow the key, False to let it through.
    Injected events (our own SendInput) are never passed to the handler.
    """

    def __init__(self, handler):
        self._handler = handler
        self._tid = 0
        self._hhook = None
        self._ready = threading.Event()
        self._proc = HOOKPROC(self._callback) if IS_WIN else None

    def start(self) -> None:
        if not IS_WIN:
            return
        threading.Thread(target=self._run, daemon=True, name="kbd-hook").start()
        self._ready.wait(2.0)

    def stop(self) -> None:
        if IS_WIN and self._tid:
            user32.PostThreadMessageW(self._tid, 0x0012, 0, 0)    # WM_QUIT

    def _callback(self, n_code, w_param, l_param):
        if n_code == 0:
            try:
                kb = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                if not (kb.flags & 0x10):                          # LLKHF_INJECTED
                    if w_param in (0x100, 0x104):
                        if self._handler(kb.vkCode, True):
                            return 1
                    elif w_param in (0x101, 0x105):
                        if self._handler(kb.vkCode, False):
                            return 1
            except Exception:
                pass
        return user32.CallNextHookEx(None, n_code, w_param, l_param)

    def _run(self) -> None:
        self._tid = kernel32.GetCurrentThreadId()
        msg = wt.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)     # create the message queue
        self._hhook = user32.SetWindowsHookExW(13, self._proc, kernel32.GetModuleHandleW(None), 0)
        self._ready.set()
        if not self._hhook:
            return
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            pass
        user32.UnhookWindowsHookEx(self._hhook)


# ------------------------------------------------------------ system helpers
_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def app_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --tray'
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        exe = exe[:-10] + "pythonw.exe"
    return f'"{exe}" "{os.path.abspath(sys.argv[0])}" --tray'


def set_startup(enabled: bool, command: str | None = None) -> None:
    if not IS_WIN:
        return
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
    try:
        if enabled:
            winreg.SetValueEx(key, "FXHotkeys", 0, winreg.REG_SZ, command or app_command())
        else:
            try:
                winreg.DeleteValue(key, "FXHotkeys")
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


def is_startup() -> bool:
    if not IS_WIN:
        return False
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, "FXHotkeys")
            return True
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def is_admin() -> bool:
    if not IS_WIN:
        return False
    try:
        return bool(shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> bool:
    if not IS_WIN:
        return False
    if getattr(sys, "frozen", False):
        exe, params = sys.executable, ""
    else:
        exe, params = sys.executable, f'"{os.path.abspath(sys.argv[0])}"'
    r = shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
    return (r or 0) > 32
