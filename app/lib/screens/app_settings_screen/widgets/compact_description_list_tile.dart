import 'package:flutter/material.dart';

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
