"""Regenerate the SVG and editable diagrams.net file with Python's standard library."""
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from html import escape
ROOT = Path(__file__).resolve().parent
W,H = 1800,1840
C = {'analyst':('#132e38','#63e0d9'), 'system':('#242444','#aea0ff'), 'decision':('#282c47','#9faed0'), 'error':('#452d21','#efb86e'), 'decline':('#42253c','#f194c2'), 'review':('#40351f','#f4d28a'), 'eligible':('#173d38','#8ce8cc')}
nodes = []
edges = []
def node(id,x,y,w,h,title,lines,kind='system',diamond=False):
    nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,lines=lines,kind=kind,diamond=diamond))
def edge(source,target,points,label='',color='#929ebd',label_at=None):
    edges.append(dict(source=source,target=target,points=points,label=label,color=color,label_at=label_at))
node('intake',270,290,320,104,'01  Enter fictional loan',['Borrower + property context','Loan, value, NOI, debt service'],'analyst')
node('valid',800,290,214,122,'Inputs valid?',[],'decision',True)
node('errors',270,478,320,104,'Correct input errors',['Field-specific feedback','Nothing recorded on failure'],'error')
node('ratios',800,480,420,104,'02  Calculate financial ratios',['DSCR · LTV · debt yield','Compare before display rounding'])
node('evaluate',800,650,420,104,'03  Evaluate all three rules',['Pass / review / decline per rule','Decline > review > eligible'])
node('save',800,820,420,112,'04  Record evaluation evidence',['Inputs, ratios, reasons + outcome','Policy snapshot, UUID + UTC time'])
node('declineGate',800,1010,214,122,'Any decline?',[],'decision',True)
node('reviewGate',800,1190,214,122,'Any review?',[],'decision',True)
node('allPass',800,1380,320,100,'All three rules pass',['No decline or review triggers'],'eligible')
node('declineResult',1440,1010,380,112,'SCREENING DECLINE',['Explain every triggered rule','Outside fictional screening limits'],'decline')
node('reviewResult',1440,1190,380,112,'ANALYST REVIEW',['Explain the rule exceptions','Closer analyst review is needed'],'review')
node('eligibleResult',1440,1380,380,112,'ELIGIBLE FOR UNDERWRITING',['Explain the three passing rules','Proceed to fictional underwriting'],'eligible')
node('inspect',270,1570,340,112,'05  Review / inspect / export',['Read the saved rule explanations','Revisit history or download JSON'],'analyst')
edge('intake','valid',[(430,290),(693,290)],'Submit',label_at=(555,271))
edge('valid','errors',[(693,290),(550,290),(550,478),(430,478)],'No',C['error'][1],(571,392))
edge('errors','intake',[(110,478),(80,478),(80,290),(110,290)],'Correct',C['analyst'][1],(122,398))
edge('valid','ratios',[(800,351),(800,428)],'Yes',C['analyst'][1],(825,392))
edge('ratios','evaluate',[(800,532),(800,598)])
edge('evaluate','save',[(800,702),(800,764)])
edge('save','declineGate',[(800,876),(800,949)],'Read saved outcome',label_at=(920,920))
edge('declineGate','declineResult',[(907,1010),(1250,1010)],'Yes',C['decline'][1],(1070,990))
edge('declineGate','reviewGate',[(800,1071),(800,1129)],'No',label_at=(825,1112))
edge('reviewGate','reviewResult',[(907,1190),(1250,1190)],'Yes',C['review'][1],(1070,1170))
edge('reviewGate','allPass',[(800,1251),(800,1330)],'No',label_at=(825,1300))
edge('allPass','eligibleResult',[(960,1380),(1250,1380)],'Pass',C['eligible'][1],(1090,1360))
for n in ['declineResult','reviewResult','eligibleResult']:
    y=next(x['y'] for x in nodes if x['id']==n)
    edge(n,'inspect',[(1630,y),(1690,y),(1690,1690),(270,1690),(270,1626)],color='#73839f')

svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1840" viewBox="0 0 1800 1840" role="img" aria-labelledby="title desc">', '<title id="title">CreditFlow analyst and system swimlane process</title><desc id="desc">Fictional loan intake, input correction, calculation of all financial ratios and rules, saved evidence, decline-first routing, and analyst review of explanations and JSON export. Local evidence uses SQLite; hosted demo uses session history.</desc>', '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#091423"/><stop offset=".55" stop-color="#16172e"/><stop offset="1" stop-color="#25203f"/></linearGradient><linearGradient id="heading"><stop stop-color="#68e6db"/><stop offset="1" stop-color="#bdabff"/></linearGradient><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>', '<rect width="1800" height="1840" rx="24" fill="url(#bg)"/>', '<g font-family="DejaVu Sans,Arial,sans-serif">']
def text(x,y,content,size=18,color='#eef3ff',weight=400,anchor='middle'):
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(content)}</text>')
text(80,68,'CREDITFLOW  /  PROCESS & DECISION DESIGN',18,'#afa8d7',600,'start')
text(80,126,'A clear path from intake to explanation.',42,'url(#heading)',650,'start')
text(80,168,'Fictional policy demo-cre-1.0 · All rules evaluated · Saved outcomes explained',20,'#b7c5df',400,'start')
lanes=[('ANALYST',80,400,'#132831','#63e0d9'),('SYSTEM',510,590,'#1d203a','#afa0ff'),('OUTCOME / NEXT STEP',1130,600,'#222039','#ccb6ee')]
for label,x,w,fill,stroke in lanes:
    svg.append(f'<rect x="{x}" y="208" width="{w}" height="1455" rx="18" fill="{fill}" fill-opacity=".6" stroke="#3a405b"/>')
    text(x+24,230,label,16,stroke,700,'start')
for e in edges:
    coords=' '.join(f'{x},{y}' for x,y in e['points'])
    svg.append(f'<polyline points="{coords}" fill="none" stroke="{e["color"]}" stroke-width="2.5" stroke-linejoin="round" marker-end="url(#arrow)"/>')
    if e['label']:
        x,y=e['label_at']; text(x,y,e['label'],16,e['color'],600)
for n in nodes:
    x,y,w,h=n['x'],n['y'],n['w'],n['h'];fill,stroke=C[n['kind']]
    if n['diamond']:
        svg.append(f'<polygon points="{x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        text(x,y+6,n['title'],18,stroke,650)
    else:
        svg.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="15" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>')
        text(x,y-h/2+32,n['title'],18,stroke,650)
        for i,line in enumerate(n['lines']): text(x,y-h/2+58+i*23,line,16,'#d0daed')
# Policy references are notes, not additional workflow steps.
svg.append('<rect x="1200" y="278" width="460" height="428" rx="18" fill="#11192d" stroke="#454262"/>')
text(1230,319,'FICTIONAL POLICY AT A GLANCE',16,'#c5b6f5',700,'start')
for i,(name,review,decline) in enumerate([('DSCR','Review < 1.25×','Decline < 1.00×'),('LTV','Review > 75%','Decline > 85%'),('Debt yield','Review < 8%','Decline < 6%')]):
    y=365+i*94;text(1230,y,name,19,'#e8edff',650,'start');text(1230,y+27,review,17,'#f4d28a',400,'start');text(1430,y+27,decline,17,'#f194c2',400,'start')
text(1230,668,'Exact thresholds use strict inequalities.',16,'#b7c5df',400,'start')
text(1230,691,'Property type is contextual only.',16,'#b7c5df',400,'start')
text(800,1510,'EVIDENCE STORAGE',16,'#afa0ff',700)
text(800,1544,'Local app: SQLite history',17,'#c0cce1')
text(800,1572,'Public demo: session history only',17,'#c0cce1')
text(800,1600,'Re-evaluation creates a new record.',16,'#97a7c2')
text(80,1750,'READING THE DIAGRAM',15,'#afa8d7',700,'start')
text(80,1782,'Teal = analyst action  ·  Violet = system action  ·  Diamonds = validation / routing  ·  Outcome color is paired with a text label.',17,'#c2cce1',400,'start')
text(80,1812,'Screening only, not loan approval. Next steps are explanatory; no task assignment or downstream underwriting integration.',17,'#98a9c6',400,'start')
svg.append('</g></svg>')
(ROOT/'creditflow-process.svg').write_text('\n'.join(svg)+'\n')

# Uncompressed diagrams.net XML: named nodes, editable labels, and editable connectors.
mx=Element('mxfile',host='app.diagrams.net');diagram=SubElement(mx,'diagram',name='CreditFlow process');model=SubElement(diagram,'mxGraphModel',dx='1800',dy='1840',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),background='#0d1425');r=SubElement(model,'root');SubElement(r,'mxCell',id='0');SubElement(r,'mxCell',id='1',parent='0')
def mxnode(id,x,y,w,h,value,style):
    cell=SubElement(r,'mxCell',id=id,value=value,style=style,vertex='1',parent='1');SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
mxnode('title',80,60,1560,100,'CREDITFLOW | Process & decision design\nFictional screening from intake to explanation','text;html=0;align=left;fontColor=#b6b0f5;fontSize=28;')
for label,x,w,fill,stroke in lanes:
    mxnode('lane'+str(x),x,208,w,1455,label,'swimlane;html=0;startSize=42;horizontal=1;rounded=1;fillColor='+fill+';swimlaneFillColor='+fill+';strokeColor=#3a405b;fontColor='+stroke+';fontSize=16;')
for n in nodes:
    fill,stroke=C[n['kind']];shape='rhombus;' if n['diamond'] else 'rounded=1;arcSize=16;'
    mxnode(n['id'],n['x']-n['w']/2,n['y']-n['h']/2,n['w'],n['h'],'\n'.join([n['title'],*n['lines']]),shape+'whiteSpace=wrap;html=0;fillColor='+fill+';strokeColor='+stroke+';fontColor=#eaf1ff;fontSize=17;')
for i,e in enumerate(edges):
    cell=SubElement(r,'mxCell',id='edge'+str(i),value=e['label'],style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;strokeWidth=2;strokeColor='+e['color']+';fontColor='+e['color']+';fontSize=16;',edge='1',parent='1',source=e['source'],target=e['target']);geom=SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=SubElement(geom,'Array',attrib={'as':'points'})
    for x,y in e['points'][1:-1]:SubElement(arr,'mxPoint',x=str(x),y=str(y))
mxnode('policy',1200,280,460,425,'FICTIONAL POLICY demo-cre-1.0\n\nDSCR: review < 1.25; decline < 1.00\nLTV: review > 75%; decline > 85%\nDebt yield: review < 8%; decline < 6%\n\nExact thresholds use strict inequalities.\nProperty type is contextual only.','rounded=1;whiteSpace=wrap;html=0;fillColor=#11192d;strokeColor=#454262;fontColor=#d2d8ed;fontSize=17;')
mxnode('storage',550,1485,500,135,'EVIDENCE STORAGE\nLocal app: SQLite history\nPublic demo: session history only\nRe-evaluation creates a new record.','text;whiteSpace=wrap;html=0;fontColor=#afa0ff;fontSize=17;')
mxnode('note',80,1730,1620,90,'Screening only, not loan approval. Next steps are explanatory; no task assignment or downstream underwriting integration.','text;whiteSpace=wrap;html=0;align=left;fontColor=#b8c6dd;fontSize=17;')
ElementTree(mx).write(ROOT/'creditflow-process.drawio',encoding='utf-8',xml_declaration=True)
print('Generated SVG and editable drawio diagram')
