Você deve gerar um código Python que automatize o preenchimento de um documento Word `.docx` chamado `C4KM_Logbook_modelo.docx`.

Esse documento contém placeholders como `{{dia1_shift}}`, `{{dia1_protein}}`, `{{dia1_sauce}}`, `{{dia1_accompaniment}}`, `{{dia1_obs}}` até o dia45.

Você deve:
1. Usar `docxtpl` para preservar a formatação original do `.docx`
2. Extrair os dados de `receitas.docx`, que estão organizados por categorias: proteínas, molhos, acompanhamentos.
3. Gerar uma rotação de turnos com base no padrão “Preparation”, “Sauce”, “Garnish” (revezando a cada 5 dias)
4. Garantir que as receitas não se repitam por pelo menos 8 dias.
5. Gerar observações padronizadas com base no turno.
6. Preencher os placeholders para os 45 dias com esses dados.
7. Salvar o resultado como `logbook_final.docx`.

Você pode se basear nesse código existente:
```python
from docxtpl import DocxTemplate
from docx import Document

def get_recipe_from_docx(path):
    # trecho que extrai as receitas...
