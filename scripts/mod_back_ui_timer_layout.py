from pathlib import Path


def main():
    path = Path('app/lib/screens/app_settings_screen/widgets/general_tab.dart')
    s = path.read_text(encoding='utf-8')
    marker = 'class KeepUiOnBackTile extends StatefulWidget'
    if marker not in s:
        raise SystemExit('KeepUiOnBackTile not found')
    start = s.index(marker)
    tile = r'''class KeepUiOnBackTile extends StatefulWidget {
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
    path.write_text(s[:start] + tile, encoding='utf-8')


if __name__ == '__main__':
    main()
