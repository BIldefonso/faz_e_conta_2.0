# Mensalidades
def calcular_rendimento_anual_bruto(responsaveis=None):
    from .models import ResponsavelEducativo
    from django.db.models import Sum
    try:
        if responsaveis is None:
            return 0
        if isinstance(responsaveis, ResponsavelEducativo):
            responsaveis = [responsaveis]
        total_rendimento = ResponsavelEducativo.objects.filter(pk__in=[r.pk for r in responsaveis]).aggregate(total=Sum('salario')*12)['total'] or 0
        return total_rendimento
    except Exception as e:
        print(f"Erro ao calcular rendimento anual bruto: {e}")
        return 0
    
def calcular_despesas_anuais_fixas(responsaveis=None):
    from .models import AlunoFinancas
    if not responsaveis:
        return 0
    aluno = responsaveis.first().aluno_id
    financas = AlunoFinancas.objects.filter(aluno_id=aluno).first()
    return financas.despesa_anual if financas and hasattr(financas, 'despesa_anual') else 0

def calcular_despesas_mensais_fixas(responsaveis=None):
    from .models import AlunoFinancas
    if not responsaveis:
        return 0
    aluno = responsaveis.first().aluno_id
    
    financas = AlunoFinancas.objects.filter(aluno_id=aluno).first()
    return financas.renda if financas and hasattr(financas, 'despesa_anual') else 0

def obter_rendimento_anual_bruto(responsaveis=None):
    from .models import AlunoFinancas
    if not responsaveis:
        return 0
    aluno = responsaveis.first().aluno_id
    
    financas = AlunoFinancas.objects.filter(aluno_id=aluno).first()
    return financas.rendim_líquido if financas and hasattr(financas, 'despesa_anual') else 0

def calcular_rendimento_medio_mensal_agregado(responsaveis=None):
    # rendimento = (calcular_rendimento_anual_bruto(responsaveis)/12 - calcular_despesas_anuais_fixas(responsaveis)/12 - calcular_despesas_mensais_fixas(responsaveis))/responsaveis.count() if responsaveis else 0
    # if rendimento < 0:
    rendimento = (obter_rendimento_anual_bruto(responsaveis)/12 - calcular_despesas_anuais_fixas(responsaveis)/12 - calcular_despesas_mensais_fixas(responsaveis))/responsaveis.count() if responsaveis else 0
    
    return rendimento

def calcular_desconto_mensalidade(aluno_id=None):
    from .models import Aluno, EscalaoRendimento
    aluno = Aluno.objects.get(pk=aluno_id)
    escalao = aluno.escalao
    if escalao is None:
        escaloes = EscalaoRendimento.objects.all()
        ultimo = None
        for escalao in escaloes:
            ultimo = escalao
        return ultimo.percentagem_mensalidade/100
    return escalao.percentagem_mensalidade/100
    
def calcular_mensalidade_aluno(id_aluno):
    from .models import Aluno, ResponsavelEducativo
    try:
        aluno = Aluno.objects.get(pk=id_aluno)
        responsaveis = ResponsavelEducativo.objects.filter(aluno_id=aluno.pk)
        mensalidade = float(calcular_rendimento_medio_mensal_agregado(responsaveis=responsaveis)) * float(calcular_desconto_mensalidade(aluno_id=aluno.pk))
        return round(mensalidade, 2)
    except Aluno.DoesNotExist:
        print(f"Aluno com ID {id_aluno} não encontrado.")
        return 0
    except ResponsavelEducativo.DoesNotExist:
        print(f"Responsável educativo para o aluno com ID {id_aluno} não encontrado.")
        return 0
    except Exception as e:
        print(f"Erro ao calcular mensalidade do aluno: {e}")
        return 0

def atribuir_escalao_aluno(rendimento_per_capita=None, rmmg=None, aluno_id=None):
    from .models import Aluno, EscalaoRendimento, ResponsavelEducativo, salario_minimo
    if aluno_id is None:
        return None

    responsaveis = ResponsavelEducativo.objects.filter(aluno_id=aluno_id)
    if rendimento_per_capita is None:
        rendimento_per_capita = calcular_rendimento_medio_mensal_agregado(responsaveis=responsaveis)
    
    if rmmg is None:
        rmmg = salario_minimo

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
        escalaoes = EscalaoRendimento.objects.all()
        escalao_associar = None

        for escalao in escalaoes:
            rmmg_min = float(escalao.rmmg_min) if escalao.rmmg_min is not None else None
            rmmg_max = float(escalao.rmmg_max) if escalao.rmmg_max is not None else None
            rendimento = float(rendimento_per_capita)
            rmmg_float = float(rmmg)

            if rmmg_min is not None and rmmg_max is not None:
                if rmmg_min * rmmg_float <= rendimento <= rmmg_max * rmmg_float:
                    escalao_associar = escalao
                    break
            elif rmmg_min is not None and rmmg_max is None:
                if rendimento >= rmmg_min * rmmg_float:
                    escalao_associar = escalao
                    break
            elif rmmg_max is not None and rmmg_min is None:
                if rendimento <= rmmg_max * rmmg_float:
                    escalao_associar = escalao
                    break
            
        if escalao_associar:
            aluno.escalao = escalao
            aluno.save()
            return escalao
        else:
            print("Nenhum escalão encontrado para o rendimento informado.")
            return None
    except Aluno.DoesNotExist:
        print(f"Aluno com ID {aluno_id} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao atribuir escalão ao aluno: {e}")
        return None

# Calculos
def calcular_despesas():
    from .models import DespesaFixa, DespesasVariavel
    from django.db.models import Sum
    try:
        despesas_fixas = DespesaFixa.objects.all()
        despesas_variaveis = DespesasVariavel.objects.all()
        
        total_fixas = despesas_fixas.aggregate(total=Sum('valor'))['total'] or 0
        total_variaveis = despesas_variaveis.aggregate(total=Sum('valor'))['total'] or 0

        return total_fixas + total_variaveis
    except Exception as e:
        print(f"Erro ao calcular despesas fixas e variáveis: {e}")
        return 0

def calcular_pagamento_mensal_alunos(mes=None):
    from .models import Aluno, pagamento
    from django.db.models import Sum

    try:
        if mes is None:
            pagamentos = pagamento.objects.filter(tipo_pagamento_id__tipo_pagamento="pagamento")
        else:
            pagamentos = pagamento.objects.filter(
            data_transacao__month=mes,
            tipo_pagamento_id__tipo_pagamento="pagamento"
            )
        alunos = Aluno.objects.all()
        
        total_pagamentos = pagamentos.aggregate(total=Sum('valor'))['total'] or 0
        total_alunos = alunos.count()
        
        if total_alunos == 0:
            return 0
        
        return total_pagamentos / total_alunos
    except Exception as e:
        print(f"Erro ao calcular pagamento mensal dos alunos: {e}")
        return 0

def calcular_pagamentos_falta_alunos(mes=None, ano=None):
    from .models import Aluno, Transacao
    from django.db.models import Sum
    from collections import defaultdict
    from django.db.models import Q
    
    alunos_saldo = set()
    
    if mes is None or ano is None:
        pagamentos = Transacao.objects.all()
    else:
        pagamentos = Transacao.objects.filter(
            (Q(data_transacao__year=ano) & Q(data_transacao__month__lte=mes)) |
            Q(data_transacao__year__lt=ano)
        )
    
    # Calcula o saldo de cada aluno a partir dos pagamentos
    alunos_saldo = defaultdict(float)
    for pagamento in pagamentos:
        alunos_saldo[pagamento.aluno_id_id] += pagamento.valor
    
    saldos = 0
    for aluno in alunos_saldo:
        if alunos_saldo[aluno] < 0:
            saldos -= abs(alunos_saldo[aluno])
    
    return saldos
            

# Transações
def get_tipo_transacao_default(valor):
    from .models import TipoTransacao
    if valor > 0:
        return TipoTransacao.objects.get(tipo_transacao="Carregamento")
    else:
        return TipoTransacao.objects.get(tipo_transacao="Pagamento")
    
def pagamento(id_aluno, valor, descricao=None, tipo_transacao=None, data_transacao=None):
    from .models import Aluno, Transacao, TipoTransacao
    from django.utils import timezone

    try:
        aluno = Aluno.objects.get(pk=id_aluno)
        
        print(f"{tipo_transacao}")

        # Determinar o tipo de transação
        tipo_pagamento = None
        if tipo_transacao is not None:
            if isinstance(tipo_transacao, TipoTransacao):
                tipo_pagamento = tipo_transacao
            else:
                tipo_pagamento = TipoTransacao.objects.get(pk=tipo_transacao) if isinstance(tipo_transacao, int) else TipoTransacao.objects.get(tipo_transacao=tipo_transacao)
        else:
            tipo_pagamento = TipoTransacao.objects.get(tipo_transacao="Carregamento") if valor > 0 else TipoTransacao.objects.get(tipo_transacao="Pagamento")

        # Ajustar saldo do aluno (exceto para Comparticipação)
        if tipo_pagamento.tipo_transacao != "Comparticipação":
            aluno.saldo += valor

        # Definir descrição se não fornecida
        if descricao is None:
            if tipo_pagamento.tipo_transacao == "Comparticipação":
                descricao = "Comparticipação da Segurança Social"
            elif valor > 0:
                descricao = "Carregamento"
            else:
                descricao = "Pagamento"

        # Definir data da transação
        if data_transacao is not None:
            if isinstance(data_transacao, str):
                data_transacao = timezone.datetime.strptime(data_transacao, "%Y-%m-%d %H:%M:%S")
        else:
            data_transacao = timezone.now()

        Transacao.objects.create(
            aluno_id=aluno,
            valor=valor,
            data_transacao=data_transacao,
            descricao=descricao,
            tipo_transacao=tipo_pagamento,
        )
        aluno.save()
    except Exception as e:
        print(f"Erro ao registrar pagamento: {e}")

def verificar_pagamentos():
    from .models import Aluno, Transacao as pagamento
    try:
        pagamentos = pagamento.objects.filter(data_transacao__isnull=True)
        alunos = Aluno.objects.filter()
        valores_alunos = set()
        
        alunos_saldo_invalido = set()
        
        for pagamento in pagamentos:
            if pagamento.aluno_id and pagamento.valor:
                valores_alunos.add((pagamento.aluno_id.pk, pagamento.valor))
        
        for aluno in alunos:
            if valores_alunos[aluno.pk] == aluno.saldo:
                continue
            else:
                alunos_saldo_invalido[aluno.pk] = aluno.saldo-valores_alunos[aluno.pk]
                     
    except Exception as e:
        print(f"Erro ao verificar pagamentos: {e}")
    
    return alunos_saldo_invalido

# Other
def get_sala_id(aluno_id):
    from .models import Sala
    for sala in Sala.objects.all():
        if sala.alunos.filter(pk=aluno_id).exists():
            return sala.pk

# Backup
def create_backup():
    import os
    import shutil
    from datetime import datetime
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'db.sqlite3')
    backup_dir = os.path.join(base_dir, 'backup')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    now = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_filename = f"db_{now}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_filename)
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Backup criado em: {backup_path}")
    except Exception as e:
        print(f"Erro ao criar backup: {e}")

def restore_backup(backup_filename=None):
    import os
    import shutil
    from datetime import datetime
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'db.sqlite3')
    backup_dir = os.path.join(base_dir, 'backup')
    if not os.path.exists(backup_dir):
        print("Diretório de backup não encontrado.")
        return
    if backup_filename is None:
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('db_') and f.endswith('.sqlite3')]
        if not backup_files:
            print("Nenhum arquivo de backup encontrado.")
            return
        backup_filename = sorted(backup_files)[-1]  # Pega o mais recente
    backup_path = os.path.join(backup_dir, backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"Arquivo de backup {backup_filename} não encontrado.")
        return
    try:
        shutil.copy2(backup_path, db_path)
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        print(f"Backup restaurado de: {backup_path}")
    except Exception as e:
        print(f"Erro ao restaurar backup: {e}")

def listar_backups():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_dir = os.path.join(base_dir, 'backup')
    if not os.path.exists(backup_dir):
        print("Diretório de backup não encontrado.")
        return []
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith('db_') and f.endswith('.sqlite3')]
    if not backup_files:
        print("Nenhum arquivo de backup encontrado.")
        return []
    backup_files.sort(reverse=True)  # Ordena do mais recente para o mais antigo
    return [os.path.join(f) for f in backup_files]
