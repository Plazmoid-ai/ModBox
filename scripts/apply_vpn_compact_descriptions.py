from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "app/lib/widgets/compact_description.dart"
SETTINGS = ROOT / "app/lib/screens/settings_screen.dart"
TEMPLATE = ROOT / "app/lib/widgets/template_var_list.dart"

helper = r'''import 'package:flutter/material.dart';

/// Long explanatory text is shown as one compact line and can be expanded.
/// Short descriptions are left unchanged.
class CompactDescription extends StatefulWidget {
  const CompactDescription(
    this.text, {
    super.key,
    this.style,
    this.collapseAbove = 140,
  });

  final String text;
  final TextStyle? style;
  final int collapseAbove;

  @override
  State<CompactDescription> createState() => _CompactDescriptionState();
}

class _CompactDescriptionState extends State<CompactDescription> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final compact = widget.text.length > widget.collapseAbove;
    if (!compact) {
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
  }
}
'''

HELPER.write_text(helper, encoding="utf-8")

settings = SETTINGS.read_text(encoding="utf-8")
if "compact_description.dart" not in settings:
    settings = settings.replace(
        "import '../widgets/template_var_list.dart';",
        "import '../widgets/template_var_list.dart';\nimport '../widgets/compact_description.dart';",
    )

replacements = {
'''subtitle: Text(getLocalText.s("Drop active connections when you switch nodes, so traffic moves to the new node immediately")),''':
'''subtitle: CompactDescription(getLocalText.s("Drop active connections when you switch nodes, so traffic moves to the new node immediately")),''',
'''Text(\n                getLocalText.s("Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use. Only affects tunnels not on the active route."),''':
'''CompactDescription(\n                getLocalText.s("Put unreachable WireGuard tunnels to sleep after they sit idle, freeing memory and saving battery. They wake instantly on use."),''',
'''Text(\n                  getLocalText.s("Also put tunnels on the active route (pool members, the selected node) to sleep after a long quiet period — e.g. overnight. The first connection after sleep adds ~1 round trip. Keep this at or above the directions' idle timeout (30 min by default). Requires \\"Suspend idle tunnels\\" to be on."),''':
'''CompactDescription(\n                  getLocalText.s("Also put tunnels on the active route (pool members, the selected node) to sleep after a long quiet period — e.g. overnight. The first connection after sleep adds ~1 round trip. Keep this at or above the directions' idle timeout (30 min by default). Requires \\"Suspend idle tunnels\\" to be on."),''',
'''subtitle: Text(getLocalText.s("Skip periodic server probes while your own traffic already proves the connection works. Fewer wakeups and less battery; ping numbers refresh less often.")),''':
'''subtitle: CompactDescription(getLocalText.s("Skip periodic server probes while your own traffic already proves the connection works. Fewer wakeups and less battery; ping numbers refresh less often.")),''',
'''Text(\n                getLocalText.s("Caps the VPN core's memory. A cap that is too low keeps the processor busy with garbage collection and heats the phone. Auto sizes the cap to this device's RAM; Off removes the cap but keeps low-memory monitoring. Applies immediately."),''':
'''CompactDescription(\n                getLocalText.s("Caps the VPN core's memory. A cap that is too low keeps the processor busy with garbage collection and heats the phone. Auto sizes the cap to this device's RAM; Off removes the cap but keeps low-memory monitoring. Applies immediately."),''',
'''Text(\n                getLocalText.s("When to pause the tunnel to save battery. Takes effect on next VPN connect."),''':
'''CompactDescription(\n                getLocalText.s("When to pause the tunnel to save battery. Takes effect on next VPN connect."),''',
'''subtitle: Text(getLocalText.s("Tunnel is always active. Best reliability — pushes and long-lived sockets survive. Higher battery use.")),''':
'''subtitle: CompactDescription(getLocalText.s("Tunnel is always active. Best reliability — pushes and long-lived sockets survive. Higher battery use.")),''',
'''subtitle: Text(getLocalText.s("Pause only in deep Doze (screen off for a long time + no motion). Balanced.")),''':
'''subtitle: CompactDescription(getLocalText.s("Pause only in deep Doze (screen off for a long time + no motion). Balanced.")),''',
'''subtitle: Text(getLocalText.s("Pause tunnel whenever screen turns off. Max battery savings, but pushes, incoming calls and background sync stop until unlock.")),''':
'''subtitle: CompactDescription(getLocalText.s("Pause tunnel whenever screen turns off. Max battery savings, but pushes, incoming calls and background sync stop until unlock.")),''',
}
for old, new in replacements.items():
    if old in settings:
        settings = settings.replace(old, new)

SETTINGS.write_text(settings, encoding="utf-8")

template = TEMPLATE.read_text(encoding="utf-8")
if "compact_description.dart" not in template:
    template = template.replace(
        "import 'var_values_model.dart';",
        "import 'var_values_model.dart';\nimport 'compact_description.dart';",
    )

template = template.replace(
'''subtitle: v.tooltip.isNotEmpty\n              ? Text(v.tooltip, style: const TextStyle(fontSize: 12))\n              : null,''',
'''subtitle: v.tooltip.isNotEmpty\n              ? CompactDescription(v.tooltip, style: const TextStyle(fontSize: 12))\n              : null,''',
)

template = template.replace(
'''Text(\n                description,\n                style: Theme.of(context).textTheme.bodySmall?.copyWith(''',
'''CompactDescription(\n                description,\n                style: Theme.of(context).textTheme.bodySmall?.copyWith(''',
)

template = template.replace(
'''Text(\n              tooltip,\n              style: theme.textTheme.bodySmall?.copyWith(''',
'''CompactDescription(\n              tooltip,\n              style: theme.textTheme.bodySmall?.copyWith(''',
)
TEMPLATE.write_text(template, encoding="utf-8")

print("Applied compact long-description UI to VPN settings and template-driven Core descriptions.")
