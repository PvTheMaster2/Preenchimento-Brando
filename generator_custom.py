#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Customizado de Logbook - Usa dados personalizados
Combina dados inseridos pelo usuário com pools automáticos

Uso: python generator_custom.py
"""

from docxtpl import DocxTemplate
import json
from datetime import datetime, timedelta
import random
import os
import sys

class CustomLogbookGenerator:
    def __init__(self):
        """Inicializa o gerador customizado"""
        print("🍳 GERADOR CUSTOMIZADO DE LOGBOOK")
        print("=" * 50)
        self.config = self.load_json('config.json')
        self.content_pools = self.load_json('content_pools.json')
        self.custom_data = self.load_custom_data()
        
    def load_json(self, filename):
        """Carrega arquivo JSON com tratamento de erro"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo {filename} não encontrado!")
            print(f"   Certifique-se de que o arquivo existe no diretório atual.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Erro: Arquivo {filename} com formato JSON inválido!")
            print(f"   Erro específico: {e}")
            sys.exit(1)
    
    def load_custom_data(self):
        """Carrega dados personalizados se existirem"""
        filename = 'shifts_data_custom.json'
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Dados personalizados carregados: {len(data)} shifts")
                return {item['shift_number']: item for item in data}
            except Exception as e:
                print(f"⚠️ Erro ao carregar dados personalizados: {e}")
                return {}
        else:
            print("⚠️ Arquivo de dados personalizados não encontrado!")
            print("   Execute primeiro: python input_collector.py")
            choice = input("   Continuar com dados automáticos? (s/n): ")
            if choice.lower() != 's':
                sys.exit(1)
            return {}
    
    def generate_shifts(self):
        """Gera dados para todos os 48 shifts (customizados + automáticos)"""
        print("📊 Gerando dados para 48 shifts...")
        shifts = []
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        
        # Índices para controlar variedade do conteúdo automático
        used_content = {
            'special_requests': [],
            'food_details': [],
            'complaints': [],
            'debrief': []
        }
        
        custom_count = 0
        auto_count = 0
        
        for i in range(48):
            shift_number = i + 1
            shift_date = start_date + timedelta(days=i//2)
            shift_type = 'lunch' if i % 2 == 0 else 'dinner'
            
            # Dados básicos (sempre os mesmos)
            shift_data = {
                'shift_number': shift_number,
                'establishment': self.config['establishment'],
                'date': shift_date.strftime('%d/%m/%Y'),
                'shift_type': shift_type.title(),
                'start_time': self.config['shifts'][shift_type]['start_time'],
                'end_time': self.config['shifts'][shift_type]['end_time'], 
                'hours': self.config['shifts'][shift_type]['hours'],
                'menu_style': self.config['menu_style'],
                'workflow': self.content_pools[f'workflow_{shift_type}']
            }
            
            # Verificar se há dados customizados para este shift
            if shift_number in self.custom_data:
                # Usar dados customizados
                custom_shift = self.custom_data[shift_number]
                shift_data.update(self.merge_custom_data(custom_shift, shift_type))
                custom_count += 1
                print(f"📝 Shift {shift_number}: dados personalizados")
            else:
                # Usar dados automáticos dos pools
                shift_data.update(self.generate_automatic_data(shift_type, used_content))
                auto_count += 1
                print(f"🎲 Shift {shift_number}: dados automáticos")
            
            shifts.append(shift_data)
        
        print(f"✅ {len(shifts)} shifts gerados!")
        print(f"   📝 Personalizados: {custom_count}")
        print(f"   🎲 Automáticos: {auto_count}")
        return shifts
    
    def merge_custom_data(self, custom_shift, shift_type):
        """Combina dados customizados com dados padrão"""
        data = {}
        
        # Prepared for service - usar customizado se existir, senão padrão
        data['prepared_service'] = custom_shift.get(
            'prepared_service', 
            self.content_pools['prepared_service'][shift_type]
        )
        
        # Campos customizados - usar se existirem, senão usar dos pools
        for field in ['special_requests', 'food_details', 'complaints', 'debrief']:
            if field in custom_shift and custom_shift[field].strip():
                data[field] = custom_shift[field]
            else:
                # Usar pool automático se campo vazio
                data[field] = random.choice(self.content_pools[field])
        
        return data
    
    def generate_automatic_data(self, shift_type, used_content):
        """Gera dados automáticos dos pools com variedade"""
        data = {
            'prepared_service': self.content_pools['prepared_service'][shift_type],
            'special_requests': self.get_varied_content('special_requests', used_content),
            'food_details': self.get_varied_content('food_details', used_content),
            'complaints': self.get_varied_content('complaints', used_content),
            'debrief': self.get_varied_content('debrief', used_content)
        }
        return data
    
    def get_varied_content(self, content_type, used_content):
        """Seleciona conteúdo com variedade, evitando repetições excessivas"""
        available_content = self.content_pools[content_type]
        
        # Se todos foram usados, resetar para permitir reutilização
        if len(used_content[content_type]) >= len(available_content):
            used_content[content_type] = []
        
        # Preferir conteúdo não usado recentemente
        unused = [item for item in available_content if item not in used_content[content_type]]
        
        if unused:
            selected = random.choice(unused)
        else:
            selected = random.choice(available_content)
        
        # Registrar uso
        used_content[content_type].append(selected)
        
        # Manter apenas os últimos 3 itens para permitir reutilização após um intervalo
        if len(used_content[content_type]) > 3:
            used_content[content_type].pop(0)
        
        return selected
    
    def format_workflow_table(self, workflow_data):
        """Formata dados do workflow para o template"""
        formatted_rows = []
        for item in workflow_data:
            formatted_rows.append({
                'time': item['time'],
                'task': item['task'],
                'equipment': item['equipment'],
                'communication': item['communication']
            })
        return formatted_rows
    
    def generate_documents(self):
        """Gera todos os documentos Word"""
        print("🚀 Iniciando geração de documentos...")
        
        # Verificar se template existe
        template_file = 'logbook_template.docx'
        if not os.path.exists(template_file):
            print(f"❌ Erro: Arquivo '{template_file}' não encontrado!")
            print("   Crie o template Word primeiro seguindo as instruções do PLANO.md")
            return False
        
        try:
            template = DocxTemplate(template_file)
        except Exception as e:
            print(f"❌ Erro ao carregar template: {e}")
            return False
        
        # Gerar dados dos shifts
        shifts = self.generate_shifts()
        
        # Criar pasta output se não existir
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Pasta de saída: {os.path.abspath(output_dir)}")
        
        # Gerar documentos
        success_count = 0
        custom_count = 0
        
        for shift in shifts:
            try:
                # Adicionar workflow formatado
                shift['workflow_table'] = self.format_workflow_table(shift['workflow'])
                
                # Renderizar template com dados do shift
                template.render(shift)
                
                # Salvar arquivo
                filename = f"shift_{shift['shift_number']:02d}_{shift['shift_type'].lower()}.docx"
                filepath = os.path.join(output_dir, filename)
                template.save(filepath)
                
                # Identificar se é customizado
                is_custom = shift['shift_number'] in self.custom_data
                icon = "📝" if is_custom else "🎲"
                print(f"{icon} Gerado: {filename}")
                
                if is_custom:
                    custom_count += 1
                
                success_count += 1
                
                # Recarregar template para próximo uso (evita problemas de estado)
                template = DocxTemplate(template_file)
                
            except Exception as e:
                print(f"❌ Erro ao gerar shift {shift['shift_number']}: {e}")
                continue
        
        # Relatório final
        if success_count == 48:
            print(f"\n🎉 SUCESSO TOTAL! {success_count} documentos gerados na pasta '{output_dir}/'")
            print(f"📊 ESTATÍSTICAS:")
            print(f"   📝 Personalizados: {custom_count}")
            print(f"   🎲 Automáticos: {48 - custom_count}")
            print(f"   📁 Local: {os.path.abspath(output_dir)}")
            print("\n📝 Próximos passos:")
            print("   1. Conferir os documentos gerados")
            print("   2. Imprimir e levar para assinatura do head chef")
            print("   3. Completar seu curso com sucesso! 🎓")
        else:
            print(f"\n⚠️ Geração parcial: {success_count}/48 documentos criados")
            print("   Verifique os erros acima e execute novamente se necessário")
        
        return success_count == 48
    
    def validate_generated_files(self):
        """Valida se todos os arquivos foram gerados corretamente"""
        output_dir = 'output'
        if not os.path.exists(output_dir):
            print("❌ Pasta output não encontrada")
            return False
        
        expected_files = 48
        generated_files = len([f for f in os.listdir(output_dir) if f.endswith('.docx')])
        
        if generated_files == expected_files:
            print(f"✅ Validação: {generated_files} arquivos gerados com sucesso!")
            return True
        else:
            print(f"⚠️ Aviso: Esperados {expected_files}, encontrados {generated_files}")
            return False
    
    def show_statistics(self):
        """Mostra estatísticas dos dados personalizados"""
        total_custom = len(self.custom_data)
        total_auto = 48 - total_custom
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   Total de shifts: 48")
        print(f"   📝 Personalizados: {total_custom}")
        print(f"   🎲 Automáticos: {total_auto}")
        print(f"   📍 Estabelecimento: {self.config['establishment']}")
        print(f"   📅 Data inicial: {self.config['start_date']}")
        print(f"   ⏱️ Período: 24 dias")
        
        if total_custom > 0:
            custom_shifts = sorted(self.custom_data.keys())
            print(f"   📝 Shifts personalizados: {custom_shifts}")

def main():
    """Função principal"""
    print("🍳 GERADOR CUSTOMIZADO DE LOGBOOK")
    print("=" * 60)
    print("SIT40521 Certificate IV in Kitchen Management")
    print("Combina dados personalizados + automáticos")
    print("=" * 60)
    
    try:
        # Verificar dependências
        try:
            from docxtpl import DocxTemplate
        except ImportError:
            print("❌ Erro: Biblioteca 'python-docx-template' não encontrada!")
            print("   Instale com: pip install python-docx-template")
            sys.exit(1)
        
        # Criar instância do gerador
        generator = CustomLogbookGenerator()
        
        # Mostrar estatísticas
        generator.show_statistics()
        
        # Confirmar geração
        print("\n🤔 Deseja gerar os 48 documentos? (s/n): ", end="")
        try:
            response = input().lower().strip()
        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada pelo usuário")
            sys.exit(0)
        
        if response in ['s', 'sim', 'y', 'yes']:
            # Gerar documentos
            if generator.generate_documents():
                generator.validate_generated_files()
            else:
                print("❌ Falha na geração dos documentos")
                sys.exit(1)
        else:
            print("👋 Operação cancelada")
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
