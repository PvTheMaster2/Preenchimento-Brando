#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Collector - Sistema de Coleta de Dados para Logbook
Permite ao usuário inserir informações específicas de cada shift

Uso: python input_collector.py
"""

import json
import os
from datetime import datetime, timedelta

class ShiftInputCollector:
    def __init__(self):
        """Inicializa o coletor de dados"""
        print("📝 COLETOR DE DADOS DO LOGBOOK")
        print("=" * 50)
        self.config = self.load_json('config.json')
        self.content_pools = self.load_json('content_pools.json')
        self.shifts_data = []
        
    def load_json(self, filename):
        """Carrega arquivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo {filename} não encontrado!")
            exit(1)
    
    def show_menu(self):
        """Mostra menu principal"""
        print("\n🍳 OPÇÕES DE PREENCHIMENTO:")
        print("1. 📝 Preencher shift por shift (detalhado)")
        print("2. 📊 Preencher planilha Excel (rápido)")
        print("3. 🎲 Usar dados automáticos dos pools")
        print("4. 🔄 Híbrido (alguns manuais + alguns automáticos)")
        print("5. 📄 Importar dados de arquivo")
        print("0. ❌ Sair")
        
        return input("\n👉 Escolha uma opção (0-5): ").strip()
    
    def collect_shift_data_interactive(self):
        """Coleta dados shift por shift de forma interativa"""
        print("\n📝 COLETA INTERATIVA DE DADOS")
        print("Para cada shift, você pode:")
        print("- ✍️ Inserir dados específicos")
        print("- 🎲 Usar opção dos pools automáticos")
        print("- ⏭️ Pular (vai usar pool automático)")
        
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        
        for i in range(48):
            shift_date = start_date + timedelta(days=i//2)
            shift_type = 'lunch' if i % 2 == 0 else 'dinner'
            
            print(f"\n" + "="*60)
            print(f"🍽️ SHIFT {i+1}/48 - {shift_type.upper()} - {shift_date.strftime('%d/%m/%Y')}")
            print("="*60)
            
            # Dados básicos (fixos)
            shift_data = {
                'shift_number': i + 1,
                'date': shift_date.strftime('%d/%m/%Y'),
                'shift_type': shift_type,
                'establishment': self.config['establishment'],
                'start_time': self.config['shifts'][shift_type]['start_time'],
                'end_time': self.config['shifts'][shift_type]['end_time'],
                'hours': self.config['shifts'][shift_type]['hours'],
                'menu_style': self.config['menu_style']
            }
            
            # Coleta dados variáveis
            shift_data.update(self.collect_variable_data(shift_type, i+1))
            
            self.shifts_data.append(shift_data)
            
            # Perguntar se quer continuar
            if i < 47:  # Não perguntar no último shift
                continue_choice = input("\n➡️ Continuar para próximo shift? (s/n/q=quit): ").lower()
                if continue_choice == 'q':
                    print("💾 Salvando dados coletados até agora...")
                    break
                elif continue_choice == 'n':
                    print("⏸️ Pausando coleta. Dados salvos.")
                    break
    
    def collect_variable_data(self, shift_type, shift_num):
        """Coleta dados variáveis de um shift específico"""
        data = {}
        
        # 1. Prepared for service (geralmente fixo, mas pode personalizar)
        print(f"\n1️⃣ PREPARED FOR SERVICE ({shift_type}):")
        print("Padrão:", self.content_pools['prepared_service'][shift_type][:100] + "...")
        custom_prep = input("✏️ Personalizar? (Enter=usar padrão, ou digite novo): ").strip()
        data['prepared_service'] = custom_prep if custom_prep else self.content_pools['prepared_service'][shift_type]
        
        # 2. Special requests
        print(f"\n2️⃣ SPECIAL REQUESTS:")
        data['special_requests'] = self.get_user_choice_or_custom(
            'special_requests',
            "Que pedidos especiais você atendeu?"
        )
        
        # 3. Food details (mais importante - o que realmente preparou)
        print(f"\n3️⃣ FOOD DETAILS (IMPORTANTE!):")
        print("🍽️ O que você realmente preparou/cozinhou neste shift?")
        data['food_details'] = self.get_user_choice_or_custom(
            'food_details',
            "Descreva o que preparou/cozinhou/serviu:",
            allow_long_text=True
        )
        
        # 4. Complaints
        print(f"\n4️⃣ COMPLAINTS/ISSUES:")
        data['complaints'] = self.get_user_choice_or_custom(
            'complaints',
            "Houve alguma reclamação/problema?"
        )
        
        # 5. Debrief
        print(f"\n5️⃣ DEBRIEF/OBSERVAÇÕES:")
        data['debrief'] = self.get_user_choice_or_custom(
            'debrief',
            "Observações finais do shift:"
        )
        
        return data
    
    def get_user_choice_or_custom(self, pool_key, question, allow_long_text=False):
        """Permite escolher entre pool ou inserir customizado"""
        print(f"\n📋 Opções disponíveis para {pool_key}:")
        options = self.content_pools[pool_key]
        
        # Mostrar opções numeradas
        for i, option in enumerate(options[:5], 1):  # Mostrar até 5 opções
            preview = option[:80] + "..." if len(option) > 80 else option
            print(f"   {i}. {preview}")
        
        if len(options) > 5:
            print(f"   ... e mais {len(options)-5} opções")
        
        print(f"\n{question}")
        print("Opções:")
        print("• Digite 1-5 para usar uma opção acima")
        print("• Digite 'c' para texto customizado")
        print("• Digite 'r' para ver todas as opções")
        print("• Enter para usar aleatório do pool")
        
        choice = input("👉 Sua escolha: ").strip().lower()
        
        if choice == 'c':
            print("\n✏️ Digite seu texto customizado:")
            if allow_long_text:
                print("(Digite 'END' em uma linha separada para finalizar)")
                lines = []
                while True:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    lines.append(line)
                return '\n'.join(lines)
            else:
                return input("📝 Texto: ")
        
        elif choice == 'r':
            print("\n📜 TODAS AS OPÇÕES:")
            for i, option in enumerate(options, 1):
                print(f"{i:2d}. {option}")
            choice = input(f"👉 Escolha 1-{len(options)} ou 'c' para customizado: ").strip()
        
        # Tentar converter para número
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        
        # Usar aleatório se escolha inválida
        import random
        return random.choice(options)
    
    def create_excel_template(self):
        """Cria planilha Excel para preenchimento"""
        try:
            import pandas as pd
            
            print("\n📊 CRIANDO PLANILHA EXCEL...")
            
            # Gerar estrutura básica
            start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
            rows = []
            
            for i in range(48):
                shift_date = start_date + timedelta(days=i//2)
                shift_type = 'lunch' if i % 2 == 0 else 'dinner'
                
                rows.append({
                    'shift_number': i + 1,
                    'date': shift_date.strftime('%d/%m/%Y'),
                    'shift_type': shift_type,
                    'start_time': self.config['shifts'][shift_type]['start_time'],
                    'end_time': self.config['shifts'][shift_type]['end_time'],
                    'special_requests': '',  # Para preencher
                    'food_details': '',      # Para preencher
                    'complaints': '',        # Para preencher
                    'debrief': ''           # Para preencher
                })
            
            df = pd.DataFrame(rows)
            filename = 'logbook_input_template.xlsx'
            df.to_excel(filename, index=False)
            
            print(f"✅ Planilha criada: {filename}")
            print("📝 Instruções:")
            print("1. Abra a planilha no Excel")
            print("2. Preencha as colunas vazias com seus dados")
            print("3. Salve o arquivo")
            print("4. Execute: python input_collector.py (opção 5)")
            
        except ImportError:
            print("❌ pandas não encontrado. Instale com: pip install pandas openpyxl")
    
    def save_data(self):
        """Salva dados coletados"""
        filename = 'shifts_data_custom.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.shifts_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Dados salvos em: {filename}")
        print(f"📊 Total de shifts coletados: {len(self.shifts_data)}")
        
        # Instruções para usar os dados
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python generator_custom.py")
        print("2. Seus dados personalizados serão usados!")
        
        return filename
    
    def load_existing_data(self):
        """Carrega dados existentes se houver"""
        filename = 'shifts_data_custom.json'
        if os.path.exists(filename):
            choice = input(f"📁 Encontrado arquivo {filename}. Carregar? (s/n): ")
            if choice.lower() == 's':
                with open(filename, 'r', encoding='utf-8') as f:
                    self.shifts_data = json.load(f)
                print(f"📊 Carregados {len(self.shifts_data)} shifts existentes")
                return True
        return False
    
    def run(self):
        """Executa o coletor principal"""
        # Tentar carregar dados existentes
        self.load_existing_data()
        
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                self.collect_shift_data_interactive()
                self.save_data()
                break
            
            elif choice == '2':
                self.create_excel_template()
                break
            
            elif choice == '3':
                print("🎲 Usando dados automáticos dos pools")
                print("Execute diretamente: python generator.py")
                break
            
            elif choice == '4':
                print("🔄 Modo híbrido - colete alguns dados importantes")
                # Implementar lógica híbrida
                self.collect_key_shifts_only()
                self.save_data()
                break
            
            elif choice == '5':
                self.import_from_file()
                break
            
            elif choice == '0':
                print("👋 Saindo...")
                break
            
            else:
                print("❌ Opção inválida!")
    
    def collect_key_shifts_only(self):
        """Coleta apenas alguns shifts importantes (híbrido)"""
        print("\n🔄 MODO HÍBRIDO")
        print("Vamos coletar dados apenas para shifts específicos")
        print("Os outros usarão dados automáticos dos pools")
        
        # Perguntar quais shifts personalizar
        important_shifts = input("📝 Quais shifts personalizar? (ex: 1,5,10,15 ou Enter=aleatórios): ").strip()
        
        if important_shifts:
            try:
                shift_numbers = [int(x.strip()) for x in important_shifts.split(',')]
            except:
                print("❌ Formato inválido, usando shifts aleatórios")
                import random
                shift_numbers = random.sample(range(1, 49), 10)
        else:
            import random
            shift_numbers = random.sample(range(1, 49), 10)
        
        print(f"🎯 Personalizando shifts: {sorted(shift_numbers)}")
        
        # Coletar apenas esses shifts
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        
        for shift_num in sorted(shift_numbers):
            i = shift_num - 1
            shift_date = start_date + timedelta(days=i//2)
            shift_type = 'lunch' if i % 2 == 0 else 'dinner'
            
            print(f"\n📝 PERSONALIZANDO SHIFT {shift_num} - {shift_type.upper()}")
            
            shift_data = {
                'shift_number': shift_num,
                'date': shift_date.strftime('%d/%m/%Y'),
                'shift_type': shift_type,
                'custom': True  # Marcar como customizado
            }
            
            # Coletar apenas food_details (mais importante)
            print("🍽️ O que você preparou/cozinhou neste shift?")
            shift_data['food_details'] = input("📝 Descreva: ").strip()
            
            self.shifts_data.append(shift_data)
    
    def import_from_file(self):
        """Importa dados de arquivo Excel"""
        filename = input("📁 Nome do arquivo Excel: ").strip()
        if not filename:
            filename = 'logbook_input_template.xlsx'
        
        try:
            import pandas as pd
            df = pd.read_excel(filename)
            
            self.shifts_data = []
            for _, row in df.iterrows():
                shift_data = row.to_dict()
                self.shifts_data.append(shift_data)
            
            print(f"✅ Importados {len(self.shifts_data)} shifts de {filename}")
            self.save_data()
            
        except ImportError:
            print("❌ pandas não encontrado. Instale com: pip install pandas openpyxl")
        except Exception as e:
            print(f"❌ Erro ao importar: {e}")

def main():
    """Função principal"""
    collector = ShiftInputCollector()
    collector.run()

if __name__ == "__main__":
    main() 