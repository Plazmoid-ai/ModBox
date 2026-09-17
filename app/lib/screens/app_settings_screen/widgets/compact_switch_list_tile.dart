import 'package:flutter/material.dart';

/// A compact switch setting that keeps the switch itself as the only
/// on/off control. Long descriptions can be expanded without changing the
/// behaviour of the rest of the settings row.
class CompactSwitchListTile extends StatefulWidget {
  const CompactSwitchListTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
    this.secondary,
  });

  final Widget title;
  final Widget subtitle;
  final bool value;
  final ValueChanged<bool>? onChanged;
  final Widget? secondary;

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
        leading: widget.secondary,
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
        trailing: Switch(
          value: widget.value,
          onChanged: widget.onChanged,
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

    // Keep non-Text subtitles safe rather than attempting to introspect them.
    return subtitle;
  }
}
