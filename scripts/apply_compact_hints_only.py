from pathlib import Path
import re

ROOT = Path(".")
W = ROOT / "app/lib/widgets"
AS = ROOT / "app/lib/screens/app_settings_screen/widgets"

compact_switch = r'''import 'package:flutter/material.dart';

/// Compact switch setting: the switch itself is the only on/off control.
/// Long descriptions stay available through a small expand/collapse control.
class CompactSwitchListTile extends StatefulWidget {
  const CompactSwitchListTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
    this.secondary,
    this.beforeSwitch,
    this.leading,
  });

  final Widget title;
  final Widget subtitle;
  final bool value;
  final ValueChanged<bool>? onChanged;
  final Widget? secondary;
  final Widget? beforeSwitch;
  final Widget? leading;

  @override
  State<CompactSwitchListTile> createState() => _CompactSwitchListTileState();
}

class _CompactSwitchListTileState extends State<CompactSwitchListTile> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final subtitle = widget.subtitle;

    return AnimatedSize(
      duration: const Duration(milliseconds: 180),
      curve: Curves.easeOut,
      alignment: Alignment.topCenter,
      child: ListTile(
        leading: widget.secondary ?? widget.leading,
        title: widget.title,
        subtitle: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _expanded
                  ? subtitle
                  : _collapsedSubtitle(subtitle),
            ),
            const SizedBox(width: 2),
            InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => setState(() => _expanded = !_expanded),
              child: Padding(
                padding: const EdgeInsets.all(4),
                child: Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  size: 18,
                ),
              ),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (widget.beforeSwitch != null) widget.beforeSwitch!,
            Switch(
              value: widget.value,
              onChanged: widget.onChanged,
            ),
          ],
        ),
      ),
    );
  }

  Widget _collapsedSubtitle(Widget subtitle) {
    if (subtitle is Text) {
      return Text(
        subtitle.data ?? '',
        style: subtitle.style,
        strutStyle: subtitle.strutStyle,
        textAlign: subtitle.textAlign,
        textDirection: subtitle.textDirection,
        locale: subtitle.locale,
        softWrap: false,
        overflow: TextOverflow.ellipsis,
        maxLines: 1,
      );
    }

    return subtitle;
  }
}
'''

compact_desc = r'''import 'package:flutter/material.dart';

/// Long explanatory text is shown as one compact line and can be expanded.
/// Short descriptions are left unchanged.
class CompactDescription extends StatefulWidget {
  const CompactDescription(
    this.text, {
    super.key,
    this.style,
    this.maxLinesBeforeCollapse = 3,
  });

  final String text;
  final TextStyle? style;
  final int maxLinesBeforeCollapse;

  @override
  State<CompactDescription> createState() => _CompactDescriptionState();
}

class _CompactDescriptionState extends State<CompactDescription> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final style = widget.style ?? DefaultTextStyle.of(context).style;

    return LayoutBuilder(
      builder: (context, constraints) {
        final available =
            (constraints.maxWidth - 28).clamp(0.0, double.infinity);
        final painter = TextPainter(
          text: TextSpan(text: widget.text, style: style),
          textDirection: Directionality.of(context),
          maxLines: widget.maxLinesBeforeCollapse,
        )..layout(maxWidth: available);
        final shouldCompact = painter.didExceedMaxLines;

        if (!shouldCompact) {
          return Text(widget.text, style: widget.style);
        }

        return AnimatedSize(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          alignment: Alignment.topCenter,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  widget.text,
                  style: widget.style,
                  softWrap: _expanded,
                  maxLines: _expanded ? null : 1,
                  overflow: _expanded
                      ? TextOverflow.visible
                      : TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 2),
              InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => setState(() => _expanded = !_expanded),
                child: Padding(
                  padding: const EdgeInsets.all(4),
                  child: Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    size: 18,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
'''

compact_list = r'''import 'package:flutter/material.dart';

/// List tile with a one-line collapsed description and an expand control.
/// The tile's original onTap behavior is preserved; only the description
/// expand/collapse control is separate.
class CompactDescriptionListTile extends StatefulWidget {
  const CompactDescriptionListTile({
    super.key,
    required this.title,
    required this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
  });

  final Widget title;
  final Widget subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  State<CompactDescriptionListTile> createState() =>
      _CompactDescriptionListTileState();
}

class _CompactDescriptionListTileState
    extends State<CompactDescriptionListTile> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final subtitle = widget.subtitle;

    return AnimatedSize(
      duration: const Duration(milliseconds: 180),
      curve: Curves.easeOut,
      alignment: Alignment.topCenter,
      child: ListTile(
        leading: widget.leading,
        title: widget.title,
        subtitle: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _expanded ? subtitle : _collapsedSubtitle(subtitle),
            ),
            const SizedBox(width: 2),
            InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => setState(() => _expanded = !_expanded),
              child: Padding(
                padding: const EdgeInsets.all(4),
                child: Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  size: 18,
                ),
              ),
            ),
          ],
        ),
        trailing: widget.trailing,
        onTap: widget.onTap,
      ),
    );
  }

  Widget _collapsedSubtitle(Widget subtitle) {
    if (subtitle is Text) {
      return Text(
        subtitle.data ?? '',
        style: subtitle.style,
        strutStyle: subtitle.strutStyle,
        textAlign: subtitle.textAlign,
        textDirection: subtitle.textDirection,
        locale: subtitle.locale,
        softWrap: false,
        overflow: TextOverflow.ellipsis,
        maxLines: 1,
      );
    }

    return subtitle;
  }
}
'''

(W / "compact_description.dart").write_text(compact_desc, encoding="utf-8")
(AS / "compact_switch_list_tile.dart").write_text(compact_switch, encoding="utf-8")
(AS / "compact_description_list_tile.dart").write_text(compact_list, encoding="utf-8")

def replace_once(p, old, new):
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise RuntimeError(f"target not found in {p}: {old[:100]}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

# General: compact switch settings only. Do not touch timer dialog/layout.
p = AS / "general_tab.dart"
s = p.read_text(encoding="utf-8")
if "compact_switch_list_tile.dart" not in s:
    s = s.replace(
        "import '../../../services/l10n/locale_controller.dart';",
        "import '../../../services/l10n/locale_controller.dart';\nimport 'compact_switch_list_tile.dart';",
        1,
    )
for title in [
    "Auto-start on boot",
    "Allow rotation",
    "Auto-restart VPN on settings change",
    "Check for updates on launch",
    "Auto-ping after connect",
    "Haptic feedback",
]:
    old = f'        SwitchListTile(\n          title: Text(getLocalText.s("{title}"))'
    new = f'        CompactSwitchListTile(\n          title: Text(getLocalText.s("{title}"))'
    if old not in s:
        raise RuntimeError(f"General target not found: {title}")
    s = s.replace(old, new, 1)

# Keep-ui tile: only its description UI is converted to the compact switch.
old = '''  @override
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
  }'''
new = '''  @override
  Widget build(BuildContext context) {
    return CompactSwitchListTile(
      title: const Text('Сохранять интерфейс при выходе'),
      subtitle: Text(
        'Кнопка/жест «Назад» сворачивает приложение вместо закрытия интерфейса.\\n$_timerLabel',
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
  }'''
if old not in s:
    raise RuntimeError("KeepUiOnBackTile build target not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

# Diagnostics: compact descriptions for the System setup list tiles.
p = AS / "diagnostics_tab.dart"
s = p.read_text(encoding="utf-8")
if "compact_description_list_tile.dart" not in s:
    s = s.replace(
        "import '../../../services/l10n/locale_controller.dart';",
        "import '../../../services/l10n/locale_controller.dart';\nimport 'compact_description_list_tile.dart';",
        1,
    )
start = s.find('Text(getLocalText.s("System setup")')
end = s.find('const Divider', start)
if start < 0 or end < 0:
    raise RuntimeError("Diagnostics System setup block not found")
block = s[start:end]
block2 = block.replace("ListTile(", "CompactDescriptionListTile(")
if block2 == block:
    raise RuntimeError("No Diagnostics tiles found")
s = s[:start] + block2 + s[end:]
p.write_text(s, encoding="utf-8")

# Quick connect: preserve original actions, only compact the descriptions.
p = AS / "general_tab.dart"
s = p.read_text(encoding="utf-8")
start = s.find('Text(getLocalText.s("Quick connect")')
end = s.find('const Divider', start)
block = s[start:end]
block2 = block.replace("ListTile(", "CompactDescriptionListTile(")
if block2 == block:
    raise RuntimeError("No Quick connect tiles found")
if "compact_description_list_tile.dart" not in s:
    s = s.replace(
        "import 'compact_switch_list_tile.dart';",
        "import 'compact_switch_list_tile.dart';\nimport 'compact_description_list_tile.dart';",
        1,
    )
s = s[:start] + block2 + s[end:]
p.write_text(s, encoding="utf-8")

# Subscriptions: compact switch descriptions; do not change HWID/device fields.
p = AS / "subscriptions_tab.dart"
s = p.read_text(encoding="utf-8")
if "compact_switch_list_tile.dart" not in s:
    s = s.replace(
        "import '../../../services/l10n/locale_controller.dart';",
        "import '../../../services/l10n/locale_controller.dart';\nimport 'compact_switch_list_tile.dart';",
        1,
    )
for title in ["Auto-update subscriptions", "Update disabled subscriptions", "Send HWID"]:
    old = f'        SwitchListTile(\n          title: Text(getLocalText.s("{title}"))'
    new = f'        CompactSwitchListTile(\n          title: Text(getLocalText.s("{title}"))'
    if old not in s:
        raise RuntimeError(f"Subscriptions target not found: {title}")
    s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

# VPN Settings: wrap only explanatory text, preserve exact text and behavior.
p = ROOT / "app/lib/screens/settings_screen.dart"
s = p.read_text(encoding="utf-8")
if "widgets/compact_description.dart" not in s:
    s = s.replace(
        "import '../widgets/template_var_list.dart';",
        "import '../widgets/template_var_list.dart';\nimport '../widgets/compact_description.dart';",
        1,
    )
pairs = [
    ('subtitle: Text(getLocalText.s("Drop active connections when you switch nodes, so traffic moves to the new node immediately"))',
     'subtitle: CompactDescription(getLocalText.s("Drop active connections when you switch nodes, so traffic moves to the new node immediately"))'),
    ('Text(\n                getLocalText.s("Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use. Only affects tunnels not on the active route."),',
     'CompactDescription(\n                getLocalText.s("Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use. Only affects tunnels not on the active route."),'),
    ('Text(\n                  getLocalText.s("Also put tunnels on the active route (pool members, the selected node) to sleep after a long quiet period — e.g. overnight. The first connection after sleep adds ~1 round trip. Keep this at or above the directions\' idle timeout (30 min by default). Requires \\"Suspend idle tunnels\\" to be on."),',
     'CompactDescription(\n                  getLocalText.s("Also put tunnels on the active route (pool members, the selected node) to sleep after a long quiet period — e.g. overnight. The first connection after sleep adds ~1 round trip. Keep this at or above the directions\' idle timeout (30 min by default). Requires \\"Suspend idle tunnels\\" to be on."),'),
    ('subtitle: Text(getLocalText.s("Skip periodic server probes while your own traffic already proves the connection works. Fewer wakeups and less battery; ping numbers refresh less often."))',
     'subtitle: CompactDescription(getLocalText.s("Skip periodic server probes while your own traffic already proves the connection works. Fewer wakeups and less battery; ping numbers refresh less often."))'),
    ('Text(\n                getLocalText.s("Caps the VPN core\'s memory. A cap that is too low keeps the processor busy with garbage collection and heats the phone. Auto sizes the cap to this device\'s RAM; Off removes the cap but keeps low-memory monitoring. Applies immediately."),',
     'CompactDescription(\n                getLocalText.s("Caps the VPN core\'s memory. A cap that is too low keeps the processor busy with garbage collection and heats the phone. Auto sizes the cap to this device\'s RAM; Off removes the cap but keeps low-memory monitoring. Applies immediately."),'),
    ('Text(\n                getLocalText.s("When to pause the tunnel to save battery. Takes effect on next VPN connect."),',
     'CompactDescription(\n                getLocalText.s("When to pause the tunnel to save battery. Takes effect on next VPN connect."),'),
    ('subtitle: Text(getLocalText.s("Tunnel is always active. Best reliability — pushes and long-lived sockets survive. Higher battery use."))',
     'subtitle: CompactDescription(getLocalText.s("Tunnel is always active. Best reliability — pushes and long-lived sockets survive. Higher battery use."))'),
    ('subtitle: Text(getLocalText.s("Pause only in deep Doze (screen off for a long time + no motion). Balanced."))',
     'subtitle: CompactDescription(getLocalText.s("Pause only in deep Doze (screen off for a long time + no motion). Balanced."))'),
    ('subtitle: Text(getLocalText.s("Pause tunnel whenever screen turns off. Max battery savings, but pushes, incoming calls and background sync stop until unlock."))',
     'subtitle: CompactDescription(getLocalText.s("Pause tunnel whenever screen turns off. Max battery savings, but pushes, incoming calls and background sync stop until unlock."))'),
]
for old,new in pairs:
    if old not in s:
        raise RuntimeError("VPN Settings target not found: " + old[:90])
    s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")

# VPN Mode: compact the mode explanation.
p = ROOT / "app/lib/screens/vpn_mode_tab.dart"
s = p.read_text(encoding="utf-8")
if "../widgets/compact_description.dart" not in s:
    s = s.replace(
        "import 'lazy_persist_mixin.dart';",
        "import 'lazy_persist_mixin.dart';\nimport '../widgets/compact_description.dart';",
        1,
    )
old = '''        Text(
          _modeDescription(_cfg.mode),
          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
        ),'''
new = '''        CompactDescription(
          _modeDescription(_cfg.mode),
          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
        ),'''
if old not in s:
    raise RuntimeError("VPN Mode description target not found")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")

# Template-driven Core descriptions.
p = ROOT / "app/lib/widgets/template_var_list.dart"
s = p.read_text(encoding="utf-8")
if "compact_description.dart" not in s:
    s = s.replace(
        "import 'var_values_model.dart';",
        "import 'var_values_model.dart';\nimport 'compact_description.dart';",
        1,
    )
s=s.replace(
'''subtitle: v.tooltip.isNotEmpty
              ? Text(v.tooltip, style: const TextStyle(fontSize: 12))
              : null,''',
'''subtitle: v.tooltip.isNotEmpty
              ? CompactDescription(v.tooltip, style: const TextStyle(fontSize: 12))
              : null,''',1)
s=s.replace(
'''child: Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(''',
'''child: CompactDescription(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(''',1)
s=s.replace(
'''Text(
              tooltip,
              style: theme.textTheme.bodySmall?.copyWith(''',
'''CompactDescription(
              tooltip,
              style: theme.textTheme.bodySmall?.copyWith(''',1)
p.write_text(s,encoding="utf-8")

print("compact hint changes applied")
