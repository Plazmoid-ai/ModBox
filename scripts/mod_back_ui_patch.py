from pathlib import Path


def edit(path, transform):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    out = transform(s)
    if out == s:
        return
    p.write_text(out, encoding='utf-8')


def patch_main_activity(s):
    # Native helper: Android-side Handler keeps the delayed close alive while
    # the Activity is merely in the background. It is deliberately in this
    # patch script so the source stays reproducible.
    if 'private object ModBoxBackUiTimer' not in s:
        marker = 'class MainActivity'
        if marker not in s:
            raise SystemExit('MainActivity class insertion point not found')
        helper = '''private object ModBoxBackUiTimer {
    private val handler = android.os.Handler(android.os.Looper.getMainLooper())
    private var pending: Runnable? = null

    fun schedule(activity: android.app.Activity, delayMs: Long) {
        cancel()
        val task = Runnable { activity.finishAndRemoveTask() }
        pending = task
        handler.postDelayed(task, delayMs.coerceAtLeast(1000L))
    }

    fun cancel() {
        pending?.let(handler::removeCallbacks)
        pending = null
    }
}

'''
        s = s.replace(marker, helper + marker, 1)

    if '"scheduleBackUiClose" ->' not in s:
        marker = '''                    "setAutoRecordWifi" -> {
                        // §051 Phase 3 — start/stop WifiNetworkObserver
                        // (auto-record history). Toggle гейтится storage
                        // var `auto_record_wifi_history`; Dart-side читает
                        // его на init и при tap toggle, синкает сюда.
                        val enable = call.argument<Boolean>("enable") ?: false
                        if (enable) {
                            BoxApplication.wifiObserver.start()
                        } else {
                            BoxApplication.wifiObserver.stop()
                        }
                        result.success(null)
                    }
                    else -> result.notImplemented()
'''
        if marker not in s:
            raise SystemExit('MainActivity insertion point not found')
        insertion = '''                    "moveTaskToBack" -> {
                        result.success(moveTaskToBack(true))
                    }
                    "scheduleBackUiClose" -> {
                        val delayMs = call.argument<Number>("delayMs")?.toLong() ?: 0L
                        if (delayMs > 0L) {
                            ModBoxBackUiTimer.schedule(this, delayMs)
                        } else {
                            ModBoxBackUiTimer.cancel()
                        }
                        result.success(null)
                    }
                    "cancelBackUiClose" -> {
                        ModBoxBackUiTimer.cancel()
                        result.success(null)
                    }
                    else -> result.notImplemented()
'''
        if '"moveTaskToBack" ->' in s:
            insertion = insertion.replace('''                    "moveTaskToBack" -> {
                        result.success(moveTaskToBack(true))
                    }
''', '', 1)
        replacement = marker.replace(
            '                    else -> result.notImplemented()\n',
            insertion,
            1,
        )
        s = s.replace(marker, replacement, 1)
    return s


def patch_general(s):
    if 'class KeepUiOnBackTile extends StatefulWidget' not in s:
        s = s.replace(
            "import 'package:flutter/material.dart';\n",
            "import 'package:flutter/material.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\n",
            1,
        )
        marker = '''        // §220 — снятие портретной фиксации (планшетный фидбэк). Применяется
        // сразу, без рестарта; уважает системный auto-rotate.
'''
        if marker not in s:
            raise SystemExit('GeneralTab Behavior insertion point not found')
        s = s.replace(marker, '''        const KeepUiOnBackTile(),
'''+marker, 1)
        s += r'''

class KeepUiOnBackTile extends StatefulWidget {
  const KeepUiOnBackTile({super.key});

  @override
  State<KeepUiOnBackTile> createState() => _KeepUiOnBackTileState();
}

class _KeepUiOnBackTileState extends State<KeepUiOnBackTile> {
  static const _prefsKey = 'keep_ui_on_back';
  static const _timerPrefsKey = 'keep_ui_on_back_close_after_minutes';
  bool _enabled = false;
  int _minutes = 0;
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;
    setState(() {
      _enabled = prefs.getBool(_prefsKey) ?? false;
      _minutes = prefs.getInt(_timerPrefsKey) ?? 0;
      _loaded = true;
    });
  }

  Future<void> _setEnabled(bool value) async {
    setState(() => _enabled = value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefsKey, value);
  }

  Future<void> _editTimer() async {
    final controller = TextEditingController(
      text: _minutes <= 0
          ? ''
          : '${(_minutes ~/ 60).toString().padLeft(2, '0')}:${(_minutes % 60).toString().padLeft(2, '0')}',
    );
    final value = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Автоматическое закрытие'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.datetime,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Время',
            hintText: 'часы:минуты',
            prefixIcon: Icon(Icons.schedule),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, 0),
            child: const Text('Без таймера'),
          ),
          FilledButton(
            onPressed: () {
              final m = RegExp(r'^\s*(\d{1,3})\s*:\s*(\d{2})\s*$')
                  .firstMatch(controller.text);
              if (m == null) return;
              final hours = int.parse(m.group(1)!);
              final minutes = int.parse(m.group(2)!);
              if (minutes > 59 || (hours == 0 && minutes == 0)) return;
              Navigator.pop(context, hours * 60 + minutes);
            },
            child: const Text('Сохранить'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (value == null || !mounted) return;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_timerPrefsKey, value);
    setState(() => _minutes = value);
  }

  String get _timerLabel {
    if (_minutes <= 0) return 'Таймер не задан';
    final h = _minutes ~/ 60;
    final m = _minutes % 60;
    return 'Закрывать через ${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')} после выхода';
  }

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.exit_to_app),
      title: const Text('Сохранять интерфейс при выходе'),
      subtitle: Text(
        'Кнопка/жест «Назад» сворачивает приложение вместо закрытия интерфейса.\n$_timerLabel',
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            tooltip: 'Таймер',
            onPressed: _loaded && _enabled ? _editTimer : null,
            icon: const Icon(Icons.schedule),
          ),
          Switch(
            value: _enabled,
            onChanged: _loaded ? _setEnabled : null,
          ),
        ],
      ),
      isThreeLine: _minutes > 0,
    );
  }
}
'''
    else:
        # Upgrade the already-present tile to the timer-capable implementation.
        start = s.index('class KeepUiOnBackTile extends StatefulWidget')
        s = s[:start] + _timer_tile()
    return s


def _timer_tile():
    return r'''class KeepUiOnBackTile extends StatefulWidget {
  const KeepUiOnBackTile({super.key});

  @override
  State<KeepUiOnBackTile> createState() => _KeepUiOnBackTileState();
}

class _KeepUiOnBackTileState extends State<KeepUiOnBackTile> {
  static const _prefsKey = 'keep_ui_on_back';
  static const _timerPrefsKey = 'keep_ui_on_back_close_after_minutes';
  bool _enabled = false;
  int _minutes = 0;
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;
    setState(() {
      _enabled = prefs.getBool(_prefsKey) ?? false;
      _minutes = prefs.getInt(_timerPrefsKey) ?? 0;
      _loaded = true;
    });
  }

  Future<void> _setEnabled(bool value) async {
    setState(() => _enabled = value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefsKey, value);
  }

  Future<void> _editTimer() async {
    final controller = TextEditingController(
      text: _minutes <= 0
          ? ''
          : '${(_minutes ~/ 60).toString().padLeft(2, '0')}:${(_minutes % 60).toString().padLeft(2, '0')}',
    );
    final value = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Автоматическое закрытие'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.datetime,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Время',
            hintText: 'часы:минуты',
            prefixIcon: Icon(Icons.schedule),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, 0),
            child: const Text('Без таймера'),
          ),
          FilledButton(
            onPressed: () {
              final m = RegExp(r'^\s*(\d{1,3})\s*:\s*(\d{2})\s*$')
                  .firstMatch(controller.text);
              if (m == null) return;
              final hours = int.parse(m.group(1)!);
              final minutes = int.parse(m.group(2)!);
              if (minutes > 59 || (hours == 0 && minutes == 0)) return;
              Navigator.pop(context, hours * 60 + minutes);
            },
            child: const Text('Сохранить'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (value == null || !mounted) return;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_timerPrefsKey, value);
    setState(() => _minutes = value);
  }

  String get _timerLabel {
    if (_minutes <= 0) return 'Таймер не задан';
    final h = _minutes ~/ 60;
    final m = _minutes % 60;
    return 'Закрывать через ${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')} после выхода';
  }

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.exit_to_app),
      title: const Text('Сохранять интерфейс при выходе'),
      subtitle: Text(
        'Кнопка/жест «Назад» сворачивает приложение вместо закрытия интерфейса.\n$_timerLabel',
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            tooltip: 'Таймер',
            onPressed: _loaded && _enabled ? _editTimer : null,
            icon: const Icon(Icons.schedule),
          ),
          Switch(
            value: _enabled,
            onChanged: _loaded ? _setEnabled : null,
          ),
        ],
      ),
      isThreeLine: _minutes > 0,
    );
  }
}
'''


def patch_home(s):
    # Existing home file already has the Back patch. Add timer prefs/lifecycle
    # and native scheduling without disturbing navigator child-route behavior.
    if '_backUiTimerPrefsKey' not in s:
        marker = "  static const _keepUiOnBackPrefsKey = 'keep_ui_on_back';\n"
        if marker not in s:
            raise SystemExit('HomeScreen Back preference marker not found')
        s = s.replace(marker, marker + "  static const _backUiTimerPrefsKey = 'keep_ui_on_back_close_after_minutes';\n", 1)

    if 'void didChangeAppLifecycleState(AppLifecycleState state)' not in s:
        marker = '''  @override
  void initState() {
'''
        if marker not in s:
            raise SystemExit('HomeScreen initState marker not found')
        lifecycle = '''  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      unawaited(_cancelBackUiCloseTimer());
    }
  }

'''
        s = s.replace(marker, lifecycle + marker, 1)

    if 'Future<void> _cancelBackUiCloseTimer() async' not in s:
        marker = '''  Future<void> _handleSystemBack() async {
'''
        if marker not in s:
            raise SystemExit('HomeScreen Back handler not found')
        helpers = '''  Future<void> _cancelBackUiCloseTimer() async {
    try {
      await const MethodChannel('com.leadaxe.lxbox/utils')
          .invokeMethod<void>('cancelBackUiClose');
    } catch (_) {}
  }

  Future<void> _scheduleBackUiCloseTimer() async {
    final prefs = await SharedPreferences.getInstance();
    final minutes = prefs.getInt(_backUiTimerPrefsKey) ?? 0;
    if (minutes <= 0) return;
    final delayMs = minutes * 60 * 1000;
    try {
      await const MethodChannel('com.leadaxe.lxbox/utils').invokeMethod<void>(
        'scheduleBackUiClose',
        {'delayMs': delayMs},
      );
    } catch (_) {}
  }

'''
        s = s.replace(marker, helpers + marker, 1)

    old = '''      try {
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
        await SystemNavigator.pop();
      } catch (_) {
        await SystemNavigator.pop();
      }
'''
    new = '''      try {
        await _scheduleBackUiCloseTimer();
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
        await SystemNavigator.pop();
      } catch (_) {
        await SystemNavigator.pop();
      }
'''
    if old in s:
        s = s.replace(old, new, 1)
    else:
        raise SystemExit('HomeScreen moveTaskToBack block not found')

    return s


edit('app/android/app/src/main/kotlin/com/leadaxe/lxbox/MainActivity.kt', patch_main_activity)
edit('app/lib/screens/app_settings_screen/widgets/general_tab.dart', patch_general)
edit('app/lib/screens/home_screen.dart', patch_home)
