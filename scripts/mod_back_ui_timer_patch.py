from pathlib import Path


def edit(path, transform):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    out = transform(s)
    if out != s:
        p.write_text(out, encoding='utf-8')


def patch_main_activity(s):
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
        marker = '''                    "moveTaskToBack" -> {
                        result.success(moveTaskToBack(true))
                    }
'''
        if marker not in s:
            raise SystemExit('moveTaskToBack insertion point not found')
        insertion = marker + '''                    "scheduleBackUiClose" -> {
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
'''
        s = s.replace(marker, insertion, 1)
    return s


def patch_general(s):
    # The generated timer dialog uses Flutter's text input formatters.
    # Keep the required services import in the generated Dart source so
    # flutter build can resolve FilteringTextInputFormatter and
    # LengthLimitingTextInputFormatter.
    if "import 'package:flutter/services.dart';" not in s:
        material_import = "import 'package:flutter/material.dart';\n"
        if material_import not in s:
            raise SystemExit('Flutter material import not found in general_tab.dart')
        s = s.replace(
            material_import,
            material_import + "import 'package:flutter/services.dart';\n",
            1,
        )

    start_marker = 'class KeepUiOnBackTile extends StatefulWidget'
    if start_marker not in s:
        raise SystemExit('KeepUiOnBackTile not found')
    start = s.index(start_marker)
    s = s[:start] + r'''class KeepUiOnBackTile extends StatefulWidget {
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
    final hoursController = TextEditingController(
      text: _minutes <= 0 ? '' : (_minutes ~/ 60).toString(),
    );
    final minutesController = TextEditingController(
      text: _minutes <= 0 ? '' : (_minutes % 60).toString().padLeft(2, '0'),
    );

    final value = await showDialog<int>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Автоматическое закрытие'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Align(
              alignment: Alignment.centerLeft,
              child: Text('Закрыть интерфейс через:'),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: hoursController,
                    autofocus: true,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(3),
                    ],
                    decoration: const InputDecoration(
                      labelText: 'Часы',
                      hintText: '0',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 10),
                  child: Text(':', style: TextStyle(fontSize: 22)),
                ),
                Expanded(
                  child: TextField(
                    controller: minutesController,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(2),
                    ],
                    decoration: const InputDecoration(
                      labelText: 'Минуты',
                      hintText: '00',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Минуты: от 00 до 59',
                style: TextStyle(fontSize: 12),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, 0),
            child: const Text('Без таймера'),
          ),
          FilledButton(
            onPressed: () {
              final hours = int.tryParse(hoursController.text.trim()) ?? 0;
              final minutes = int.tryParse(minutesController.text.trim()) ?? 0;
              if (minutes > 59 || (hours == 0 && minutes == 0)) {
                ScaffoldMessenger.of(dialogContext).showSnackBar(
                  const SnackBar(
                    content: Text('Введите время больше 00:00, минуты 00–59.'),
                  ),
                );
                return;
              }
              Navigator.pop(dialogContext, hours * 60 + minutes);
            },
            child: const Text('Сохранить'),
          ),
        ],
      ),
    );

    hoursController.dispose();
    minutesController.dispose();
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
    return s


def patch_home(s):
    prefs_marker = "  static const _keepUiOnBackPrefsKey = 'keep_ui_on_back';\n"
    if '_backUiTimerPrefsKey' not in s:
        if prefs_marker not in s:
            raise SystemExit('HomeScreen Back preference marker not found')
        s = s.replace(
            prefs_marker,
            prefs_marker + "  static const _backUiTimerPrefsKey = 'keep_ui_on_back_close_after_minutes';\n",
            1,
        )

    helpers_added = 'Future<void> _cancelBackUiCloseTimer() async' in s
    if not helpers_added:
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
'''
        new = '''      try {
        await _scheduleBackUiCloseTimer();
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
'''
        if old not in s:
            raise SystemExit('HomeScreen moveTaskToBack block not found')
        s = s.replace(old, new, 1)

    lifecycle_marker = '''  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _lifecycle = state;
'''
    if 'unawaited(_cancelBackUiCloseTimer());' not in s:
        if lifecycle_marker not in s:
            raise SystemExit('HomeScreen lifecycle handler not found')
        s = s.replace(
            lifecycle_marker,
            lifecycle_marker + '    if (state == AppLifecycleState.resumed) {\n      unawaited(_cancelBackUiCloseTimer());\n    }\n',
            1,
        )
    return s


edit('app/android/app/src/main/kotlin/com/leadaxe/lxbox/MainActivity.kt', patch_main_activity)
edit('app/lib/screens/app_settings_screen/widgets/general_tab.dart', patch_general)
edit('app/lib/screens/home_screen.dart', patch_home)
