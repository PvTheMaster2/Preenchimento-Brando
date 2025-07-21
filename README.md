# Preenchimento-Brando

Ferramentas em Python para gerar automaticamente documentos do logbook do curso **SIT40521 Certificate IV in Kitchen Management**.

Os scripts utilizam modelos `.docx` e pools de conteúdo para criar 48 registros de turnos (shifts) prontos para impressão. Também é possível importar dados de um CSV ou personalizar manualmente algumas informações.

## Pré-requisitos

- Python 3.8+
- Instalar dependências:
  ```bash
  pip install python-docx-template pandas
  ```

## Arquivos necessários

Antes de executar os scripts prepare os seguintes arquivos na pasta do projeto:

| Arquivo | Descrição |
| ------- | --------- |
| `logbook_template.docx` | Modelo do logbook com placeholders para o `docxtpl` (ex.: `{{shift_number}}`, `{{date}}` etc.). |
| `config.json` | Configurações gerais (estabelecimento, datas e horários). Veja exemplo abaixo. |
| `content_pools.json` | Textos automáticos usados nos campos (pedidos especiais, detalhes de comida etc.). |
| `shifts_data_custom.json` | (Opcional) Dados personalizados coletados pelo `input_collector.py`. |
| `seu_arquivo.csv` | (Opcional) Planilha CSV com informações dos shifts para usar no `csv_processor.py`. |
| `receitas.docx` | Documento de receitas utilizado pelas versões avançadas do gerador. |

### Exemplo de `config.json`
```json
{
  "start_date": "2024-01-01",
  "establishment": "Fatcow on James Street",
  "menu_style": "à la carte",
  "shifts": {
    "lunch": {"start_time": "10:30", "end_time": "15:30", "hours": 5},
    "dinner": {"start_time": "17:00", "end_time": "22:00", "hours": 5}
  },
  "student_name": "Seu Nome",
  "supervisor": "Nome do Supervisor",
  "course": "SIT40521 Certificate IV in Kitchen Management",
  "template_path": "template_logbook.docx"
}
```

O arquivo `content_pools.json` deve conter listas de textos para as chaves `prepared_service`, `special_requests`, `food_details`, `complaints`, `debrief` e tabelas de `workflow_lunch` e `workflow_dinner`.

## Uso dos scripts

### 1. `generator.py`
Gera automaticamente 48 documentos usando apenas dados do `config.json` e `content_pools.json`.

```bash
python generator.py
```
Os arquivos serão salvos na pasta `output/`.

### 2. `generator_custom.py`
Combina dados automáticos com informações personalizadas do arquivo `shifts_data_custom.json` (criado pelo `input_collector.py`).

```bash
python generator_custom.py
```

### 3. `csv_processor.py`
Processa um CSV com dados dos shifts, preenche campos vazios usando os pools e gera um documento `.docx` para cada linha.

```bash
python csv_processor.py --csv seu_arquivo.csv --output documentos
```

### Scripts auxiliares
- `input_collector.py` – permite criar `shifts_data_custom.json` interativamente ou gerar uma planilha modelo para preenchimento manual.
- `csv_processor_completo.py` – versão estendida do processador de CSV para planilhas com campos adicionais.

## Preparando o template DOCX

Crie um arquivo `logbook_template.docx` com todos os campos necessários. Os nomes dos placeholders devem corresponder às chaves usadas nos scripts (por exemplo `{{shift_number}}`, `{{date}}`, `{{food_details}}`).

## Preparando o CSV

O `csv_processor.py` espera um arquivo com colunas semelhantes a:

```
shift_number,date,shift_type,start_time,end_time,food_details,special_requests,complaints_problems,solutions_implemented,debrief_learnings
```

## Preparando o documento de receitas

O arquivo `receitas.docx` deve listar as receitas organizadas por categoria (proteínas, molhos, acompanhamentos). Ele é utilizado por versões futuras do gerador para evitar repetições.

---

Com todos os arquivos preparados, execute o script desejado para gerar seu logbook completo!
