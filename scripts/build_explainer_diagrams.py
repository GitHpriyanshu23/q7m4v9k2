"""Render the reviewed architecture/workflow as editable draw.io and SVG files.

Standard-library only. Each SVG and draw.io page shares node geometry and text.
Run: python scripts/build_explainer_diagrams.py
"""
from dataclasses import dataclass
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parents[1] / "docs" / "diagrams"
GREEN = "#285840"
TEXT = "#243e30"
MUTED = "#64786a"
LINE = "#9aafa0"


@dataclass
class Node:
    key: str
    x: int
    y: int
    w: int
    h: int
    title: str
    lines: list[str]
    tone: str = "white"


def colors(tone):
    return {"white": ("#ffffff", "#cbd8c9"), "green": ("#edf3e7", "#9eb391"),
            "amber": ("#fcf6e9", "#d3b784"), "dark": ("#285840", "#285840")}[tone]


def render(name, title, subtitle, height, nodes, edges, bands=(), footnote=""):
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}">',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#819889"/></marker></defs>',
           '<rect width="1440" height="100%" fill="#fafbf7"/>',
           f'<text x="48" y="45" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="2" fill="{GREEN}">WINDWARD / TECHNICAL HANDOVER</text>',
           f'<text x="48" y="88" font-family="Georgia,serif" font-size="34" fill="{TEXT}">{escape(title)}</text>',
           f'<text x="48" y="118" font-family="Arial,sans-serif" font-size="15" fill="{MUTED}">{escape(subtitle)}</text>']
    mx = ET.Element("mxfile", {"host": "app.diagrams.net", "version": "24.7.17", "type": "device"})
    diagram = ET.SubElement(mx, "diagram", {"id": name, "name": title})
    model = ET.SubElement(diagram, "mxGraphModel", {"dx": "1440", "dy": str(height), "grid": "1", "gridSize": "10", "page": "1", "pageScale": "1", "pageWidth": "1440", "pageHeight": str(height), "math": "0", "shadow": "0"})
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def cell(key, x, y, w, h, value, style):
        c = ET.SubElement(root, "mxCell", {"id": key, "value": value, "style": style, "vertex": "1", "parent": "1"})
        ET.SubElement(c, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

    cell("heading", 48, 20, 1330, 105, f'<b>{escape(title)}</b><br>{escape(subtitle)}', "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=26;fontColor=#243e30;")
    for index, (x, y, w, h, label, tone) in enumerate(bands):
        fill = "#f0f4eb" if tone == "green" else "#f5f6f1"
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="{fill}" stroke="#dce4d8"/>')
        svg.append(f'<text x="{x+22}" y="{y+31}" font-family="Arial,sans-serif" font-size="12" font-weight="700" letter-spacing="1.5" fill="{MUTED}">{escape(label)}</text>')
        cell(f"band-{index}", x, y, w, h, label, f"rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacing=18;fillColor={fill};strokeColor=#dce4d8;fontSize=12;fontStyle=1;fontColor=#64786a;")

    for index, (points, label, label_x, label_y, dashed) in enumerate(edges):
        path = "M" + " L".join(f"{x} {y}" for x, y in points)
        dash = ' stroke-dasharray="5 5"' if dashed else ""
        svg.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="2" marker-end="url(#arrow)"{dash}/>')
        if label:
            width = len(label) * 7 + 14
            svg.append(f'<rect x="{label_x-width/2}" y="{label_y-15}" width="{width}" height="22" rx="3" fill="#fafbf7"/>')
            svg.append(f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="{MUTED}">{escape(label)}</text>')
        edge = ET.SubElement(root, "mxCell", {"id": f"edge-{index}", "value": label, "style": f"edgeStyle=none;html=1;endArrow=block;endFill=1;strokeColor={LINE};strokeWidth=2;fontSize=12;fontColor={MUTED};labelBackgroundColor=#fafbf7;dashed={int(dashed)};", "edge": "1", "parent": "1"})
        for endpoint, attribute, prefix in ((points[0], "source", "exit"), (points[-1], "target", "entry")):
            px, py = endpoint
            attached = next((n for n in nodes if n.x <= px <= n.x+n.w and n.y <= py <= n.y+n.h), None)
            if attached:
                edge.set(attribute, attached.key)
                edge.set("style", edge.get("style") + f"{prefix}X={(px-attached.x)/attached.w};{prefix}Y={(py-attached.y)/attached.h};{prefix}Dx=0;{prefix}Dy=0;")
        geo = ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        ET.SubElement(geo, "mxPoint", {"x": str(points[0][0]), "y": str(points[0][1]), "as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", {"x": str(points[-1][0]), "y": str(points[-1][1]), "as": "targetPoint"})
        if len(points) > 2:
            arr = ET.SubElement(geo, "Array", {"as": "points"})
            for x, y in points[1:-1]:
                ET.SubElement(arr, "mxPoint", {"x": str(x), "y": str(y)})

    for node in nodes:
        fill, stroke = colors(node.tone)
        color = "#ffffff" if node.tone == "dark" else TEXT
        muted = "#e4eddf" if node.tone == "dark" else MUTED
        svg.append(f'<rect x="{node.x}" y="{node.y}" width="{node.w}" height="{node.h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        svg.append(f'<text x="{node.x+18}" y="{node.y+29}" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="{color}">{escape(node.title)}</text>')
        for i, line in enumerate(node.lines):
            svg.append(f'<text x="{node.x+18}" y="{node.y+55+i*22}" font-family="Arial,sans-serif" font-size="14" fill="{muted}">{escape(line)}</text>')
        value = f'<b>{escape(node.title)}</b><br>' + '<br>'.join(escape(line) for line in node.lines)
        cell(node.key, node.x, node.y, node.w, node.h, value, f"rounded=1;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacing=18;fillColor={fill};strokeColor={stroke};fontColor={color};fontFamily=Arial;fontSize=15;")
    if footnote:
        svg.append(f'<text x="48" y="{height-25}" font-family="Arial,sans-serif" font-size="12" fill="{MUTED}">{escape(footnote)}</text>')
        cell("footnote", 48, height-50, 1340, 38, escape(footnote), "text;html=1;align=left;whiteSpace=wrap;fontSize=12;fontColor=#64786a;")
    svg.append('</svg>')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text("\n".join(svg))
    ET.indent(mx)
    ET.ElementTree(mx).write(OUT / f"{name}.drawio", encoding="utf-8", xml_declaration=True)
    print(f"Generated {name}.svg and {name}.drawio")


def architecture():
    nodes = [
        Node("sources", 70, 210, 330, 120, "Elexon public APIs", ["WINDFOR: forecast + publication time", "FUELHH: half-hour actuals, WIND only", "No additional market datasets"], "green"),
        Node("ingest", 555, 210, 330, 120, "Offline ingestion", ["scripts/ingest.py — manual run", "Download, retry, validate, normalize", "No download on a dashboard request"]),
        Node("snapshot", 1040, 210, 330, 120, "Bundled evidence", ["windfor.json.gz + fuelhh.json.gz", "manifest.json: URLs, time, counts, hashes", "Fixed historical snapshot; no database"], "green"),
        Node("react", 70, 470, 330, 140, "Buyer / React browser app", ["Date, cutoff, date range, view selection", "Recharts, audit trail, actuals toggle", "TypeScript + Vite; same-origin requests", "Does not calculate accuracy formulas"]),
        Node("api", 555, 470, 330, 140, "Python FastAPI", ["backend/main.py + api/index.py", "Validate request; call analysis functions", "Decision, performance, metadata, CSV", "Return computed JSON or CSV"]),
        Node("analysis", 1040, 470, 330, 140, "Pure analysis functions", ["backend/analysis.py", "Latest publication at/before cutoff", "Average two half-hour actuals", "MAE, RMSE, bias, shortfall, coverage"], "green"),
        Node("cache", 1040, 685, 330, 100, "Memory cache / indexes", ["Lazy load per Python process", "Snapshot indexes + selected-day results"]),
        Node("timing", 70, 685, 815, 100, "Two separate information views", ["Decision context: earlier decisions and actual versions available by current cutoff.", "Retrospective review: latest actual versions in the bundled snapshot."], "amber"),
        Node("vercel", 70, 890, 630, 120, "Current public deployment — Vercel", ["Static React assets served by Vercel", "/api/* rewrites to a Python function exposing FastAPI", "Snapshot files are included in the function bundle"], "green"),
        Node("docker", 740, 890, 630, 120, "Separate container path — Docker", ["Node build stage creates the React production files", "Non-root Python + Uvicorn serves UI and API together", "Docker Compose gives one-command local startup"]),
    ]
    edges = [
        ([(400,270),(555,270)],"Public data",478,252,False),
        ([(885,270),(1040,270)],"Validated files",962,252,False),
        ([(400,515),(555,515)],"GET /api/*",478,498,False),
        ([(555,570),(400,570)],"JSON / CSV",478,553,False),
        ([(885,515),(1040,515)],"Parameters",962,498,False),
        ([(1040,570),(885,570)],"Results",962,553,False),
        ([(1370,285),(1390,285),(1390,735),(1370,735)],"",0,0,True),
        ([(1205,685),(1205,610)],"Indexed data",1275,651,False),
    ]
    render("windward-architecture", "How Windward is built", "Offline preparation is separate from interactive analysis. Vercel and Docker are different deployment paths.", 1100, nodes, edges,
           [(40,160,1360,220,"01 / OFFLINE DATA PREPARATION", "green"),(40,410,1360,410,"02 / INTERACTIVE REQUEST AND ANALYSIS", "white"),(40,840,1360,205,"03 / TWO WAYS TO RUN THE SAME APPLICATION", "white")],
           "Source: implemented repository. Pilot has no live ingestion scheduler, shared database, trained wind model, or trade execution.")


def workflow():
    nodes = [
        Node("select",555,175,330,100,"1. Select the decision",["January date + cutoff (09:00 default)","Delivery is the following day"],"dark"),
        Node("validate",555,325,330,100,"2. Validate and load",["FastAPI checks dates and time", "Use cached indexes of bundled data"]),
        Node("forecast",555,475,330,120,"3. Reconstruct the forecast",["For each next-day delivery hour:","latest publication at/before cutoff", "No eligible forecast stays missing"],"green"),
        Node("display",555,665,330,120,"4. Show the buying outlook",["Forecast curve and energy total", "Publication age, lead time, audit trail", "Prior context shown alongside"]),
        Node("prior",65,475,330,120,"Earlier January decisions",["Only decisions before the chosen date", "Use the same selected cutoff policy", "No full-month hindsight"]),
        Node("asof",65,665,330,120,"Actuals available at cutoff",["Only versions already published", "Average both actual half-hours", "Exclude future hours and revisions"]),
        Node("context",65,855,330,120,"Prior-history context",["MAE, bias, P90 shortfall and count", "Descriptive sample history only", "Not a guaranteed reserve"],"green"),
        Node("actual",1045,475,330,120,"Retrospective actuals",["Latest versions in fixed snapshot", "Never presented as known beforehand", "Not an additional live data fetch"],"amber"),
        Node("align",1045,665,330,120,"Align actuals to the hour",["Mean of HH:00 and HH:30 actuals", "Both half-hours must exist", "Missing remains null; zero is valid"],"amber"),
        Node("metrics",1045,855,330,120,"Compute matched errors",["Error = forecast minus actual", "MAE, RMSE, bias, shortfall energy", "Report matched / expected coverage"],"amber"),
        Node("review",555,1040,330,120,"5. Review the outcomes",["Reveal actuals or open performance", "Charts, hourly patterns, worst intervals", "Clearly labelled retrospective"],"amber"),
        Node("export",555,1230,330,100,"6. Export for review",["CSV keeps selected dates and cutoff", "Forecast, actual, error, timestamps"],"green"),
    ]
    edges = [
        ([(720,275),(720,325)],"",0,0,False),
        ([(720,425),(720,475)],"",0,0,False),
        ([(720,595),(720,665)],"Forecast data",790,635,False),
        ([(555,375),(230,375),(230,475)],"Time-safe history",330,358,False),
        ([(230,595),(230,665)],"",0,0,False),
        ([(230,785),(230,855)],"",0,0,False),
        ([(395,915),(465,915),(465,725),(555,725)],"Context",465,822,False),
        ([(885,535),(1045,535)],"Compare later",965,517,False),
        ([(1210,595),(1210,665)],"",0,0,False),
        ([(1210,785),(1210,855)],"",0,0,False),
        ([(1210,975),(1210,1100),(885,1100)],"Measured results",1045,1082,False),
        ([(720,785),(720,1040)],"Optional review",790,920,True),
        ([(720,1160),(720,1230)],"",0,0,False),
    ]
    render("windward-workflow", "From buying decision to measured outcome", "Green: information and history available by the decision cutoff. Amber: explicitly retrospective evaluation.", 1410, nodes, edges,
           footnote="Source: implemented analysis rules. January 1–31 decisions deliver January 2–February 1. National wind exposure is not a client purchase order.")


if __name__ == "__main__":
    architecture()
    workflow()
