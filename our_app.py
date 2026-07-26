import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os
import copy
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import plotly.io as pio
import io
from datetime import datetime

st.set_page_config(page_title="Customer Analytics Platform", layout="wide")

try:
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSansCondensed.ttf'))
    RUSSIAN_FONT = 'DejaVu'
except:
    RUSSIAN_FONT = 'Helvetica'

def export_to_pdf(text_content, filename="report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    for line in text_content.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(filename)

def export_full_pdf(page_name, df, fig=None, fig2=None, segment_name=None, segment_df=None, threshold=None):
    filename = f"report_{page_name}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontName=RUSSIAN_FONT, fontSize=16, spaceAfter=30)
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontName=RUSSIAN_FONT, fontSize=10)
    heading_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName=RUSSIAN_FONT, fontSize=12, spaceAfter=10)
    
    story.append(Paragraph(f"отчет: {page_name}", title_style))
    story.append(Paragraph(f"дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    if page_name == "общая статистика":
        data = [
            ['показатель', 'значение'],
            ['всего клиентов', str(len(df))],
            ['средняя вероятность оттока', f"{df['ChurnProbability'].mean():.1%}"],
            ['клиентов с высоким риском (>0.7)', str(len(df[df['ChurnProbability'] > 0.7]))],
            ['количество сегментов', str(df['Segment'].nunique())]
        ]
        table = Table(data, colWidths=[80*mm, 80*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        segment_counts = df['Segment'].value_counts()
        segment_labels_dict = {0: 'vip', 1: 'экономные', 2: 'спящие', 3: 'средние'}
        seg_data = [['сегмент', 'количество']]
        for seg, count in segment_counts.items():
            seg_data.append([segment_labels_dict[seg], str(count)])
        seg_table = Table(seg_data, colWidths=[80*mm, 80*mm])
        seg_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(Paragraph("распределение по сегментам", heading_style))
        story.append(Spacer(1, 10))
        story.append(seg_table)
    
    elif page_name == "сегменты" and segment_df is not None and segment_name is not None:
        data = [
            ['показатель', 'значение'],
            ['выбранный сегмент', segment_name],
            ['клиентов в сегменте', str(len(segment_df))],
            ['средняя вероятность оттока', f"{segment_df['ChurnProbability'].mean():.1%}"],
            ['средний monetary', f"{segment_df['Monetary'].mean():.2f}"]
        ]
        table = Table(data, colWidths=[80*mm, 80*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        top10 = segment_df[['CustomerID', 'Recency', 'Monetary', 'ChurnProbability']].head(10)
        top_data = [['customerid', 'recency', 'monetary', 'риск']]
        for _, row in top10.iterrows():
            top_data.append([str(row['CustomerID']), f"{row['Recency']:.2f}", f"{row['Monetary']:.2f}", f"{row['ChurnProbability']:.1%}"])
        top_table = Table(top_data, colWidths=[40*mm, 30*mm, 40*mm, 30*mm])
        top_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(Paragraph("топ-10 клиентов", heading_style))
        story.append(Spacer(1, 10))
        story.append(top_table)
    
    elif page_name == "прогноз оттока" and threshold is not None:
        high_risk = df[df['ChurnProbability'] > threshold]
        data = [
            ['показатель', 'значение'],
            ['порог риска', f"{threshold:.0%}"],
            ['клиентов с риском выше порога', str(len(high_risk))],
            ['средняя вероятность (все)', f"{df['ChurnProbability'].mean():.1%}"],
            ['максимальный риск', f"{df['ChurnProbability'].max():.1%}"]
        ]
        table = Table(data, colWidths=[80*mm, 80*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        if len(high_risk) > 0:
            top10_risk = high_risk[['CustomerID', 'Segment', 'ChurnProbability']].head(10)
            seg_names = {0: 'vip', 1: 'экономные', 2: 'спящие', 3: 'средние'}
            risk_data = [['customerid', 'сегмент', 'риск']]
            for _, row in top10_risk.iterrows():
                risk_data.append([str(row['CustomerID']), seg_names[row['Segment']], f"{row['ChurnProbability']:.1%}"])
            risk_table = Table(risk_data, colWidths=[50*mm, 60*mm, 40*mm])
            risk_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(Paragraph("топ-10 клиентов с высоким риском", heading_style))
            story.append(Spacer(1, 10))
            story.append(risk_table)
    
    def add_fig_to_pdf(figure, title):
        if figure is not None:
            story.append(Spacer(1, 20))
            story.append(Paragraph(title, heading_style))
            story.append(Spacer(1, 10))
            fig_copy = copy.deepcopy(figure)
            fig_copy.update_layout(template='plotly_white', autosize=True)
            fig_copy.update_traces(marker=dict(line=dict(width=1, color='black')))
            img_bytes = pio.to_image(fig_copy, format='png', width=800, height=500, scale=2)
            img_io = io.BytesIO(img_bytes)
            img = Image(img_io, width=180*mm, height=100*mm)
            story.append(img)
    
    add_fig_to_pdf(fig, "визуализация 1")
    add_fig_to_pdf(fig2, "визуализация 2")
    
    doc.build(story)
    return filename

st.title("Платформа аналитики пользовательских данных")

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/customer_profiles.csv', sep=';')
    return df

df = load_data()

st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу", ["Общая статистика", "Сегменты", "Прогноз оттока"])

segment_labels = {0: 'VIP клиенты', 1: 'Экономные клиенты', 2: 'Спящие клиенты', 3: 'Средние клиенты'}

if page == "Общая статистика":
    st.header("Общая статистика")
    
    if st.button("экспорт в pdf (текст)"):
        content = f"""
общая статистика
всего клиентов: {len(df)}
средняя вероятность оттока: {df['ChurnProbability'].mean():.1%}
клиентов с высоким риском (>0.7): {len(df[df['ChurnProbability'] > 0.7])}
количество сегментов: {df['Segment'].nunique()}

распределение по сегментам:
vip клиенты: {len(df[df['Segment']==0])}
экономные клиенты: {len(df[df['Segment']==1])}
спящие клиенты: {len(df[df['Segment']==2])}
средние клиенты: {len(df[df['Segment']==3])}
"""
        export_to_pdf(content)
        st.success("pdf сохранен как report.pdf")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего клиентов", len(df))
    col2.metric("Средняя вероятность оттока", f"{df['ChurnProbability'].mean():.1%}")
    col3.metric("Клиентов с высоким риском (>0.7)", len(df[df['ChurnProbability'] > 0.7]))
    col4.metric("Количество сегментов", df['Segment'].nunique())
    
    st.subheader("Распределение клиентов по сегментам")
    
    segment_counts = df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'count']
    segment_counts['SegmentName'] = segment_counts['Segment'].map(segment_labels)
    
    fig1 = px.pie(segment_counts, values='count', names='SegmentName', title='Сегменты клиентов')
    st.plotly_chart(fig1, use_container_width=True)
    
    if st.button("Подготовить полный pdf с графиком (стр. 1)"):
        filename = export_full_pdf("общая статистика", df, fig=fig1)
        with open(filename, "rb") as f:
            st.download_button("скачать отчет", f, file_name=filename)
    
    st.subheader("Статистика по сегментам")
    st.info("пояснение: отрицательный recency = активный клиент (купил недавно). положительный recency = спящий клиент (давно не покупал)")
    st.info("с monetary наоборот: отрицательное значение - тратит мало. положительное - много")
    
    stats = df.groupby('Segment').agg({
        'CustomerID': 'count',
        'Recency': 'mean',
        'Monetary': 'mean',
        'ChurnProbability': 'mean'
    }).round(2)
    stats.columns = ['Клиентов', 'Recency (средн.)', 'Monetary (средн.)', 'Вероятность оттока']
    stats.index = stats.index.map(segment_labels)
    st.dataframe(stats)

elif page == "Сегменты":
    st.header("Анализ по сегментам")
    
    selected_segment = st.selectbox(
        "Выберите сегмент",
        options=list(segment_labels.keys()),
        format_func=lambda x: segment_labels[x]
    )
    
    segment_df = df[df['Segment'] == selected_segment]
    
    if st.button("экспорт в pdf (текст)"):
        content = f"""
анализ сегментов
выбран сегмент: {segment_labels[selected_segment]}
клиентов в сегменте: {len(segment_df)}
средняя вероятность оттока: {segment_df['ChurnProbability'].mean():.1%}
средний monetary: {segment_df['Monetary'].mean():.2f}

примеры клиентов (первые 10):
{segment_df[['CustomerID', 'Recency', 'Monetary', 'ChurnProbability']].head(10).to_string()}
"""
        export_to_pdf(content)
        st.success("pdf сохранен как report.pdf")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Клиентов", len(segment_df))
    col2.metric("Средняя вероятность оттока", f"{segment_df['ChurnProbability'].mean():.1%}")
    col3.metric("Средний Monetary", f"{segment_df['Monetary'].mean():.2f}")
    
    st.subheader("Таблица клиентов")
    st.dataframe(segment_df[['CustomerID', 'Recency', 'Monetary', 'ChurnProbability']].head(20))
    
    st.subheader("Распределение вероятности оттока")
    fig2 = px.histogram(segment_df, x='ChurnProbability', nbins=20)
    st.plotly_chart(fig2, use_container_width=True)
    
    if st.button("Подготовить полный pdf с графиком (стр. 2)"):
        filename = export_full_pdf("сегменты", df, fig=fig2, segment_name=segment_labels[selected_segment], segment_df=segment_df)
        with open(filename, "rb") as f:
            st.download_button("скачать отчет", f, file_name=filename)

else:
    st.header("Прогноз оттока")
    
    threshold = st.slider("Порог вероятности оттока", 0.0, 1.0, 0.5, 0.05)
    high_risk = df[df['ChurnProbability'] > threshold].sort_values('ChurnProbability', ascending=False)
    
    if st.button("экспорт в pdf (текст)"):
        content = f"""
прогноз оттока
порог риска: {threshold}
клиентов с риском выше порога: {len(high_risk)}

топ-10 клиентов с наибольшим риском:
{high_risk[['CustomerID', 'Segment', 'ChurnProbability']].head(10).to_string()}

общая статистика по рискам:
средняя вероятность: {df['ChurnProbability'].mean():.3f}
минимальная: {df['ChurnProbability'].min():.3f}
максимальная: {df['ChurnProbability'].max():.3f}
"""
        export_to_pdf(content)
        st.success("pdf сохранен как report.pdf")
    
    st.metric("Клиентов с риском выше порога", len(high_risk))
    
    if len(high_risk) > 0:
        st.subheader("Топ-10 клиентов с наибольшим риском")
        st.dataframe(high_risk[['CustomerID', 'Segment', 'ChurnProbability']].head(10))
        
        fig3 = px.bar(high_risk.head(10), x='CustomerID', y='ChurnProbability', color='Segment')
        st.plotly_chart(fig3, use_container_width=True)
        
        st.subheader("Общее распределение вероятностей оттока")
        fig4 = px.histogram(df, x='ChurnProbability', nbins=30)
        st.plotly_chart(fig4, use_container_width=True)
        
        if st.button("Подготовить полный pdf с графиком (стр. 3)"):
            filename = export_full_pdf("прогноз оттока", df, fig=fig3, fig2=fig4, threshold=threshold)
            with open(filename, "rb") as f:
                st.download_button("скачать отчет", f, file_name=filename)
    else:
        st.info("Нет клиентов с вероятностью оттока выше выбранного порога")
        
        fig3 = px.histogram(df, x='ChurnProbability', nbins=30)
        st.plotly_chart(fig3, use_container_width=True)
        
        if st.button("Подготовить полный pdf с графиком (стр. 3)"):
            filename = export_full_pdf("прогноз оттока", df, fig=fig3, threshold=threshold)
            with open(filename, "rb") as f:
                st.download_button("скачать отчет", f, file_name=filename)
