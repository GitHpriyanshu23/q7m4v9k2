# Editable architecture and workflow diagrams

Editable local sources and presentation previews for the implemented Windward pilot. **These files have not been imported into or created as new Lucidchart documents.** No existing Lucidchart diagram was overwritten.

- `windward-architecture.drawio`: editable shapes, labels, connectors, and deployment blocks.
- `windward-workflow.drawio`: editable decision, historical-context, retrospective-analysis, and export flow.
- `windward-architecture.svg` / `windward-workflow.svg`: scalable previews for viewing or presenting.
- `windward-architecture.png` / `windward-workflow.png`: rendered previews that open in ordinary image viewers.
- `../architecture.mmd` / `../workflow.mmd`: Mermaid source alternatives.

Open the `.drawio` files in diagrams.net to edit them. The SVG files can also be opened in a browser or vector editor.

Lucidchart supports importing `.drawio` files, but its documentation says free users can view imports while editing imported documents requires a paid plan. Its diagram-as-code Mermaid feature is also listed for paid plans. Do not purchase or change plans just to view these files.

If you later choose to import them, use Lucidchart's **New → Import documents** flow and verify the resulting diagram before sharing it. Preserve the distinction between the currently deployed Vercel app and the separate Docker runtime.

Official reference: https://help.lucid.co/hc/en-us/articles/16389149809428-Import-files-into-Lucidchart

Regenerate both formats with:

```sh
python scripts/build_explainer_diagrams.py
```
