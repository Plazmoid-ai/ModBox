import 'package:flutter/material.dart';

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
