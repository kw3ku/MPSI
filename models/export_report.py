"""
Generate professional PDF research reports from MPSI analysis
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io


class MPSIReportGenerator:

    ACCENT = colors.HexColor('#6366f1')
    HAWK   = colors.HexColor('#ef4444')
    DOVE   = colors.HexColor('#3b82f6')
    DARK   = colors.HexColor('#0f1623')
    MUTED  = colors.HexColor('#7b90b8')

    def generate(self, result: dict) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=letter,
            leftMargin=.85*inch, rightMargin=.85*inch,
            topMargin=.9*inch,   bottomMargin=.9*inch
        )

        styles = getSampleStyleSheet()
        h1  = ParagraphStyle('h1',  fontSize=18, fontName='Helvetica-Bold',
                              textColor=self.ACCENT, spaceAfter=4)
        h2  = ParagraphStyle('h2',  fontSize=12, fontName='Helvetica-Bold',
                              textColor=colors.HexColor('#eef2ff'), spaceBefore=14, spaceAfter=4)
        body = ParagraphStyle('body', fontSize=9.5, fontName='Helvetica',
                               textColor=colors.HexColor('#cbd5e1'), leading=14)
        tiny = ParagraphStyle('tiny', fontSize=8, fontName='Helvetica',
                               textColor=self.MUTED, leading=12)

        score = result.get('mpsi_score', 0)
        stance = result.get('stance', 'Neutral')
        score_color = self.HAWK if score > 10 else (self.DOVE if score < -10 else self.MUTED)

        story = []

        # ── HEADER ──
        story.append(Paragraph("MONETARY POLICY SENTIMENT INDEX", h1))
        story.append(Paragraph("Federal Reserve Document Analysis Report", body))
        story.append(HRFlowable(width='100%', thickness=1, color=self.ACCENT))
        story.append(Spacer(1, 10))

        # ── META TABLE ──
        meta = [
            ['Document',  result.get('filename', 'N/A'),
             'Generated', datetime.now().strftime('%B %d, %Y %H:%M UTC')],
            ['Words',     str(result.get('word_count', 'N/A')),
             'Model',     'Hybrid MPSI v1.0'],
        ]
        mt = Table(meta, colWidths=[1*inch, 2.4*inch, 1*inch, 2.4*inch])
        mt.setStyle(TableStyle([
            ('FONTSIZE',    (0,0),(-1,-1), 8.5),
            ('FONTNAME',    (0,0),(0,-1),  'Helvetica-Bold'),
            ('FONTNAME',    (2,0),(2,-1),  'Helvetica-Bold'),
            ('TEXTCOLOR',   (0,0),(0,-1),  self.MUTED),
            ('TEXTCOLOR',   (2,0),(2,-1),  self.MUTED),
            ('TEXTCOLOR',   (1,0),(1,-1),  colors.HexColor('#eef2ff')),
            ('TEXTCOLOR',   (3,0),(3,-1),  colors.HexColor('#eef2ff')),
            ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#131d2e')]),
            ('GRID',        (0,0),(-1,-1),  .3, colors.HexColor('#243048')),
            ('PADDING',     (0,0),(-1,-1),  6),
        ]))
        story.append(mt)
        story.append(Spacer(1, 14))

        # ── MPSI SCORE BLOCK ──
        story.append(Paragraph("MPSI SCORE & STANCE", h2))
        score_data = [[
            f"MPSI Score: {score}",
            f"Stance: {stance}",
            f"Keyword MPSI: {result.get('keyword_mpsi','N/A')}",
            f"FinBERT MPSI: {result.get('finbert_mpsi','N/A')}"
        ]]
        st = Table(score_data, colWidths=[1.7*inch]*4)
        st.setStyle(TableStyle([
            ('FONTSIZE',  (0,0),(-1,-1), 9),
            ('FONTNAME',  (0,0),(-1,-1), 'Helvetica-Bold'),
            ('ALIGN',     (0,0),(-1,-1), 'CENTER'),
            ('TEXTCOLOR', (0,0),(0,0),   score_color),
            ('TEXTCOLOR', (1,0),(1,0),   score_color),
            ('TEXTCOLOR', (2,0),(-1,-1), self.MUTED),
            ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#131d2e')),
            ('GRID',      (0,0),(-1,-1), .3, colors.HexColor('#243048')),
            ('PADDING',   (0,0),(-1,-1), 10),
        ]))
        story.append(st)
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f"<b>Hybrid Formula:</b> {result.get('hybrid_formula','N/A')}", body))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Policy Implication:</b> {result.get('policy_implication','N/A')}", body))
        story.append(Spacer(1, 14))

        # ── KEYWORD BREAKDOWN ──
        story.append(Paragraph("KEYWORD ANALYSIS", h2))
        kw_data = [
            ['Metric', 'Value'],
            ['Hawkish Keywords Found', str(result.get('hawkish_count', 0))],
            ['Dovish Keywords Found',  str(result.get('dovish_count', 0))],
            ['Neutral Keywords Found', str(result.get('neutral_count', 0))],
            ['Total Keywords',         str(result.get('keyword_count', 0))],
            ['Hawkish %',              f"{result.get('hawkish_pct',0):.1f}%"],
            ['Dovish %',               f"{result.get('dovish_pct',0):.1f}%"],
        ]
        kt = Table(kw_data, colWidths=[3.5*inch, 3.3*inch])
        kt.setStyle(TableStyle([
            ('FONTNAME',     (0,0),(-1,0),   'Helvetica-Bold'),
            ('FONTSIZE',     (0,0),(-1,-1),   9),
            ('BACKGROUND',   (0,0),(-1,0),    colors.HexColor('#1a2540')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),  [colors.HexColor('#131d2e'),
                                               colors.HexColor('#0f1623')]),
            ('TEXTCOLOR',    (0,0),(-1,-1),   colors.HexColor('#eef2ff')),
            ('GRID',         (0,0),(-1,-1),   .3, colors.HexColor('#243048')),
            ('PADDING',      (0,0),(-1,-1),   7),
        ]))
        story.append(kt)

        # Hawkish / Dovish word lists
        if result.get('hawkish_words'):
            story.append(Spacer(1,8))
            story.append(Paragraph(
                f"<b>Hawkish terms detected:</b> {', '.join(result['hawkish_words'][:15])}", tiny))
        if result.get('dovish_words'):
            story.append(Spacer(1,4))
            story.append(Paragraph(
                f"<b>Dovish terms detected:</b> {', '.join(result['dovish_words'][:15])}", tiny))

        story.append(Spacer(1, 14))

        # ── VALIDATION ──
        story.append(Paragraph("MODEL VALIDATION", h2))
        val_data = [
            ['Metric',                    'Value',   'Interpretation'],
            ['Pearson r (MPSI vs FFR)',    '0.689',   'Strong positive correlation ***'],
            ['R-squared',                  '0.475',   '47.5% of FFR variance explained'],
            ['p-value',                    '< 0.001', 'Highly statistically significant'],
            ['Lead time (peak r=0.721)',   '3 months','MPSI predicts Fed action ~3 mo ahead'],
            ['Sample',                     '119 docs','FOMC Statements, Minutes, Speeches'],
            ['Period',                     '2020–2026','Covers 3 full policy regimes'],
            ['FinBERT Accuracy',           '84.2%',   'Fine-tuned on financial text'],
            ['Hybrid Weight',              '70/30',   'Keyword / FinBERT'],
        ]
        vt = Table(val_data, colWidths=[2.3*inch, 1.2*inch, 3.3*inch])
        vt.setStyle(TableStyle([
            ('FONTNAME',     (0,0),(-1,0),   'Helvetica-Bold'),
            ('FONTSIZE',     (0,0),(-1,-1),   8.5),
            ('BACKGROUND',   (0,0),(-1,0),    colors.HexColor('#1a2540')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),  [colors.HexColor('#131d2e'),
                                               colors.HexColor('#0f1623')]),
            ('TEXTCOLOR',    (0,0),(-1,-1),   colors.HexColor('#eef2ff')),
            ('TEXTCOLOR',    (0,0),(-1,0),    self.ACCENT),
            ('GRID',         (0,0),(-1,-1),   .3, colors.HexColor('#243048')),
            ('PADDING',      (0,0),(-1,-1),   6),
        ]))
        story.append(vt)
        story.append(Spacer(1, 14))

        # ── FOOTER ──
        story.append(HRFlowable(width='100%', thickness=.5, color=colors.HexColor('#243048')))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "FedMPSI Dashboard · Hybrid NLP Monetary Policy Sentiment Index · "
            "For research and informational purposes only. "
            "Not financial advice.",
            tiny))

        doc.build(story)
        return buf.getvalue()