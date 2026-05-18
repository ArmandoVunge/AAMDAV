import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
from database import DatabaseManager

class RelatorioManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def gerar_excel(self, arquivo_saida='relatorio_atletas.xlsx'):
        """Gera relatório em formato Excel"""
        try:
            atletas = self.db.obter_todos_atletas()
            
            if not atletas:
                return False, "Nenhum atleta cadastrado para gerar relatório"
            
            # Criar DataFrame
            df = pd.DataFrame(atletas, columns=['ID', 'Nome', 'Idade', 'Modalidade', 'Gênero', 'Data Cadastro'])
            
            # Converter data para formato legível
            df['Data Cadastro'] = pd.to_datetime(df['Data Cadastro']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Criar arquivo Excel com múltiplas abas
            with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                # Aba 1: Dados dos atletas
                df.to_excel(writer, sheet_name='Atletas', index=False)
                
                # Aba 2: Estatísticas
                stats = self.db.obter_estatisticas()
                
                if stats:
                    # Estatísticas gerais
                    stats_data = {
                        'Métrica': ['Total de Atletas', 'Idade Média'],
                        'Valor': [stats['total'], f"{stats['idade_media']} anos"]
                    }
                    df_stats = pd.DataFrame(stats_data)
                    df_stats.to_excel(writer, sheet_name='Estatísticas', index=False, startrow=0)
                    
                    # Por modalidade
                    df_modalidade = pd.DataFrame(stats['por_modalidade'], columns=['Modalidade', 'Total'])
                    df_modalidade.to_excel(writer, sheet_name='Estatísticas', index=False, startrow=5)
                    
                    # Por gênero
                    df_genero = pd.DataFrame(stats['por_genero'], columns=['Gênero', 'Total'])
                    df_genero.to_excel(writer, sheet_name='Estatísticas', index=False, startrow=len(df_modalidade) + 10)
                
                # Formatação
                workbook = writer.book
                worksheet = writer.sheets['Atletas']
                
                # Ajustar largura das colunas
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(64 + idx)].width = min(max_length, 50)
            
            return True, f"Relatório Excel gerado com sucesso: {arquivo_saida}"
        
        except Exception as e:
            return False, f"Erro ao gerar relatório Excel: {str(e)}"
    
    def gerar_pdf(self, arquivo_saida='relatorio_atletas.pdf'):
        """Gera relatório em formato PDF"""
        try:
            atletas = self.db.obter_todos_atletas()
            
            if not atletas:
                return False, "Nenhum atleta cadastrado para gerar relatório"
            
            # Criar documento PDF
            doc = SimpleDocTemplate(arquivo_saida, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1
            )
            title = Paragraph("RELATÓRIO DE ATLETAS - AAMDAV", title_style)
            story.append(title)
            
            # Data do relatório
            data_relatorio = datetime.now().strftime('%d de %B de %Y às %H:%M:%S')
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                spaceAfter=20,
                alignment=2
            )
            data_para = Paragraph(f"Gerado em: {data_relatorio}", date_style)
            story.append(data_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Tabela de atletas
            header = ['ID', 'Nome', 'Idade', 'Modalidade', 'Gênero', 'Data Cadastro']
            data_table = [header]
            
            for atleta in atletas:
                data_table.append([
                    str(atleta[0]),
                    atleta[1],
                    str(atleta[2]),
                    atleta[3],
                    atleta[4],
                    atleta[5][:10] if atleta[5] else ''
                ])
            
            # Criar tabela
            table = Table(data_table, colWidths=[0.5*inch, 1.5*inch, 0.7*inch, 1.2*inch, 0.8*inch, 1.2*inch])
            
            # Estilo da tabela
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Estatísticas
            stats = self.db.obter_estatisticas()
            
            if stats:
                story.append(PageBreak())
                
                stats_title = Paragraph("ESTATÍSTICAS", title_style)
                story.append(stats_title)
                story.append(Spacer(1, 0.2*inch))
                
                # Resumo geral
                resumo_style = ParagraphStyle(
                    'ResumoStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceAfter=10
                )
                
                story.append(Paragraph(f"<b>Total de Atletas:</b> {stats['total']}", resumo_style))
                story.append(Paragraph(f"<b>Idade Média:</b> {stats['idade_media']} anos", resumo_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Por modalidade
                if stats['por_modalidade']:
                    story.append(Paragraph("<b>Atletas por Modalidade:</b>", resumo_style))
                    
                    modalidade_data = [['Modalidade', 'Total']]
                    for mod, total in stats['por_modalidade']:
                        modalidade_data.append([mod, str(total)])
                    
                    modalidade_table = Table(modalidade_data, colWidths=[3*inch, 1.5*inch])
                    modalidade_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ]))
                    story.append(modalidade_table)
                    story.append(Spacer(1, 0.2*inch))
                
                # Por gênero
                if stats['por_genero']:
                    story.append(Paragraph("<b>Atletas por Gênero:</b>", resumo_style))
                    
                    genero_data = [['Gênero', 'Total']]
                    for gen, total in stats['por_genero']:
                        genero_data.append([gen, str(total)])
                    
                    genero_table = Table(genero_data, colWidths=[3*inch, 1.5*inch])
                    genero_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ]))
                    story.append(genero_table)
            
            # Gerar PDF
            doc.build(story)
            return True, f"Relatório PDF gerado com sucesso: {arquivo_saida}"
        
        except Exception as e:
            return False, f"Erro ao gerar relatório PDF: {str(e)}"
