from pathlib import Path


def edit(path, transform):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    out = transform(s)
    if out == s:
        return
    p.write_text(out, encoding='utf-8')


def patch_main_activity(s):
    if '"moveTaskToBack" ->' in s:
        return s
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
    return s.replace(marker, marker.replace(
        '                    else -> result.notImplemented()\n',
        '                    "moveTaskToBack" -> {\n                        result.success(moveTaskToBack(true))\n                    }\n                    else -> result.notImplemented()\n',
        1,
    ), 1)


def patch_general(s):
    if 'class KeepUiOnBackTile extends StatefulWidget' in s:
        return s
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
    return s + r'''

class KeepUiOnBackTile extends StatefulWidget {
  const KeepUiOnBackTile({super.key});

  @override
  State<KeepUiOnBackTile> createState() => _KeepUiOnBackTileState();
}

class _KeepUiOnBackTileState extends State<KeepUiOnBackTile> {
  static const _prefsKey = 'keep_ui_on_back';
  bool _enabled = false;
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
      _loaded = true;
    });
  }

  Future<void> _setEnabled(bool value) async {
    setState(() => _enabled = value);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefsKey, value);
  }

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      // l10n-exempt: personal ModBox fork setting is intentionally Russian.
      title: const Text('Сохранять интерфейс при выходе'),
      // l10n-exempt: personal ModBox fork setting is intentionally Russian.
      subtitle: const Text('Кнопка/жест «Назад» сворачивает приложение вместо закрытия интерфейса.'),
      secondary: const Icon(Icons.exit_to_app),
      value: _enabled,
      onChanged: _loaded ? _setEnabled : null,
    );
  }
}
'''


def patch_home(s):
    if 'Future<void> _handleSystemBack() async' in s:
        return s
    s = s.replace(
        "import 'package:flutter/material.dart';\n",
        "import 'package:flutter/material.dart';\nimport 'package:flutter/services.dart';\nimport 'package:shared_preferences/shared_preferences.dart';\n",
        1,
    )
    marker = '''  Future<void>? _rebuildInFlight;
'''
    if marker not in s:
        raise SystemExit('HomeScreen field insertion point not found')
    s = s.replace(marker, marker + '''
  static const _keepUiOnBackPrefsKey = 'keep_ui_on_back';
  bool _backHandling = false;

''', 1)
    build_marker = '''  @override
  Widget build(BuildContext context) {
'''
    helper = '''  Future<void> _handleSystemBack() async {
    if (_backHandling) return;
    _backHandling = true;
    try {
      final navigator = Navigator.of(context);
      if (navigator.canPop()) {
        navigator.pop();
        return;
      }

      final prefs = await SharedPreferences.getInstance();
      final keepUi = prefs.getBool(_keepUiOnBackPrefsKey) ?? false;
      if (!mounted) return;

      if (!keepUi) {
        await SystemNavigator.pop();
        return;
      }

      try {
        await const MethodChannel('com.leadaxe.lxbox/utils')
            .invokeMethod<bool>('moveTaskToBack');
      } on PlatformException {
        await SystemNavigator.pop();
      } catch (_) {
        await SystemNavigator.pop();
      }
    } finally {
      _backHandling = false;
    }
  }

'''
    if build_marker not in s:
        raise SystemExit('HomeScreen build insertion point not found')
    s = s.replace(build_marker, helper + build_marker, 1)
    start = '''    return AnimatedBuilder(
'''
    if start not in s:
        raise SystemExit('HomeScreen AnimatedBuilder start not found')
    s = s.replace(start, '''    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) unawaited(_handleSystemBack());
      },
      child: AnimatedBuilder(
''', 1)
    tail = '''    );
  }

  /// Rebuild config → reconnect'''
    if tail not in s:
        raise SystemExit('HomeScreen build tail not found')
    s = s.replace(tail, '''      ),
    );
  }

  /// Rebuild config → reconnect''', 1)
    return s


edit('app/android/app/src/main/kotlin/com/leadaxe/lxbox/MainActivity.kt', patch_main_activity)
edit('app/lib/screens/app_settings_screen/widgets/general_tab.dart', patch_general)
edit('app/lib/screens/home_screen.dart', patch_home)
