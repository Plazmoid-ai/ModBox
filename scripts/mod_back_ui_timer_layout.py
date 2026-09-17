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
    final initialHours = _minutes <= 0 ? '' : (_minutes ~/ 60).toString();
    final initialMinutes = _minutes <= 0 ? '' : (_minutes % 60).toString().padLeft(2, '0');
    final hoursController = TextEditingController(text: initialHours);
    final minutesController = TextEditingController(text: initialMinutes);
    String? error;

    final value = await showDialog<int>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setDialogState) => AlertDialog(
          title: const Text('Автоматическое закрытие интерфейса'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Через сколько времени после выхода закрыть интерфейс:'),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: hoursController,
                      keyboardType: TextInputType.number,
                      textInputAction: TextInputAction.next,
                      maxLength: 3,
                      decoration: const InputDecoration(
                        labelText: 'Часы',
                        hintText: '0',
                        counterText: '',
                      ),
                    ),
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    child: Text(':', style: TextStyle(fontSize: 24)),
                  ),
                  Expanded(
                    child: TextField(
                      controller: minutesController,
                      keyboardType: TextInputType.number,
                      textInputAction: TextInputAction.done,
                      maxLength: 2,
                      decoration: const InputDecoration(
                        labelText: 'Минуты',
                        hintText: '00',
                        counterText: '',
                      ),
                    ),
                  ),
                ],
              ),
              if (error != null) ...[
                const SizedBox(height: 10),
                Text(
                  error!,
                  style: TextStyle(color: Theme.of(dialogContext).colorScheme.error),
                ),
              ],
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
                final hoursText = hoursController.text.trim();
                final minutesText = minutesController.text.trim();
                final hours = int.tryParse(hoursText);
                final minutes = int.tryParse(minutesText);

                if (hours == null || hours < 0 || hours > 999) {
                  setDialogState(() => error = 'Введите часы от 0 до 999.');
                  return;
                }
                if (minutes == null || minutes < 0 || minutes > 59) {
                  setDialogState(() => error = 'Минуты должны быть от 0 до 59.');
                  return;
                }
                if (hours == 0 && minutes == 0) {
                  setDialogState(() => error = 'Укажите время больше 00:00.');
                  return;
                }
                Navigator.pop(dialogContext, hours * 60 + minutes);
              },
              child: const Text('Сохранить'),
            ),
          ],
        ),
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
          Switch(
            value: _enabled,
            onChanged: _loaded ? _setEnabled : null,
          ),
          IconButton(
            tooltip: 'Таймер',
            onPressed: _loaded && _enabled ? _editTimer : null,
            icon: const Icon(Icons.schedule),
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
