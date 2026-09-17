import 'package:flutter/material.dart';

/// A SwitchListTile variant that keeps long descriptions compact.
///
/// Collapsed: the description is limited to one line with an ellipsis.
/// Expanded: the complete description is shown and can be collapsed again.
/// The switch itself keeps the normal SwitchListTile behaviour.
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

class _CompactSwitchListTileState extends State<CompactSwitchListTile>
    with TickerProviderStateMixin {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final subtitle = widget.subtitle;

    return AnimatedSize(
      duration: const Duration(milliseconds: 180),
      curve: Curves.easeOut,
      alignment: Alignment.topCenter,
      vsync: this,
      child: SwitchListTile(
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
        secondary: widget.secondary,
        value: widget.value,
        onChanged: widget.onChanged,
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

    // Current settings use Text subtitles. Keep non-Text subtitles safe by
    // displaying them unchanged rather than attempting to introspect them.
    return subtitle;
  }
}
