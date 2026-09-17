import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../main.dart';
import '../../../services/l10n/locale_controller.dart';
import 'compact_description_list_tile.dart';
import 'compact_switch_list_tile.dart';
import 'update_status_row.dart';

/// General tab для App Settings.
class GeneralTab extends StatelessWidget {
  const GeneralTab({
    super.key,
    required this.loaded,
    required this.autoStart,
    required this.autoCheckUpdates,
    required this.autoPing,
    required this.haptic,
    required this.allowRotation,
    required this.autoReloadOnChange,
    required this.padding,
    required this.onAutoStartChanged,
    required this.onAutoCheckUpdatesChanged,
    required this.onAutoPingChanged,
    required this.onHapticChanged,
    required this.onAllowRotationChanged,
    required this.onAutoReloadOnChangeChanged,
    required this.onAddQuickSettingsTile,
    required this.onOpenBackup,
    required this.region,
    required this.detectedRegion,
    required this.onEditRegion,
  });

  final bool loaded;
  final bool autoStart;
  final bool autoCheckUpdates;
  final bool autoPing;
  final bool haptic;
  final bool allowRotation;
  final bool autoReloadOnChange;
  final EdgeInsets padding;

  final ValueChanged<bool> onAutoStartChanged;
  final ValueChanged<bool> onAutoCheckUpdatesChanged;
  final ValueChanged<bool> onAutoPingChanged;
  final ValueChanged<bool> onHapticChanged;
  final ValueChanged<bool> onAllowRotationChanged;
  final ValueChanged<bool> onAutoReloadOnChangeChanged;
  final VoidCallback onAddQuickSettingsTile;
  final VoidCallback onOpenBackup;
  final String region;
  final String detectedRegion;
  final VoidCallback onEditRegion;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: padding,
      children: [
        Text(getLocalText.s("Appearance"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        RadioGroup<ThemeMode>(
          groupValue: themeNotifier.mode,
          onChanged: (v) { if (v != null) themeNotifier.setMode(v); },
          child: Column(
            children: ThemeMode.values.map((mode) {
              final label = switch (mode) {
                ThemeMode.system => 'System',
                ThemeMode.light => 'Light',
                ThemeMode.dark => 'Dark',
              };
              final icon = switch (mode) {
                ThemeMode.system => Icons.brightness_auto,
                ThemeMode.light => Icons.light_mode,
                ThemeMode.dark => Icons.dark_mode,
              };
              return RadioListTile<ThemeMode>(
                value: mode,
                title: Text(label),
                secondary: Icon(icon),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
        Text(getLocalText.s("Language"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        RadioGroup<String>(
          groupValue: LocaleController.I.setting,
          onChanged: (v) { if (v != null) LocaleController.I.set(v); },
          child: Column(
            children: [
              RadioListTile<String>(
                value: 'system',
                title: Text(getLocalText.s("System default")),
                secondary: const Icon(Icons.language),
              ),
              const RadioListTile<String>(
                value: 'en',
                title: Text('English'),
              ),
              const RadioListTile<String>(
                value: 'ru',
                title: Text('Русский'),
              ),
              const RadioListTile<String>(
                value: 'zh',
                title: Text('中文（简体）'),
              ),
            ],
          ),
        ),
        const Divider(height: 32),
        Text(getLocalText.s("Region"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ListTile(
          leading: const Icon(Icons.public_outlined),
          title: Text(getLocalText.s("Usage region")),
          subtitle: Text(regionLabel(region, detectedRegion)),
          trailing: const Icon(Icons.edit_outlined),
          onTap: loaded ? onEditRegion : null,
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
          child: Text(
            getLocalText.s("The country you use the app in. Drives region-specific defaults: today the WARP SNI pool, later routing rule presets. Auto = country of the mobile network, then of the device locale."),
            style: TextStyle(
                fontSize: 11,
                color: Theme.of(context).colorScheme.onSurfaceVariant),
          ),
        ),
        const Divider(height: 32),
        Text(getLocalText.s("Behavior"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Auto-start on boot")),
          subtitle: Text(getLocalText.s("Start VPN when device turns on")),
          secondary: const Icon(Icons.power_settings_new),
          value: autoStart,
          onChanged: loaded ? onAutoStartChanged : null,
        ),
        const KeepUiOnBackTile(),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Allow rotation")),
          subtitle: Text(getLocalText.s("Rotate to landscape when the device turns — handy on tablets. Follows the system auto-rotate setting.")),
          secondary: const Icon(Icons.screen_rotation),
          value: allowRotation,
          onChanged: loaded ? onAllowRotationChanged : null,
        ),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Auto-restart VPN on settings change")),
          subtitle: Text(getLocalText.s("Apply every config change to the running tunnel by itself, so no banner is left to tap. Each apply drops the tunnel for about 3 seconds and kills open connections.")),
          secondary: const Icon(Icons.restart_alt),
          value: autoReloadOnChange,
          onChanged: loaded ? onAutoReloadOnChangeChanged : null,
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
          child: Text(
            getLocalText.s("While this is on, the per-subscription \"On update\" setting is hidden — everything is applied immediately. Turning it off brings each subscription's own choice back."),
            style: TextStyle(
              fontSize: 11,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        const Divider(height: 32),
        Text(getLocalText.s("Quick connect"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        CompactDescriptionListTile(
          leading: const Icon(Icons.dashboard_customize_outlined),
          title: Text(getLocalText.s("Quick Settings tile")),
          subtitle: Text(getLocalText.s("Add to status-bar shade for one-tap toggle. Android 13+ shows a system prompt; on older versions edit the shade manually.")),
          trailing: TextButton(
            onPressed: onAddQuickSettingsTile,
            child: Text(getLocalText.s("Add")),
          ),
        ),
        CompactDescriptionListTile(
          leading: const Icon(Icons.touch_app_outlined),
          title: Text(getLocalText.s("Home-screen shortcut")),
          subtitle: Text(getLocalText.s("Long-press the L×Box icon on your home screen → choose \"Toggle VPN\".")),
        ),
        const Divider(height: 32),
        Text(getLocalText.s("Updates"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Check for updates on launch")),
          subtitle: Text(getLocalText.s("Pings github.com once a day to check for new releases. \"View\" opens the release page in browser; install is manual.")),
          secondary: const Icon(Icons.system_update_alt),
          value: autoCheckUpdates,
          onChanged: loaded ? onAutoCheckUpdatesChanged : null,
        ),
        const UpdateStatusRow(),
        const Divider(height: 32),
        Text(getLocalText.s("Feedback"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Auto-ping after connect")),
          subtitle: Text(getLocalText.s("Ping nodes of active group 5s after VPN starts (once per connect)")),
          secondary: const Icon(Icons.network_ping),
          value: autoPing,
          onChanged: loaded ? onAutoPingChanged : null,
        ),
        CompactSwitchListTile(
          title: Text(getLocalText.s("Haptic feedback")),
          subtitle: Text(getLocalText.s("Vibrate on connect, disconnect and errors. Respects system \"Touch feedback\" setting")),
          secondary: const Icon(Icons.vibration),
          value: haptic,
          onChanged: loaded ? onHapticChanged : null,
        ),
        const Divider(height: 32),
        Text(getLocalText.s("Backup & restore"),
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ListTile(
          leading: const Icon(Icons.import_export),
          title: Text(getLocalText.s("Backup & restore")),
          subtitle: Text(getLocalText.s("Export subscriptions, routing setup and preferences as JSON.")),
          trailing: const Icon(Icons.chevron_right),
          contentPadding: EdgeInsets.zero,
          onTap: onOpenBackup,
        ),
      ],
    );
  }

  static String regionLabel(String region, String detected) {
    if (region == 'none') return getLocalText.s("Not set");
    if (region == 'auto') {
      return detected.isEmpty
          ? getLocalText.s("Auto · country not detected")
          : getLocalText.s("Auto · %s", detected.toUpperCase());
    }
    return region.toUpperCase();
  }
}

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
                      maxLength: 2,
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
                Text(error!, style: TextStyle(color: Theme.of(dialogContext).colorScheme.error)),
              ],
              Align(
                alignment: Alignment.centerLeft,
                child: TextButton(
                  onPressed: () => Navigator.pop(dialogContext, 0),
                  child: const Text('Без таймера'),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Отмена'),
            ),
            FilledButton(
              onPressed: () {
                final hours = int.tryParse(hoursController.text.trim());
                final minutes = int.tryParse(minutesController.text.trim());
                if (hours == null || hours < 0 || hours > 99) {
                  setDialogState(() => error = 'Введите часы от 0 до 99.');
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
    return CompactSwitchListTile(
      leading: null,
      title: const Text('Сохранять интерфейс при выходе'),
      subtitle: Text(
        'Кнопка/жест «Назад» сворачивает приложение вместо закрытия интерфейса.\n$_timerLabel',
      ),
      secondary: const Icon(Icons.exit_to_app),
      value: _enabled,
      onChanged: _loaded ? _setEnabled : null,
      beforeSwitch: IconButton(
        tooltip: 'Таймер',
        onPressed: _loaded && _enabled ? _editTimer : null,
        icon: const Icon(Icons.schedule),
      ),
    );
  }
}
